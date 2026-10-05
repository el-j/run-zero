"""
Request-hardening helpers shared by the dashboard and the Host VM Bridge HTTP servers.

Both servers are local control planes: they can wipe caches, spawn runners with
caller-supplied credentials, and destroy VMs. They are therefore protected in layers:

- **Loopback by default.** Both bind 127.0.0.1 unless told otherwise (containers still
  reach the host via ``host.docker.internal`` on Docker Desktop and OrbStack).
- **Host-header allowlist.** Rejects DNS-rebinding, where a web page re-points its own
  hostname at 127.0.0.1 to make same-origin requests to a loopback service.
- **JSON-only bodies, size-capped.** A browser cannot send ``application/json``
  cross-origin without a CORS preflight, and neither server grants CORS, so a hostile
  page can no longer drive a state-changing endpoint with a "simple" ``text/plain`` POST.
- **Optional bearer token** (constant-time compared) for callers that are not a browser.
- **Contained static paths.** Static file requests resolve inside their root directory
  or not at all.
"""

import contextlib
import hmac
import ipaddress
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

MAX_JSON_BODY_BYTES = 64 * 1024

# Hostnames a legitimate client uses to reach a loopback-bound service: a local browser,
# or a container reaching the host through Docker Desktop / OrbStack's host aliases.
DEFAULT_ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "host.docker.internal", "host.orb.internal"})


class RequestRejected(Exception):
    """A request failed validation; carries the HTTP status and message to send back."""

    def __init__(self, status: int, message: str):
        """Record the HTTP `status` code and client-facing `message` for this rejection."""
        super().__init__(message)
        self.status = status
        self.message = message


# Peer went away mid-request (browser tab closed, SSE client dropped, probe hung up).
CLIENT_DISCONNECT_ERRORS = (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, TimeoutError)


class ControlPlaneHTTPServer(ThreadingHTTPServer):
    """ThreadingHTTPServer whose per-request error reporting can never take a thread down.

    The stdlib's `handle_error` prints a traceback for every client that disconnects before
    finishing its request -- routine for a dashboard (closed tabs, dropped SSE streams) -- and
    if stderr itself is unusable that print raises and escapes the request thread. Client
    disconnects are ignored; anything else is still reported, best-effort.
    """

    runner_drivers: dict[str, Any] | None = None
    config: Any | None = None
    scaler: Any | None = None
    sse_heartbeat_interval: float = 5.0

    def handle_error(self, request: Any, client_address: Any) -> None:
        """Ignore client disconnects; report other request errors without ever raising."""
        if isinstance(sys.exception(), CLIENT_DISCONNECT_ERRORS):
            return
        with contextlib.suppress(Exception):
            super().handle_error(request, client_address)


def is_loopback_host(host: str) -> bool:
    """Return True when `host` (a bind address or hostname) only accepts local connections."""
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def allowed_hosts_from_env(env_var: str = "RUNZERO_ALLOWED_HOSTS") -> frozenset[str]:
    """Return DEFAULT_ALLOWED_HOSTS plus any comma-separated extra hostnames from `env_var`."""
    extra = {h.strip().lower() for h in os.getenv(env_var, "").split(",") if h.strip()}
    return DEFAULT_ALLOWED_HOSTS | extra


def _hostname_from_header(host_header: str) -> str:
    """Extract normalized hostname or IP from an HTTP Host header, stripping port and IPv6 brackets."""
    host = host_header.strip().lower()
    if host.startswith("["):  # [::1]:8080
        return host[1 : host.find("]")] if "]" in host else host
    if host.count(":") == 1:  # name:port or v4:port
        return host.split(":", 1)[0]
    return host  # bare name, bare v4, or bare v6


def check_host_header(handler: BaseHTTPRequestHandler, allowed: frozenset[str]) -> None:
    """Raise RequestRejected(421) unless the request's Host header names an allowed host.

    An empty `allowed` set disables the check (used when an operator deliberately exposes a
    server on a LAN address and lists nothing extra -- see allowed_hosts_from_env()).
    """
    if not allowed:
        return
    hostname = _hostname_from_header(handler.headers.get("Host", ""))
    if hostname not in allowed:
        raise RequestRejected(421, f"Host '{hostname}' is not allowed; add it to RUNZERO_ALLOWED_HOSTS to permit it")


def check_bearer_token(handler: BaseHTTPRequestHandler, expected: str) -> None:
    """Raise RequestRejected(401) unless `Authorization: Bearer <expected>` is present.

    An empty `expected` token disables the check.
    """
    if not expected:
        return
    supplied = handler.headers.get("Authorization", "")
    scheme, _, token = supplied.partition(" ")
    if scheme.lower() != "bearer" or not hmac.compare_digest(token.strip().encode(), expected.encode()):
        raise RequestRejected(401, "missing or invalid bearer token")


def read_json_body(handler: BaseHTTPRequestHandler, max_bytes: int = MAX_JSON_BODY_BYTES) -> dict[str, Any]:
    """Read and parse a JSON-object request body, enforcing Content-Type and size.

    An empty body is an empty dict. Raises RequestRejected with 400 (malformed length or
    JSON, or a non-object), 413 (too large) or 415 (not ``application/json``).
    """
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except ValueError as exc:
        raise RequestRejected(400, "invalid Content-Length") from exc
    if length < 0:
        raise RequestRejected(400, "invalid Content-Length")
    if length == 0:
        return {}
    if length > max_bytes:
        raise RequestRejected(413, f"request body exceeds {max_bytes} bytes")

    content_type = handler.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        raise RequestRejected(415, "Content-Type must be application/json")

    try:
        body = json.loads(handler.rfile.read(length).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RequestRejected(400, "request body is not valid JSON") from exc
    if not isinstance(body, dict):
        raise RequestRejected(400, "request body must be a JSON object")
    return body


def resolve_static_path(root: str, relative: str) -> str | None:
    """Return the real path of `relative` inside `root`, or None if it escapes `root` or isn't a file.

    Symlinks are resolved before the containment check, so a link pointing outside `root`
    is refused just like a ``..`` segment.
    """
    if not relative or "\x00" in relative or os.path.isabs(relative):
        return None
    real_root = os.path.realpath(root)
    candidate = os.path.realpath(os.path.join(real_root, relative))
    if os.path.commonpath([real_root, candidate]) != real_root or not os.path.isfile(candidate):
        return None
    return candidate
