#!/usr/bin/env python3
"""
⚡ RunZero — Host VM Bridge Server
Zero-dependency HTTP server running on the host machine to expose VM lifecycle
operations (OrbStack, Canonical Multipass, WSL2) to containerized RunZero daemons.
"""

import json
import os
import signal
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from drivers import RunnerDriver, RunnerInfo, get_available_drivers, get_driver
from drivers.docker_driver import DockerDriver

DEFAULT_BRIDGE_PORT = 49504
DEFAULT_BRIDGE_HOST = "0.0.0.0"

# get_driver() constructs a brand-new driver instance on every call -- fine
# for autoscaler.py, which calls it once at startup and holds the result for
# its whole lifetime, but the bridge previously called it fresh on EVERY
# incoming HTTP request. That silently discarded OrbStackVMDriver's
# _building_arches/_build_retry_after state (the backoff/dedup mechanism
# that stops a golden-image build from being retried every poll tick)
# between one request and the next. Confirmed live: the containerized
# autoscaler polls the bridge every POLL_INTERVAL (default 5s); each poll
# got served by a fresh, backoff-unaware driver instance, so the bridge
# deleted and recreated the "-building" staging VM roughly every 5s,
# forever -- provisioning never survived long enough to even write
# provision.log, let alone finish, stop, and rename. Caching one instance
# per driver name here makes the bridge behave like autoscaler.py's own
# persistent-driver model.
_driver_cache: Dict[str, RunnerDriver] = {}
_driver_cache_lock = threading.Lock()


def _get_cached_driver(name: str) -> RunnerDriver:
    key = name.lower().strip()
    with _driver_cache_lock:
        driver = _driver_cache.get(key)
        if driver is None:
            driver = get_driver(key)
            _driver_cache[key] = driver
        return driver


class VMBridgeRequestHandler(BaseHTTPRequestHandler):
    """Handles VM lifecycle requests from containerized autoscaler."""

    server_version = "RunZero-VMBridge/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default stdout access logging unless DEBUG is enabled."""
        if os.getenv("RUNZERO_DEBUG", "").lower() in ("true", "1"):
            sys.stderr.write(f"[VMBridge:HTTP] {format % args}\n")

    def _send_json(self, status_code: int, data: Dict[str, Any]) -> None:
        try:
            payload = json.dumps(data).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _read_json(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                return json.loads(raw_body)
            except json.JSONDecodeError:
                return {}
        return {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path in ("", "/health", "/api/health"):
            drivers = get_available_drivers()
            # VM bridge is for VM drivers (orbstack-vm, multipass, wsl2)
            vm_drivers = [k for k, d in drivers.items() if not isinstance(d, DockerDriver)]
            self._send_json(200, {
                "status": "ok",
                "service": "runzero-vm-bridge",
                "platform": sys.platform,
                "available_vm_drivers": vm_drivers,
                "all_drivers": list(drivers.keys())
            })
            return

        if path == "/api/status":
            drivers = get_available_drivers()
            self._send_json(200, {
                "status": "ok",
                "available_drivers": list(drivers.keys()),
                "platform": sys.platform
            })
            return

        # /api/drivers/{driver_name}/runners
        parts = [p for p in path.split("/") if p]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "drivers" and parts[3] == "runners":
            driver_name = parts[2]
            try:
                driver = _get_cached_driver(driver_name)
                runners = driver.list_runners()
                self._send_json(200, {
                    "driver": driver_name,
                    "runners": [r.to_dict() for r in runners]
                })
            except Exception as e:
                self._send_json(500, {"error": str(e), "driver": driver_name})
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        parts = [p for p in path.split("/") if p]

        if len(parts) >= 4 and parts[0] == "api" and parts[1] == "drivers":
            driver_name = parts[2]
            action = parts[3]
            body = self._read_json()

            try:
                driver = _get_cached_driver(driver_name)
            except Exception as e:
                self._send_json(400, {"error": f"Invalid driver: {driver_name} ({e})"})
                return

            if action == "spawn":
                try:
                    runner_id = driver.spawn_runner(
                        repo=body.get("repo"),
                        org=body.get("org"),
                        arch=body.get("arch", "arm64"),
                        labels=body.get("labels"),
                        access_token=body.get("access_token"),
                        cache_mounts=body.get("cache_mounts"),
                        proxies_enabled=body.get("proxies_enabled", True),
                        extra_env=body.get("extra_env")
                    )
                    self._send_json(200, {
                        "status": "success",
                        "driver": driver_name,
                        "runner_id": runner_id
                    })
                except Exception as e:
                    self._send_json(500, {"error": str(e), "driver": driver_name})
                return

            elif action == "prune":
                try:
                    runners_data = body.get("runners", [])
                    runners = [
                        RunnerInfo(
                            id=r.get("id", ""),
                            name=r.get("name", ""),
                            status=r.get("status", ""),
                            state=r.get("state", ""),
                            target_repo=r.get("target_repo", ""),
                            target_arch=r.get("target_arch", ""),
                            backend=r.get("backend", driver_name),
                            created_at=r.get("created_at")
                        )
                        for r in runners_data
                    ]
                    driver.prune_exited(runners)
                    self._send_json(200, {"status": "success", "driver": driver_name})
                except Exception as e:
                    self._send_json(500, {"error": str(e), "driver": driver_name})
                return

            elif action == "destroy":
                runner_id = body.get("runner_id") or (parts[4] if len(parts) > 4 else None)
                if not runner_id:
                    self._send_json(400, {"error": "runner_id is required"})
                    return
                try:
                    success = driver.destroy_runner(runner_id)
                    self._send_json(200, {"status": "success", "destroyed": success, "runner_id": runner_id})
                except Exception as e:
                    self._send_json(500, {"error": str(e), "driver": driver_name})
                return

            elif action == "cleanup":
                try:
                    driver.cleanup_all()
                    self._send_json(200, {"status": "success", "driver": driver_name})
                except Exception as e:
                    self._send_json(500, {"error": str(e), "driver": driver_name})
                return

            elif action == "ensure-base-stopped":
                try:
                    ensure_fn = getattr(driver, "ensure_base_images_stopped", None)
                    if callable(ensure_fn):
                        ensure_fn()
                    self._send_json(200, {"status": "success", "driver": driver_name})
                except Exception as e:
                    self._send_json(500, {"error": str(e), "driver": driver_name})
                return

            elif action == "build-base":
                arch = body.get("arch", "arm64")
                try:
                    build_fn = getattr(driver, "build_base_image", None)
                    if callable(build_fn):
                        ok = build_fn(arch)
                        self._send_json(200, {"status": "success", "driver": driver_name, "arch": arch, "built": ok})
                    else:
                        self._send_json(400, {"error": f"Driver {driver_name} does not support build_base_image"})
                except Exception as e:
                    self._send_json(500, {"error": str(e), "driver": driver_name})
                return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})


