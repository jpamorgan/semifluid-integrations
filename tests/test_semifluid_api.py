import importlib.util
import os
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
    def test_missing_token_error_explains_codex_mcp_oauth_boundary(self):
        helper = load_helper_module()

        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as raised:
                helper.get_bearer_token()

        message = str(raised.exception)
        self.assertIn("Codex MCP OAuth does not expose plugin access tokens", message)
        self.assertIn("SEMIFLUID_ACCESS_TOKEN", message)
        self.assertIn("Semifluid MCP tools", message)


if __name__ == "__main__":
    unittest.main()
