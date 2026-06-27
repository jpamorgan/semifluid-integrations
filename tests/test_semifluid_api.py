import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "semifluid"
    / "scripts"
    / "semifluid_api.py"
)


def load_helper_module():
    spec = importlib.util.spec_from_file_location("semifluid_api", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SemifluidApiAuthTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_path = str(Path(self.temp_dir.name) / "oauth-token.json")
        self.env = {
            "SEMIFLUID_OAUTH_CACHE": self.cache_path,
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_env_token_wins_over_cache(self):
        with mock.patch.dict(
            os.environ,
            {**self.env, "SEMIFLUID_ACCESS_TOKEN": "env-token"},
            clear=True,
        ):
            self.helper.write_oauth_cache(
                {
                    "base_url": "https://api.semifluid.ai",
                    "resource": "https://api.semifluid.ai/v1",
                    "access_token": "cached-token",
                    "expires_at": int(time.time() + 3600),
                }
            )

            self.assertEqual(self.helper.get_oauth_token("https://api.semifluid.ai"), "env-token")

    def test_valid_cached_token_is_used_for_api_calls(self):
        with mock.patch.dict(os.environ, self.env, clear=True):
            self.helper.write_oauth_cache(
                {
                    "base_url": "https://api.semifluid.ai",
                    "resource": "https://api.semifluid.ai/v1",
                    "access_token": "cached-token",
                    "expires_at": int(time.time() + 3600),
                }
            )

            self.assertEqual(self.helper.get_oauth_token("https://api.semifluid.ai"), "cached-token")

    def test_expired_cached_token_refreshes(self):
        with mock.patch.dict(os.environ, self.env, clear=True):
            self.helper.write_oauth_cache(
                {
                    "base_url": "https://api.semifluid.ai",
                    "resource": "https://api.semifluid.ai/v1",
                    "issuer": "https://api.semifluid.ai/api/auth",
                    "token_endpoint": "https://api.semifluid.ai/api/auth/oauth2/token",
                    "client_id": "client-1",
                    "access_token": "expired-token",
                    "refresh_token": "refresh-token",
                    "expires_at": int(time.time() - 60),
                }
            )

            with mock.patch.object(
                self.helper,
                "form_request",
                return_value={
                    "access_token": "fresh-token",
                    "refresh_token": "next-refresh-token",
                    "expires_in": 3600,
                },
            ) as form_request:
                self.assertEqual(self.helper.get_oauth_token("https://api.semifluid.ai"), "fresh-token")

            form_request.assert_called_once_with(
                "https://api.semifluid.ai/api/auth/oauth2/token",
                {
                    "grant_type": "refresh_token",
                    "refresh_token": "refresh-token",
                    "client_id": "client-1",
                    "resource": "https://api.semifluid.ai/v1",
                },
            )
            cached = json.loads(Path(self.cache_path).read_text())
            self.assertEqual(cached["access_token"], "fresh-token")
            self.assertEqual(cached["refresh_token"], "next-refresh-token")

    def test_missing_token_points_to_oauth_login(self):
        with mock.patch.dict(os.environ, self.env, clear=True):
            with self.assertRaises(SystemExit) as raised:
                self.helper.get_oauth_token("https://api.semifluid.ai")

        message = str(raised.exception)
        self.assertIn("auth login", message)
        self.assertIn("SEMIFLUID_ACCESS_TOKEN", message)
        self.assertNotIn("retry in a new thread", message)


if __name__ == "__main__":
    unittest.main()
