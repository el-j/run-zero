"""
Security regression tests for the dashboard and Host VM Bridge control planes.

Two layers:
  - Unit tests for every helper in src/http_security.py.
  - Live-socket tests against the REAL DashboardServer / VMBridgeServer on an ephemeral
    loopback port, using raw http.client so request paths and headers go on the wire
    exactly as written (urllib would add its own Host / Content-Type).

Each live test pins one hardening property: static-path containment, the Host-header
allowlist (anti DNS-rebinding), JSON-only size-capped bodies, no CORS grant, the bridge
bearer token, and loopback-by-default binding.
"""

import http.client
import io
import json
import os
import tempfile
import unittest
from typing import Any, ClassVar
from unittest.mock import MagicMock, patch

import http_security
import vm_bridge
from dashboard.server import DEFAULT_DASHBOARD_HOST, DashboardServer
from drivers.bridge_driver import BridgeVMDriver
from http_security import (
    RequestRejected,
    _hostname_from_header,
    allowed_hosts_from_env,
    check_bearer_token,
    check_host_header,
    is_loopback_host,
    read_json_body,
    resolve_static_path,
)
from vm_bridge import DEFAULT_BRIDGE_HOST, VMBridgeServer


def _handler(headers: dict[str, str], body: bytes = b"") -> Any:
    """A stand-in for BaseHTTPRequestHandler exposing just .headers and .rfile."""
    handler = MagicMock()
    handler.headers = headers
    handler.rfile = io.BytesIO(body)
    return handler


class TestHostnameParsing(unittest.TestCase):
    def test_variants(self):
        cases = {
            "localhost:49505": "localhost",
            "LOCALHOST": "localhost",
            "127.0.0.1:1": "127.0.0.1",
            "[::1]:49504": "::1",
            "[::1": "[::1",
            "::1": "::1",
            " host.docker.internal:49504 ": "host.docker.internal",
            "": "",
        }
        for header, expected in cases.items():
            with self.subTest(header=header):
                self.assertEqual(_hostname_from_header(header), expected)


class TestIsLoopbackHost(unittest.TestCase):
    def test_loopback_and_not(self):
        for host in ("127.0.0.1", "127.8.9.10", "::1", "localhost"):
            self.assertTrue(is_loopback_host(host), host)
        for host in ("0.0.0.0", "::", "192.168.1.5", "example.com", ""):
            self.assertFalse(is_loopback_host(host), host)


