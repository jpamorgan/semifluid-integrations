#!/usr/bin/env python3
"""Small Semifluid API helper for Codex skills."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://api.semifluid.ai"
TRACE_ENV = "SEMIFLUID_API_TRACE"
BEARER_TOKEN_ENV_VARS = (
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


def get_bearer_token() -> str:
    token = token_from_env(BEARER_TOKEN_ENV_VARS)
    if not token:
        names = ", ".join(BEARER_TOKEN_ENV_VARS)
        raise SystemExit(
            "Missing Semifluid bearer token. Codex MCP OAuth does not expose plugin "
            "access tokens to helper subprocesses. For direct shell API calls, set "
            f"one of: {names}. For normal authenticated plugin work, use the "
            "Semifluid MCP tools; if those report Auth required, reconnect or "
            "reauthorize the Semifluid plugin and retry in a new thread."
        )
    return token


def get_api_key() -> str:
    key = os.environ.get("SEMIFLUID_API_KEY")
    if not key:
        raise SystemExit(
            "Missing SEMIFLUID_API_KEY. API-key auth is only a compatibility mode; "
            "use Semifluid MCP tools for normal authenticated plugin work."
        )
    return key


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
    headers = {"Accept": "application/json", "User-Agent": "codex-semifluid-api/1.0"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if not no_auth:
        if auth_header == "x-api-key":
            headers["x-api-key"] = get_api_key()
        elif auth_header == "bearer":
            headers["Authorization"] = f"Bearer {get_bearer_token()}"
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
