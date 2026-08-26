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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from .state import dashboard_state

DEFAULT_DASHBOARD_PORT = 49505
DEFAULT_DASHBOARD_HOST = "0.0.0.0"

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """HTTP & SSE Handler for the RunZero Web Dashboard."""

    server_version = "RunZero-Dashboard/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default stdout access logging unless RUNZERO_DEBUG is set."""
        if os.getenv("RUNZERO_DEBUG", "").lower() in ("true", "1"):
            sys.stderr.write(f"[Dashboard:HTTP] {format % args}\n")

    def _send_json(self, status_code: int, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                return json.loads(raw_body)
            except json.JSONDecodeError:
                return {}
        return {}

    def _serve_file(self, filename: str, content_type: str) -> None:
        file_path = os.path.join(STATIC_DIR, filename)
        if not os.path.isfile(file_path):
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
        """Answer a CORS preflight request with an empty 204 and the allowed methods/headers."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Route GET requests: static UI assets, REST snapshot/log endpoints, and the /api/events SSE stream."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Static assets
        if path in ("", "/index.html"):
            self._serve_file("index.html", "text/html; charset=utf-8")
            return
        elif path == "/dashboard.css":
            self._serve_file("dashboard.css", "text/css; charset=utf-8")
            return
        elif path == "/dashboard.js":
            self._serve_file("dashboard.js", "application/javascript; charset=utf-8")
            return
        elif path.startswith("/fonts/"):
            font_filename = path.replace("/fonts/", "fonts/")
            self._serve_file(font_filename, "font/woff2")
            return

        # REST Endpoints
        if path in ("/api/status", "/api/fleet"):
            self._send_json(200, dashboard_state.get_snapshot())
            return

        if path == "/api/logs":
            self._send_json(200, {"logs": list(dashboard_state.log_buffer)})
            return

        # Server-Sent Events (SSE) Stream
        if path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            client_queue = dashboard_state.subscribe()
            try:
                # Send initial snapshot immediately
                initial_msg = f"event: state\ndata: {json.dumps(dashboard_state.get_snapshot())}\n\n"
                self.wfile.write(initial_msg.encode("utf-8"))
                self.wfile.flush()

                # Stream continuous events & keep-alive
                while True:
                    try:
                        item = client_queue.get(timeout=5.0)
                        event_type = item.get("type", "message")
                        data_json = json.dumps(item.get("data", {}))
                        event_msg = f"event: {event_type}\ndata: {data_json}\n\n"
                        self.wfile.write(event_msg.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        # Heartbeat ping
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
            finally:
                dashboard_state.unsubscribe(client_queue)
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})

    def do_POST(self) -> None:
        """Route POST requests: /api/actions/clean-cache and /api/actions/prune."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json()

        if path == "/api/actions/clean-cache":
            category = body.get("category", "all")
            res = dashboard_state.clean_cache(category)
            dashboard_state.append_log(f"[Dashboard] 🧹 Purged cache: {category}")
            self._send_json(200, res)
            return

        if path == "/api/actions/prune":
            try:
                from drivers import get_available_drivers
                drivers = get_available_drivers()
                for d in drivers.values():
                    runners = d.list_runners()
                    d.prune_exited(runners)
                dashboard_state.append_log("[Dashboard] ✂️  Triggered fleet runner prune across all active drivers.")
                self._send_json(200, {"status": "success", "message": "Prune executed"})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})


class DashboardServer:
    """Manages the Dashboard HTTP & SSE server lifecycle."""

    def __init__(self, host: str = DEFAULT_DASHBOARD_HOST, port: int = DEFAULT_DASHBOARD_PORT):
        """Store the bind address/port; the server isn't started until `start()` is called."""
        self.host = host
        self.port = port
        self.httpd: Optional[ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self._is_running = False

    def start(self, blocking: bool = False) -> None:
        """Start the ThreadingHTTPServer; either block the caller (`blocking=True`) or run it on a daemon thread.

        See the comment below for why this must be ThreadingHTTPServer, not plain HTTPServer.
        """
        # Plain HTTPServer handles one request at a time. /api/events (SSE)
        # blocks its handler thread in an infinite loop for the life of the
        # connection -- with a single-threaded server, the FIRST client to
        # open that stream (e.g. the dashboard's own frontend, which connects
        # automatically) permanently wedges the server: every other request,
        # including the container's own healthcheck against /api/status,
        # hangs forever after that (confirmed live: container stuck
        # "unhealthy", curl connects but gets 0 bytes back within the 5s
        # healthcheck timeout). ThreadingHTTPServer (stdlib since 3.7, no new
        # dependency) gives each connection its own thread so a long-lived
        # SSE stream can't starve every other request.
        self.httpd = ThreadingHTTPServer((self.host, self.port), DashboardRequestHandler)
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


def main():
    """Entrypoint: start the dashboard server standalone and block until a SIGINT/SIGTERM stops it."""
    host = os.getenv("DASHBOARD_HOST", DEFAULT_DASHBOARD_HOST)
    port = int(os.getenv("DASHBOARD_PORT", str(DEFAULT_DASHBOARD_PORT)))

    server = DashboardServer(host, port)

    def signal_handler(signum, frame):
        """Stop the dashboard server cleanly and exit the process."""
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 65)
    print(" ⚡ RunZero Real-Time Observability Dashboard v0.1.0")
    print(f" Web UI:  http://localhost:{port}")
    print("=" * 65)

    server.start(blocking=True)


if __name__ == "__main__":
    main()