class VMBridgeServer:
    """Manages the lifecycle of the Host VM Bridge HTTP server."""

    def __init__(self, host: str = DEFAULT_BRIDGE_HOST, port: int = DEFAULT_BRIDGE_PORT):
        self.host = host
        self.port = port
        self.httpd: Optional[ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self._is_running = False

    def start(self, blocking: bool = False) -> None:
        # Plain HTTPServer serves one request at a time. The "build-base"
        # action calls driver.build_base_image() synchronously in the
        # handler -- a real golden-image build takes 15-25 minutes, during
        # which a single-threaded server can't answer ANY other request
        # (spawn/list/prune/status for every driver/repo/arch), defeating the
        # whole point of build_base_image()'s own internal async-thread
        # design (it's meant to let the poll loop keep moving while a build
        # runs). ThreadingHTTPServer (stdlib since 3.7, no new dependency)
        # gives each connection its own thread so one long call can't starve
        # the rest of the bridge.
        self.httpd = ThreadingHTTPServer((self.host, self.port), VMBridgeRequestHandler)
        self._is_running = True
        print(f"[VMBridge] 🚀 Host VM Bridge listening on http://{self.host}:{self.port}")

        if blocking:
            try:
                self.httpd.serve_forever()
            except KeyboardInterrupt:
                self.stop()
        else:
            self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.thread.start()

    def stop(self) -> None:
        if self._is_running and self.httpd:
            print("\n[VMBridge] Shutting down Host VM Bridge...")
            self._is_running = False
            self.httpd.shutdown()
            self.httpd.server_close()
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2.0)
            print("[VMBridge] Bridge stopped cleanly.")


def main():
    host = os.getenv("HOST_VM_BRIDGE_HOST", DEFAULT_BRIDGE_HOST)
    port = int(os.getenv("HOST_VM_BRIDGE_PORT", str(DEFAULT_BRIDGE_PORT)))

    server = VMBridgeServer(host, port)

    def signal_handler(signum, frame):
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 65)
    print(" 🌉 RunZero Host VM Bridge v0.1.0")
    print(f" Listening: http://{host}:{port}")
    print(f" Platform:  {sys.platform}")
    print("=" * 65)

    server.start(blocking=True)


if __name__ == "__main__":
    main()
