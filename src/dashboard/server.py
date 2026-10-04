"""
RunZero Real-Time Observability Web Dashboard Server
Serves static UI assets, REST API, and Server-Sent Events (SSE) stream for live updates.
"""

import json
import os
import queue
import signal
import sys
import threading
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse

from config import Config, ConfigError, load_config
from http_security import (
    ControlPlaneHTTPServer,
    RequestRejected,
    allowed_hosts_from_env,
    check_host_header,
    read_json_body,
    resolve_static_path,
)
from version import __version__

from .cache_service import get_cache_stats, purge_cache
from .runner_service import execute_runner_action
from .settings_service import get_live_settings, update_live_settings
from .state import dashboard_state
from .workflow_service import execute_workflow_action

DEFAULT_DASHBOARD_PORT = 49505
# Loopback by default: the dashboard can purge caches and prune runners. The container
# image overrides this (DASHBOARD_HOST=0.0.0.0) and docker-compose publishes the port on
# the host's 127.0.0.1 only.
DEFAULT_DASHBOARD_HOST = "127.0.0.1"

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
FONTS_DIR = os.path.join(STATIC_DIR, "fonts")
DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "web", "dist"))


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """HTTP & SSE Handler for the RunZero Web Dashboard."""

    server_version = "RunZero-Dashboard/1.0"
    sse_heartbeat_interval: float = 5.0

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default stdout access logging unless RUNZERO_DEBUG is set."""
        if os.getenv("RUNZERO_DEBUG", "").lower() in ("true", "1"):
            sys.stderr.write(f"[Dashboard:HTTP] {format % args}\n")

    def _send_json(self, status_code: int, data: dict[str, Any]) -> None:
        """Serialize payload to JSON and send response with cache-control headers."""
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def _admit(self) -> bool:
        """Apply the Host-header allowlist; on rejection send the error and return False."""
        try:
            check_host_header(self, allowed_hosts_from_env())
        except RequestRejected as rej:
            self._send_json(rej.status, {"error": rej.message})
            return False
        return True

    def _serve_file(self, root: str, relative: str, content_type: str) -> None:
        """Safely resolve and serve a static asset within root directory."""
        file_path = resolve_static_path(root, relative)
        if file_path is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))

    def do_OPTIONS(self) -> None:
        """Answer a CORS preflight with 204 but no Access-Control-Allow-* headers.

        The dashboard UI is same-origin, so it never preflights; granting nothing here is
        what stops a foreign page from issuing JSON POSTs against the action endpoints.
        """
        self.send_response(204)
        self.end_headers()

    def _serve_static_route(self, path: str) -> bool:
        """Serve static files or fonts if matching, returning True if handled."""
        if os.path.isdir(DIST_DIR):
            if path in ("", "/index.html"):
                self._serve_file(DIST_DIR, "index.html", "text/html; charset=utf-8")
                return True
            if path.startswith("/assets/"):
                asset_rel = path[len("/assets/") :]
                mime = "text/css; charset=utf-8" if asset_rel.endswith(".css") else "application/javascript; charset=utf-8"
                self._serve_file(os.path.join(DIST_DIR, "assets"), asset_rel, mime)
                return True

        if path in ("", "/index.html"):
            self._serve_file(STATIC_DIR, "index.html", "text/html; charset=utf-8")
            return True
        if path == "/dashboard.css":
            self._serve_file(STATIC_DIR, "dashboard.css", "text/css; charset=utf-8")
            return True
        if path == "/dashboard.js":
            self._serve_file(STATIC_DIR, "dashboard.js", "application/javascript; charset=utf-8")
            return True
        if path.startswith("/fonts/"):
            font_name = path[len("/fonts/") :]
            if "/" in font_name or "\\" in font_name or not font_name.endswith(".woff2"):
                font_name = ""
            self._serve_file(FONTS_DIR, font_name, "font/woff2")
            return True
        return False

    def _stream_sse_events(self) -> None:
        """Stream real-time Server-Sent Events updates and periodic heartbeat pings."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        client_queue = dashboard_state.subscribe()
        try:
            initial_msg = f"event: state\ndata: {json.dumps(dashboard_state.get_snapshot())}\n\n"
            self.wfile.write(initial_msg.encode("utf-8"))
            self.wfile.flush()

            heartbeat_interval = float(getattr(self.server, "sse_heartbeat_interval", getattr(self, "sse_heartbeat_interval", 5.0)))
            while True:
                try:
                    item = client_queue.get(timeout=heartbeat_interval)
                    event_type = item.get("type", "message")
                    data_json = json.dumps(item.get("data", {}))
                    event_msg = f"event: {event_type}\ndata: {data_json}\n\n"
                    self.wfile.write(event_msg.encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass
        finally:
            dashboard_state.unsubscribe(client_queue)

    def do_GET(self) -> None:
        """Route GET requests: static UI assets, REST snapshot/log endpoints, and the /api/events SSE stream."""
        if not self._admit():
            return
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if self._serve_static_route(path):
            return

        if path in ("/api/status", "/api/fleet"):
            self._send_json(200, dashboard_state.get_snapshot())
            return
        if path == "/api/settings":
            cfg = getattr(self.server, "config", None) or load_config()
            self._send_json(200, get_live_settings(cfg))
            return
        if path == "/api/cache":
            self._send_json(200, get_cache_stats(dashboard_state.cache_dir))
            return
        if path == "/api/logs":
            self._send_json(200, {"logs": list(dashboard_state.log_buffer)})
            return
        if path in ("/api/events", "/api/stream"):
            self._stream_sse_events()
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})

    def _handle_clean_cache_action(self, body: dict[str, Any]) -> None:
        """Handle /api/actions/clean-cache POST requests."""
        category = body.get("category", "all")
        if not isinstance(category, str):
            self._send_json(400, {"error": "category must be a string"})
            return
        res = dashboard_state.clean_cache(category)
        dashboard_state.append_log(f"[Dashboard] 🧹 Purged cache: {category}")
        self._send_json(200, res)

    def _handle_prune_action(self) -> None:
        """Handle /api/actions/prune POST requests across active runner drivers."""
        try:
            drivers = getattr(self.server, "runner_drivers", None)
            if drivers is None:
                from drivers import get_available_drivers

                drivers = get_available_drivers()
            for d in drivers.values():
                runners = d.list_runners()
                d.prune_exited(runners)
            dashboard_state.append_log("[Dashboard] ✂️  Triggered fleet runner prune across all active drivers.")
            self._send_json(200, {"status": "success", "message": "Prune executed"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_repo_priority_action(self, body: dict[str, Any]) -> None:
        """Handle /api/actions/repo-priority POST requests."""
        priority = body.get("priority", [])
        paused = body.get("paused", [])
        if not isinstance(priority, list) or not all(isinstance(x, str) for x in priority):
            self._send_json(400, {"error": "priority must be a list of strings"})
            return
        if not isinstance(paused, list) or not all(isinstance(x, str) for x in paused):
            self._send_json(400, {"error": "paused must be a list of strings"})
            return
        res = dashboard_state.set_repo_priority(priority, paused)
        prio_str = ", ".join(priority) or "default"
        paused_str = ", ".join(paused) or "none"
        dashboard_state.append_log(f"[Dashboard] 🔀 Updated repository priority: {prio_str} (paused: {paused_str})")
        self._send_json(200, res)

    def _handle_settings_action(self, body: dict[str, Any]) -> None:
        """Handle /api/settings POST requests."""
        cfg = getattr(self.server, "config", None) or load_config()
        try:
            new_cfg, live_settings = update_live_settings(body, cfg)
            if hasattr(self.server, "config"):
                self.server.config = new_cfg
            dashboard_state.append_log("[Dashboard] ⚙️  Updated live system settings.")
            self._send_json(200, {"ok": True, "settings": live_settings})
        except (ValueError, ConfigError) as err:
            self._send_json(400, {"error": str(err)})

    def _handle_cache_purge_action(self, body: dict[str, Any]) -> None:
        """Handle /api/cache/purge POST requests."""
        category = body.get("category")
        repo = body.get("repo")
        all_caches = bool(body.get("all", False))
        res = purge_cache(dashboard_state.cache_dir, category=category, repo=repo, all_caches=all_caches)
        cat_label = category or ("all" if all_caches else "unspecified")
        dashboard_state.append_log(f"[Dashboard] 🧹 Purged cache: {cat_label}")
        self._send_json(200, {"ok": True, "cleared": res.get("cleared", [])})

    def _handle_workflow_action(self, body: dict[str, Any]) -> None:
        """Handle /api/actions/workflow POST requests."""
        repo = str(body.get("repo", ""))
        run_id = int(body.get("run_id", 0))
        action = str(body.get("action", ""))
        cfg = getattr(self.server, "config", None) or load_config()
        try:
            res = execute_workflow_action(repo, run_id, action, cfg.access_token)
            dashboard_state.append_log(f"[Dashboard] ⚡ Triggered workflow action '{action}' on {repo} run #{run_id}.")
            self._send_json(200, res)
        except (ValueError, RuntimeError) as err:
            self._send_json(400, {"error": str(err)})

    def _handle_runner_action(self, body: dict[str, Any]) -> None:
        """Handle /api/actions/runner POST requests."""
        action = str(body.get("action", ""))
        runner_id = body.get("runner_id")
        repo = body.get("repo")
        arch = body.get("arch")
        drivers = getattr(self.server, "runner_drivers", None)
        scaler = getattr(self.server, "scaler", None)
        try:
            res = execute_runner_action(action, runner_id=runner_id, repo=repo, arch=arch, drivers=drivers, scaler=scaler)
            dashboard_state.append_log(f"[Dashboard] 🏃 Runner control action: {action}.")
            self._send_json(200, res)
        except (ValueError, RuntimeError) as err:
            self._send_json(400, {"error": str(err)})

    def do_POST(self) -> None:
        """Route POST requests for settings, cache, workflow, runner, and fleet actions."""
        if not self._admit():
            return
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        valid_post_routes = (
            "/api/actions/clean-cache",
            "/api/actions/prune",
            "/api/actions/repo-priority",
            "/api/settings",
            "/api/cache/purge",
            "/api/actions/workflow",
            "/api/actions/runner",
        )
        if path not in valid_post_routes:
            self._send_json(404, {"error": f"Endpoint not found: {path}"})
            return
        try:
            body = read_json_body(self)
        except RequestRejected as rej:
            self._send_json(rej.status, {"error": rej.message})
            return

        handlers = {
            "/api/actions/clean-cache": self._handle_clean_cache_action,
            "/api/actions/repo-priority": self._handle_repo_priority_action,
            "/api/settings": self._handle_settings_action,
            "/api/cache/purge": self._handle_cache_purge_action,
            "/api/actions/workflow": self._handle_workflow_action,
            "/api/actions/runner": self._handle_runner_action,
        }
        if path == "/api/actions/prune":
            self._handle_prune_action()
        else:
            handlers[path](body)


class DashboardServer:
    """Manages the Dashboard HTTP & SSE server lifecycle."""

    def __init__(
        self,
        host: str = DEFAULT_DASHBOARD_HOST,
        port: int = DEFAULT_DASHBOARD_PORT,
        drivers: dict[str, Any] | None = None,
        config: Config | None = None,
        scaler: Any | None = None,
        sse_heartbeat_interval: float = 5.0,
    ):
        """Store the bind address/port, optional driver registry, and heartbeat interval; nothing starts until `start()`.

        `drivers` is the autoscaler's registry, used by the prune action instead of building
        fresh driver instances per request.
        `config` is the autoscaler's live Config instance.
        `scaler` is the optional autoscaler instance for runner control actions.
        `sse_heartbeat_interval` is the queue timeout in seconds before sending an SSE keepalive ping.
        """
        self.host = host
        self.port = port
        self.drivers = drivers
        self.config = config
        self.scaler = scaler
        self.sse_heartbeat_interval = sse_heartbeat_interval
        self.httpd: ControlPlaneHTTPServer | None = None
        self.thread: threading.Thread | None = None
        self._is_running = False

    def start(self, blocking: bool = False) -> None:
        """Start the ThreadingHTTPServer; either block the caller (`blocking=True`) or run it on a daemon thread.

        See the comment below for why this must be ThreadingHTTPServer, not plain HTTPServer.
        """
        self.httpd = ControlPlaneHTTPServer((self.host, self.port), DashboardRequestHandler)
        self.httpd.runner_drivers = self.drivers
        self.httpd.config = self.config
        self.httpd.scaler = self.scaler
        self.httpd.sse_heartbeat_interval = self.sse_heartbeat_interval
        self._is_running = True
        print(f"[Dashboard] 📊 Real-Time Web UI running at http://localhost:{self.port}")

        if blocking:
            try:
                self.httpd.serve_forever()
            except KeyboardInterrupt:
                self.stop()
        else:
            self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        """Shut down the HTTP server and join its serving thread (up to 2s), if running."""
        if self._is_running and self.httpd:
            print("\n[Dashboard] Stopping Web Dashboard...")
            self._is_running = False
            self.httpd.shutdown()
            self.httpd.server_close()
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)
            print("[Dashboard] Dashboard stopped cleanly.")


def main() -> None:
    """Entrypoint: start the dashboard server standalone and block until a SIGINT/SIGTERM stops it."""
    host = os.getenv("DASHBOARD_HOST", DEFAULT_DASHBOARD_HOST)
    port = int(os.getenv("DASHBOARD_PORT", str(DEFAULT_DASHBOARD_PORT)))

    server = DashboardServer(host, port)

    def signal_handler(signum: int, frame: object) -> None:
        """Stop the dashboard server cleanly and exit the process."""
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 65)
    print(f" ⚡ RunZero Real-Time Observability Dashboard v{__version__}")
    print(f" Web UI:  http://localhost:{port}")
    print("=" * 65)

    server.start(blocking=True)


if __name__ == "__main__":  # pragma: no cover -- CLI entrypoint guard, only runs via `python -m dashboard.server`
    main()
