#!/usr/bin/env python3
"""Small Semifluid API helper for Codex skills."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import http.server
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://api.semifluid.ai"
TRACE_ENV = "SEMIFLUID_API_TRACE"
TOKEN_CACHE_ENV = "SEMIFLUID_OAUTH_CACHE"
DEFAULT_OAUTH_SCOPE = " ".join(
    (
        "openid",
        "email",
        "profile",
        "collections:read",
        "collections:write",
        "fields:write",
        "views:write",
        "records:read",
        "records:write",
        "attachments:read",
        "attachments:write",
        "events:read",
        "webhooks:manage",
        "offline_access",
    )
)
OAUTH_TOKEN_ENV_VARS = (
    "SEMIFLUID_ACCESS_TOKEN",
    "SEMIFLUID_OAUTH_TOKEN",
    "CODEX_SEMIFLUID_ACCESS_TOKEN",
)


class ApiError(Exception):
    def __init__(self, status: int, body: bytes, headers: Any):
        self.status = status
        self.body = body
        self.headers = headers
        super().__init__(f"HTTP {status}")


def token_from_env(names: tuple[str, ...]) -> str | None:
    for name in names:
        token = os.environ.get(name)
        if token:
            return token
    return None


def get_oauth_token(base_url: str) -> str:
    token = token_from_env(OAUTH_TOKEN_ENV_VARS)
    if token:
        return token

    cached_token = get_cached_oauth_token(base_url)
    if cached_token:
        return cached_token

    names = ", ".join(OAUTH_TOKEN_ENV_VARS)
    raise SystemExit(
        "Missing Semifluid OAuth token. Run `python3 scripts/semifluid_api.py auth login` "
        "to authorize this helper, or provide a bearer token through one of: "
        f"{names}."
    )


def get_api_key() -> str:
    key = os.environ.get("SEMIFLUID_API_KEY")
    if not key:
        raise SystemExit(
            "Missing SEMIFLUID_API_KEY. API-key auth is only a compatibility mode; "
            "use the helper OAuth login path for normal Semifluid plugin work."
        )
    return key


def oauth_cache_path() -> Path:
    configured = os.environ.get(TOKEN_CACHE_ENV)
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex" / "semifluid" / "oauth-token.json"


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def oauth_resource(base_url: str) -> str:
    return f"{normalize_base_url(base_url)}/v1"


def auth_server_metadata_url(base_url: str) -> str:
    return f"{normalize_base_url(base_url)}/api/auth/.well-known/oauth-authorization-server"


def read_oauth_cache() -> dict[str, Any] | None:
    path = oauth_cache_path()
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def write_oauth_cache(payload: dict[str, Any]) -> None:
    path = oauth_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    try:
        os.chmod(tmp_path, 0o600)
    except OSError:
        pass
    tmp_path.replace(path)


def clear_oauth_cache() -> None:
    try:
        oauth_cache_path().unlink()
    except FileNotFoundError:
        pass


def json_request(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    headers = {"Accept": "application/json", "User-Agent": "codex-semifluid-api/1.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as response:
        parsed = json.loads(response.read())
    if not isinstance(parsed, dict):
        raise SystemExit(f"Expected JSON object from {url}")
    return parsed


def form_request(url: str, fields: dict[str, str]) -> dict[str, Any]:
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "codex-semifluid-api/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        parsed = json.loads(response.read())
    if not isinstance(parsed, dict):
        raise SystemExit(f"Expected JSON object from {url}")
    return parsed


def discover_oauth_metadata(base_url: str) -> dict[str, Any]:
    return json_request(auth_server_metadata_url(base_url))


def require_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise SystemExit(f"OAuth response is missing `{key}`.")
    return value


def token_payload_from_response(
    token_response: dict[str, Any],
    *,
    base_url: str,
    metadata: dict[str, Any],
    client_id: str,
    refresh_token: str | None = None,
) -> dict[str, Any]:
    access_token = require_string(token_response, "access_token")
    next_refresh_token = token_response.get("refresh_token")
    expires_in = token_response.get("expires_in")
    expires_at = None
    if isinstance(expires_in, str):
        try:
            expires_in = float(expires_in)
        except ValueError:
            expires_in = None
    if isinstance(expires_in, int | float):
        expires_at = int(time.time() + max(0, float(expires_in) - 60))

    return {
        "base_url": normalize_base_url(base_url),
        "resource": oauth_resource(base_url),
        "issuer": metadata.get("issuer"),
        "token_endpoint": metadata.get("token_endpoint"),
        "client_id": client_id,
        "access_token": access_token,
        "refresh_token": next_refresh_token if isinstance(next_refresh_token, str) else refresh_token,
        "expires_at": expires_at,
        "scope": token_response.get("scope"),
        "token_type": token_response.get("token_type"),
    }


def cached_token_is_current(cache: dict[str, Any], base_url: str) -> bool:
    return (
        cache.get("base_url") == normalize_base_url(base_url)
        and cache.get("resource") == oauth_resource(base_url)
        and isinstance(cache.get("access_token"), str)
        and isinstance(cache.get("expires_at"), int | float)
        and float(cache["expires_at"]) > time.time()
    )


def refresh_oauth_token(cache: dict[str, Any], base_url: str) -> str | None:
    refresh_token = cache.get("refresh_token")
    token_endpoint = cache.get("token_endpoint")
    client_id = cache.get("client_id")
    if not all(isinstance(value, str) and value for value in (refresh_token, token_endpoint, client_id)):
        return None

    try:
        token_response = form_request(
            token_endpoint,
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "resource": oauth_resource(base_url),
            },
        )
    except Exception:
        return None

    metadata = {"issuer": cache.get("issuer"), "token_endpoint": token_endpoint}
    updated = token_payload_from_response(
        token_response,
        base_url=base_url,
        metadata=metadata,
        client_id=client_id,
        refresh_token=refresh_token,
    )
    write_oauth_cache(updated)
    return updated["access_token"]


def get_cached_oauth_token(base_url: str) -> str | None:
    cache = read_oauth_cache()
    if not cache:
        return None
    if cached_token_is_current(cache, base_url):
        return str(cache["access_token"])
    return refresh_oauth_token(cache, base_url)


def pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    server: "OAuthCallbackServer"

    def do_GET(self) -> None:
        url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(url.query)
        self.server.auth_code = query.get("code", [None])[0]
        self.server.auth_state = query.get("state", [None])[0]
        self.server.auth_error = query.get("error", [None])[0]
        message = "Semifluid authorization complete. You can return to Codex."
        if self.server.auth_error:
            message = f"Semifluid authorization failed: {self.server.auth_error}"
        body = message.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


class OAuthCallbackServer(http.server.HTTPServer):
    auth_code: str | None = None
    auth_state: str | None = None
    auth_error: str | None = None


def create_callback_server() -> OAuthCallbackServer:
    return OAuthCallbackServer(("127.0.0.1", 0), OAuthCallbackHandler)


def register_oauth_client(metadata: dict[str, Any], redirect_uri: str) -> str:
    registration_endpoint = require_string(metadata, "registration_endpoint")
    response = json_request(
        registration_endpoint,
        method="POST",
        payload={
            "client_name": "Semifluid Codex Plugin",
            "redirect_uris": [redirect_uri],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
            "scope": DEFAULT_OAUTH_SCOPE,
        },
    )
    return require_string(response, "client_id")


def exchange_authorization_code(
    metadata: dict[str, Any],
    *,
    code: str,
    client_id: str,
    redirect_uri: str,
    code_verifier: str,
    base_url: str,
) -> dict[str, Any]:
    return form_request(
        require_string(metadata, "token_endpoint"),
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
            "resource": oauth_resource(base_url),
        },
    )


def run_oauth_login(args: argparse.Namespace) -> int:
    metadata = discover_oauth_metadata(args.base_url)
    callback_server = create_callback_server()
    host, port = callback_server.server_address[:2]
    redirect_uri = f"http://{host}:{port}/callback"
    client_id = register_oauth_client(metadata, redirect_uri)
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    authorization_url = require_string(metadata, "authorization_endpoint")
    auth_url = f"{authorization_url}?{urllib.parse.urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': args.scope,
        'state': state,
        'code_challenge': pkce_challenge(code_verifier),
        'code_challenge_method': 'S256',
        'resource': oauth_resource(args.base_url),
    })}"

    print("Open this URL to authorize Semifluid API access:")
    print(auth_url)
    if not args.no_browser:
        webbrowser.open(auth_url)

    callback_server.timeout = args.timeout
    callback_server.handle_request()
    callback_server.server_close()

    if callback_server.auth_error:
        raise SystemExit(f"OAuth authorization failed: {callback_server.auth_error}")
    if not callback_server.auth_code:
        raise SystemExit("OAuth authorization timed out before receiving a code.")
    if callback_server.auth_state != state:
        raise SystemExit("OAuth authorization returned an invalid state.")

    token_response = exchange_authorization_code(
        metadata,
        code=callback_server.auth_code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
        base_url=args.base_url,
    )
    cache = token_payload_from_response(
        token_response,
        base_url=args.base_url,
        metadata=metadata,
        client_id=client_id,
    )
    write_oauth_cache(cache)
    print(f"Authorized Semifluid API access and cached credentials at {oauth_cache_path()}.")
    return 0


def run_oauth_status(args: argparse.Namespace) -> int:
    token = token_from_env(OAUTH_TOKEN_ENV_VARS)
    if token:
        print("Semifluid OAuth token is available from the environment.")
        return 0
    cached = get_cached_oauth_token(args.base_url)
    if cached:
        print(f"Semifluid OAuth token is available from cache at {oauth_cache_path()}.")
        return 0
    print("No Semifluid OAuth token is available. Run `python3 scripts/semifluid_api.py auth login`.")
    return 1


def run_oauth_logout(_args: argparse.Namespace) -> int:
    clear_oauth_cache()
    print(f"Removed Semifluid OAuth cache at {oauth_cache_path()}.")
    return 0


def load_json_arg(value: str | None) -> bytes | None:
    if value is None:
        return None
    if value.startswith("@"):
        raw = Path(value[1:]).read_text()
    else:
        raw = value
    parsed = json.loads(raw)
    return json.dumps(parsed, separators=(",", ":")).encode()


def parse_query(items: list[str] | None) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"Query item must be key=value: {item}")
        key, value = item.split("=", 1)
        pairs.append((key, value))
    return pairs


def build_url(base_url: str, path: str, query: list[tuple[str, str]]) -> str:
    base = base_url.rstrip("/") + "/"
    clean_path = path.lstrip("/")
    url = urllib.parse.urljoin(base, clean_path)
    if query:
        url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"
    return url


def emit_timing(method: str, path: str, status: int | None, elapsed_seconds: float) -> None:
    status_label = f"HTTP {status}" if status is not None else "failed"
    print(
        f"Timing: {method.upper()} {path} -> {status_label} in {elapsed_seconds * 1000:.1f} ms",
        file=sys.stderr,
    )


def write_trace_event(
    trace_output: str | None,
    *,
    method: str,
    path: str,
    base_url: str,
    query: list[tuple[str, str]],
    body: bytes | None,
    no_auth: bool,
    status: int | None,
    elapsed_seconds: float,
    error: str | None,
) -> None:
    output = trace_output or os.environ.get(TRACE_ENV)
    if not output:
        return

    event = {
        "ts": dt.datetime.now(dt.UTC).isoformat(),
        "method": method.upper(),
        "path": path,
        "base_url": base_url.rstrip("/"),
        "query_keys": [key for key, _value in query],
        "body_bytes": len(body) if body is not None else 0,
        "no_auth": no_auth,
        "status": status,
        "elapsed_ms": round(elapsed_seconds * 1000, 1),
        "ok": status is not None and 200 <= status < 400,
    }
    if error:
        event["error"] = error

    trace_path = Path(output)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def request(
    method: str,
    path: str,
    *,
    base_url: str,
    query: list[tuple[str, str]],
    body: bytes | None,
    no_auth: bool,
    auth_header: str,
    trace_output: str | None,
) -> tuple[int, bytes, Any]:
    headers = {
        "Accept": "application/json, application/octet-stream, text/event-stream, */*",
        "User-Agent": "codex-semifluid-api/1.0",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    if not no_auth:
        if auth_header == "x-api-key":
            headers["x-api-key"] = get_api_key()
        elif auth_header == "bearer":
            headers["Authorization"] = f"Bearer {get_oauth_token(base_url)}"
        else:
            raise SystemExit(f"Unsupported auth header mode: {auth_header}")

    req = urllib.request.Request(
        build_url(base_url, path, query),
        data=body,
        headers=headers,
        method=method.upper(),
    )
    start = time.perf_counter()
    status: int | None = None
    error_label: str | None = None
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            return response.status, response.read(), response.headers
    except urllib.error.HTTPError as error:
        status = error.code
        error_label = "HTTPError"
        raise ApiError(error.code, error.read(), error.headers) from error
    except Exception:
        error_label = "RequestError"
        raise
    finally:
        elapsed_seconds = time.perf_counter() - start
        emit_timing(method, path, status, elapsed_seconds)
        write_trace_event(
            trace_output,
            method=method,
            path=path,
            base_url=base_url,
            query=query,
            body=body,
            no_auth=no_auth,
            status=status,
            elapsed_seconds=elapsed_seconds,
            error=error_label,
        )


def emit_response(status: int, body: bytes, output: str | None) -> None:
    if output:
        Path(output).write_bytes(body)
        print(f"HTTP {status}; wrote {len(body)} bytes to {output}")
        return

    if not body:
        print(f"HTTP {status}")
        return

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        sys.stdout.buffer.write(body)
        if not body.endswith(b"\n"):
            print()
        return

    print(json.dumps(parsed, indent=2, sort_keys=True))


def run_request(args: argparse.Namespace) -> int:
    method = args.method.upper()
    body = load_json_arg(args.json)
    try:
        status, response_body, _headers = request(
            method,
            args.path,
            base_url=args.base_url,
            query=parse_query(args.query),
            body=body,
            no_auth=args.no_auth,
            auth_header=args.auth_header,
            trace_output=args.trace_output,
        )
        emit_response(status, response_body, args.output)
        return 0
    except ApiError as error:
        print(f"HTTP {error.status}", file=sys.stderr)
        if error.body:
            try:
                parsed = json.loads(error.body)
                print(json.dumps(parsed, indent=2, sort_keys=True), file=sys.stderr)
            except json.JSONDecodeError:
                print(error.body.decode(errors="replace"), file=sys.stderr)
        return 1


def run_health(args: argparse.Namespace) -> int:
    args.method = "GET"
    args.path = "/v1/health"
    args.query = []
    args.json = None
    args.no_auth = True
    args.output = None
    return run_request(args)


def run_spec(args: argparse.Namespace) -> int:
    args.method = "GET"
    args.path = "/api-reference/spec.json"
    args.query = []
    args.json = None
    args.no_auth = True
    return run_request(args)


def run_operations(args: argparse.Namespace) -> int:
    try:
        status, body, _headers = request(
            "GET",
            "/api-reference/spec.json",
            base_url=args.base_url,
            query=[],
            body=None,
            no_auth=True,
            auth_header=args.auth_header,
            trace_output=args.trace_output,
        )
    except ApiError as error:
        print(f"HTTP {error.status}", file=sys.stderr)
        if error.body:
            print(error.body.decode(errors="replace"), file=sys.stderr)
        return 1
    if status != 200:
        print(f"HTTP {status}", file=sys.stderr)
        return 1
    spec = json.loads(body)
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if method.startswith("x-"):
                continue
            op_id = operation.get("operationId", "")
            summary = operation.get("summary", "")
            print(f"{method.upper():6} {path:42} {op_id:28} {summary}")
    return 0


def add_request_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--query", action="append", help="Query parameter as key=value")
    parser.add_argument("--json", help="JSON request body, or @path/to/body.json")
    parser.add_argument("--output", help="Write raw response body to this path")
    parser.add_argument("--no-auth", action="store_true")
    parser.add_argument("--auth-header", choices=["bearer", "x-api-key"], default="bearer")
    parser.add_argument("--trace-output", help=f"Append trace JSONL events. Also configurable with {TRACE_ENV}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call the Semifluid API.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth = subparsers.add_parser("auth", help="Manage Semifluid OAuth credentials")
    auth_subparsers = auth.add_subparsers(dest="auth_command", required=True)

    login = auth_subparsers.add_parser("login", help="Authorize this helper with Semifluid OAuth")
    login.add_argument("--base-url", default=DEFAULT_BASE_URL)
    login.add_argument("--scope", default=DEFAULT_OAUTH_SCOPE)
    login.add_argument("--timeout", type=int, default=300)
    login.add_argument("--no-browser", action="store_true")
    login.set_defaults(func=run_oauth_login)

    status = auth_subparsers.add_parser("status", help="Check whether OAuth credentials are available")
    status.add_argument("--base-url", default=DEFAULT_BASE_URL)
    status.set_defaults(func=run_oauth_status)

    logout = auth_subparsers.add_parser("logout", help="Remove cached OAuth credentials")
    logout.set_defaults(func=run_oauth_logout)

    health = subparsers.add_parser("health", help="Call GET /v1/health")
    add_request_options(health)
    health.set_defaults(func=run_health)

    spec = subparsers.add_parser("spec", help="Fetch the live OpenAPI spec")
    add_request_options(spec)
    spec.set_defaults(func=run_spec)

    operations = subparsers.add_parser("operations", help="List operations from the live spec")
    operations.add_argument("--base-url", default=DEFAULT_BASE_URL)
    operations.add_argument("--auth-header", choices=["bearer", "x-api-key"], default="bearer")
    operations.add_argument("--trace-output", help=f"Append trace JSONL events. Also configurable with {TRACE_ENV}.")
    operations.set_defaults(func=run_operations)

    request_parser = subparsers.add_parser("request", help="Call any API path")
    request_parser.add_argument("method")
    request_parser.add_argument("path")
    add_request_options(request_parser)
    request_parser.set_defaults(func=run_request)

    for method in ("get", "post", "put", "patch", "delete"):
        method_parser = subparsers.add_parser(method, help=f"Shortcut for {method.upper()} requests")
        method_parser.add_argument("path")
        add_request_options(method_parser)
        method_parser.set_defaults(method=method.upper(), func=run_request)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