class TestAllowedHostsFromEnv(unittest.TestCase):
    def test_defaults_plus_extras(self):
        with patch.dict(os.environ, {"RUNZERO_ALLOWED_HOSTS": " Runner.LAN , ,10.0.0.2"}):
            hosts = allowed_hosts_from_env()
        self.assertTrue(hosts >= http_security.DEFAULT_ALLOWED_HOSTS)
        self.assertIn("runner.lan", hosts)
        self.assertIn("10.0.0.2", hosts)
        self.assertNotIn("", hosts)

    def test_defaults_only(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(allowed_hosts_from_env(), http_security.DEFAULT_ALLOWED_HOSTS)


class TestCheckHostHeader(unittest.TestCase):
    def test_allowed_passes(self):
        check_host_header(_handler({"Host": "localhost:49505"}), frozenset({"localhost"}))

    def test_foreign_host_rejected_421(self):
        with self.assertRaises(RequestRejected) as cm:
            check_host_header(_handler({"Host": "attacker.example:49505"}), frozenset({"localhost"}))
        self.assertEqual(cm.exception.status, 421)

    def test_missing_host_rejected(self):
        with self.assertRaises(RequestRejected):
            check_host_header(_handler({}), frozenset({"localhost"}))

    def test_empty_allowlist_disables_check(self):
        check_host_header(_handler({"Host": "anything"}), frozenset())


class TestCheckBearerToken(unittest.TestCase):
    def test_no_expected_token_disables_check(self):
        check_bearer_token(_handler({}), "")

    def test_correct_token_passes(self):
        check_bearer_token(_handler({"Authorization": "Bearer s3cret"}), "s3cret")
        check_bearer_token(_handler({"Authorization": "bearer s3cret"}), "s3cret")

    def test_wrong_missing_or_malformed_rejected_401(self):
        for header in ({}, {"Authorization": "Bearer nope"}, {"Authorization": "Basic s3cret"}, {"Authorization": "s3cret"}):
            with self.subTest(header=header), self.assertRaises(RequestRejected) as cm:
                check_bearer_token(_handler(header), "s3cret")
            self.assertEqual(cm.exception.status, 401)


class TestReadJsonBody(unittest.TestCase):
    JSON: ClassVar[dict[str, str]] = {"Content-Type": "application/json"}

    def _status(self, headers: dict[str, str], body: bytes = b"", **kw: Any) -> int:
        with self.assertRaises(RequestRejected) as cm:
            read_json_body(_handler(headers, body), **kw)
        return cm.exception.status

    def test_empty_body_is_empty_dict(self):
        self.assertEqual(read_json_body(_handler({})), {})
        self.assertEqual(read_json_body(_handler({"Content-Length": ""})), {})

    def test_valid_object(self):
        body = b'{"a": 1}'
        headers = {"Content-Type": "application/json; charset=utf-8", "Content-Length": str(len(body))}
        self.assertEqual(read_json_body(_handler(headers, body)), {"a": 1})

    def test_rejections(self):
        self.assertEqual(self._status({"Content-Length": "abc"}), 400)
        self.assertEqual(self._status({"Content-Length": "-1"}), 400)
        self.assertEqual(self._status({**self.JSON, "Content-Length": "11"}, b"x" * 11, max_bytes=10), 413)
        self.assertEqual(self._status({"Content-Type": "text/plain", "Content-Length": "2"}, b"{}"), 415)
        self.assertEqual(self._status({"Content-Length": "2"}, b"{}"), 415)
        self.assertEqual(self._status({**self.JSON, "Content-Length": "3"}, b"{{{"), 400)
        self.assertEqual(self._status({**self.JSON, "Content-Length": "2"}, b"\xff\xfe"), 400)
        self.assertEqual(self._status({**self.JSON, "Content-Length": "2"}, b"[]"), 400)


class TestResolveStaticPath(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        self.root = os.path.join(self.tmp, "static")
        os.makedirs(os.path.join(self.root, "fonts"))
        with open(os.path.join(self.root, "fonts", "a.woff2"), "wb") as fh:
            fh.write(b"font")
        self.secret = os.path.join(self.tmp, "secret.txt")
        with open(self.secret, "w") as fh:
            fh.write("canary")

    def test_inside_root_resolves(self):
        self.assertEqual(resolve_static_path(self.root, "fonts/a.woff2"), os.path.realpath(os.path.join(self.root, "fonts", "a.woff2")))

    def test_escapes_and_bad_inputs_refused(self):
        for rel in ("../secret.txt", "fonts/../../secret.txt", self.secret, "", "fonts/a.woff2\x00", "fonts", "missing.css"):
            with self.subTest(rel=rel):
                self.assertIsNone(resolve_static_path(self.root, rel))

    def test_symlink_pointing_outside_root_refused(self):
        os.symlink(self.secret, os.path.join(self.root, "link.css"))
        self.assertIsNone(resolve_static_path(self.root, "link.css"))


class _LiveServerMixin:
    """Raw http.client helpers against a real server on an ephemeral loopback port."""

    port: int

    def request(self, method: str, path: str, body: bytes | None = None, headers: dict[str, str] | None = None) -> tuple[int, bytes]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            merged = {"Host": f"localhost:{self.port}", **(headers or {})}
            if body is not None:
                merged.setdefault("Content-Length", str(len(body)))
            for key, value in merged.items():
                conn.putheader(key, value)
            conn.endheaders(body)
            resp = conn.getresponse()
            return resp.status, resp.read()
        finally:
            conn.close()


class TestDashboardHardeningLive(_LiveServerMixin, unittest.TestCase):
    def setUp(self):
        patcher = patch.dict(os.environ, {}, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("RUNZERO_ALLOWED_HOSTS", None)
        self.server = DashboardServer(host="127.0.0.1", port=0)
        self.server.start(blocking=False)
        self.addCleanup(self.server.stop)
        assert self.server.httpd is not None
        self.port = self.server.httpd.server_port

    def test_default_bind_is_loopback(self):
        self.assertEqual(DEFAULT_DASHBOARD_HOST, "127.0.0.1")

    def test_font_route_serves_real_font(self):
        status, body = self.request("GET", "/fonts/outfit-latin.woff2")
        self.assertEqual(status, 200)
        self.assertTrue(body)

    def test_path_traversal_is_refused(self):
        for path in (
            "/fonts/../server.py",
            "/fonts/../../server.py",
            "/fonts/..%2f..%2fserver.py",
            "/fonts/%2e%2e/%2e%2e/server.py",
            "/fonts//etc/passwd",
            "/fonts/../index.html",
            "/fonts/outfit-latin.woff2/../../server.py",
            "/fonts/..\\server.py",
        ):
            with self.subTest(path=path):
                status, body = self.request("GET", path)
                self.assertEqual(status, 404)
                self.assertNotIn(b"import", body)

    def test_foreign_host_header_is_refused(self):
        for method, path, body, headers in (
            ("GET", "/api/status", None, {}),
            ("POST", "/api/actions/clean-cache", b"{}", {"Content-Type": "application/json"}),
        ):
            with self.subTest(method=method), patch("dashboard.server.dashboard_state.clean_cache") as clean:
                status, _ = self.request(method, path, body, {"Host": "rebind.attacker.example", **headers})
                self.assertEqual(status, 421)
                clean.assert_not_called()

    def test_simple_cross_origin_post_cannot_trigger_action(self):
        # A browser form / fetch "simple request" can only send text/plain,
        # multipart/form-data or x-www-form-urlencoded without a preflight.
        for ctype in ("text/plain", "application/x-www-form-urlencoded", "multipart/form-data; boundary=x"):
            with self.subTest(ctype=ctype), patch("dashboard.server.dashboard_state.clean_cache") as clean:
                status, _ = self.request("POST", "/api/actions/clean-cache", b'{"category":"all"}', {"Content-Type": ctype})
                self.assertEqual(status, 415)
                clean.assert_not_called()

    def test_oversized_body_is_refused(self):
        body = b'{"category":"' + b"a" * (http_security.MAX_JSON_BODY_BYTES + 1) + b'"}'
        with patch("dashboard.server.dashboard_state.clean_cache") as clean:
            status, _ = self.request("POST", "/api/actions/clean-cache", body, {"Content-Type": "application/json"})
        self.assertEqual(status, 413)
        clean.assert_not_called()

    def test_non_string_category_is_refused(self):
        with patch("dashboard.server.dashboard_state.clean_cache") as clean:
            status, _ = self.request("POST", "/api/actions/clean-cache", b'{"category": ["npm"]}', {"Content-Type": "application/json"})
        self.assertEqual(status, 400)
        clean.assert_not_called()

    def test_same_origin_json_post_still_works(self):
        with patch("dashboard.server.dashboard_state.clean_cache", return_value={"status": "success"}) as clean:
            status, body = self.request("POST", "/api/actions/clean-cache", b'{"category":"npm"}', {"Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "success")
        clean.assert_called_once_with("npm")

    def test_no_cors_headers_on_responses(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/api/status", headers={"Host": "localhost", "Origin": "https://attacker.example"})
        resp = conn.getresponse()
        resp.read()
        conn.close()
        self.assertEqual(resp.status, 200)
        self.assertIsNone(resp.getheader("Access-Control-Allow-Origin"))


class TestBridgeHardeningLive(_LiveServerMixin, unittest.TestCase):
    TOKEN = "unit-test-bridge-token"

    def setUp(self):
        patcher = patch.dict(os.environ, {"RUNZERO_BRIDGE_TOKEN": self.TOKEN}, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("RUNZERO_ALLOWED_HOSTS", None)
        vm_bridge._driver_cache.clear()
        self.addCleanup(vm_bridge._driver_cache.clear)
        self.driver = MagicMock()
        self.driver.spawn_runner.return_value = "runner-1"
        get_driver = patch("vm_bridge.get_driver", return_value=self.driver)
        get_driver.start()
        self.addCleanup(get_driver.stop)
        self.server = VMBridgeServer(host="127.0.0.1", port=0)
        self.server.start(blocking=False)
        self.addCleanup(self.server.stop)
        assert self.server.httpd is not None
        self.port = self.server.httpd.server_port

    def _spawn(self, headers: dict[str, str]) -> int:
        status, _ = self.request("POST", "/api/drivers/orbstack-vm/spawn", b'{"repo":"o/r"}', {"Content-Type": "application/json", **headers})
        return status

    def test_default_bind_is_loopback(self):
        self.assertEqual(DEFAULT_BRIDGE_HOST, "127.0.0.1")

    def test_driver_routes_require_the_token(self):
        self.assertEqual(self._spawn({}), 401)
        self.assertEqual(self._spawn({"Authorization": "Bearer wrong"}), 401)
        status, _ = self.request("GET", "/api/drivers/orbstack-vm/runners")
        self.assertEqual(status, 401)
        self.driver.spawn_runner.assert_not_called()
        self.driver.list_runners.assert_not_called()

    def test_correct_token_is_accepted(self):
        self.assertEqual(self._spawn({"Authorization": f"Bearer {self.TOKEN}"}), 200)
        self.driver.spawn_runner.assert_called_once()

    def test_health_is_public(self):
        with patch("vm_bridge.get_available_drivers", return_value={}):
            status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "ok")

    def test_container_host_alias_is_allowed_but_foreign_host_is_not(self):
        auth = {"Authorization": f"Bearer {self.TOKEN}"}
        self.assertEqual(self._spawn({**auth, "Host": "host.docker.internal:49504"}), 200)
        self.assertEqual(self._spawn({**auth, "Host": "rebind.attacker.example"}), 421)

    def test_text_plain_spawn_is_refused(self):
        status, _ = self.request(
            "POST", "/api/drivers/orbstack-vm/spawn", b'{"repo":"o/r"}', {"Content-Type": "text/plain", "Authorization": f"Bearer {self.TOKEN}"}
        )
        self.assertEqual(status, 415)
        self.driver.spawn_runner.assert_not_called()


class TestBridgeBindPolicy(unittest.TestCase):
    def test_non_loopback_bind_without_token_refused(self):
        with patch.dict(os.environ, {"RUNZERO_BRIDGE_TOKEN": ""}):
            server = VMBridgeServer(host="0.0.0.0", port=0)
            with self.assertRaises(ValueError):
                server.start(blocking=False)
            self.assertIsNone(server.httpd)

    def test_non_loopback_bind_with_token_allowed(self):
        with patch.dict(os.environ, {"RUNZERO_BRIDGE_TOKEN": "t"}), patch("vm_bridge.ThreadingHTTPServer") as httpd:
            VMBridgeServer(host="0.0.0.0", port=0).start(blocking=False)
        httpd.assert_called_once()

    def test_loopback_without_token_warns(self):
        with (
            patch.dict(os.environ, {"RUNZERO_BRIDGE_TOKEN": ""}),
            patch("vm_bridge.ThreadingHTTPServer"),
            patch("sys.stderr", new_callable=io.StringIO) as err,
        ):
            VMBridgeServer(host="127.0.0.1", port=0).start(blocking=False)
        self.assertIn("RUNZERO_BRIDGE_TOKEN is not set", err.getvalue())


class TestBridgeClientSendsToken(unittest.TestCase):
    def _captured_headers(self, env: dict[str, str]) -> dict[str, str]:
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        with patch.dict(os.environ, env), patch("urllib.request.urlopen", return_value=response) as urlopen:
            BridgeVMDriver("orbstack-vm", bridge_url="http://bridge")._request("POST", "/x", {"a": 1})
        return {k.lower(): v for k, v in urlopen.call_args.args[0].header_items()}

    def test_token_sent_when_configured(self):
        self.assertEqual(self._captured_headers({"RUNZERO_BRIDGE_TOKEN": "abc"}).get("authorization"), "Bearer abc")

    def test_no_header_without_token(self):
        self.assertNotIn("authorization", self._captured_headers({"RUNZERO_BRIDGE_TOKEN": ""}))


if __name__ == "__main__":
    unittest.main()
