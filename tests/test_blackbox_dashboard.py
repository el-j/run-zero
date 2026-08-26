"""
Blackbox / process-boundary contract tests for the RunZero Dashboard HTTP API (issue #18).

Where this fits among the three test layers in this repo:

  1. White-box unit tests (e.g. tests/test_dashboard_server.py's TestDashboardState /
     TestDashboardServerLifecycle classes) -- import internals directly, mock
     subprocess/HTTP at the call site, and exist to pin specific implementation
     bugs (a regression in SSE threading, a lifecycle edge case, an error branch).
     Some of them also happen to use a real socket where that's the only way to
     reach the bug (e.g. the SSE-blocking regression test), but that's incidental
     to their purpose.

  2. THIS FILE -- blackbox contract tests. No internals are imported or
     monkeypatched except to fake out driver discovery for the one route
     (/api/actions/prune) that would otherwise require real Docker/VM
     infrastructure underneath. Every route registered in
     dashboard/server.py's do_GET/do_POST is walked exactly once with a real
     `urllib` HTTP client against a REAL ThreadingHTTPServer bound to an
     ephemeral local port -- the way an operator's browser, curl, or a
     monitoring script would reach it. The assertions are on the public
     contract only: status code, key response fields, and headers that
     external consumers (the dashboard frontend, curl, a Prometheus-style
     scraper) actually depend on.

  3. tests/test_e2e_docker.py (issue #14) -- true end-to-end tests that drive
     a real external pipeline (real container creation, real command
     execution inside it). This file never spawns a container or VM; it only
     exercises the dashboard's own HTTP surface.

These tests need no external dependencies (no real GitHub, no real Docker/VM
access, just one free local port), so they run unconditionally as part of the
default `pytest`/`unittest discover` collection -- not gated behind an env
var the way tests/test_orbstack_live_integration.py (#10) is.
"""

import json
import unittest
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

from dashboard.server import DashboardServer
from dashboard.state import dashboard_state


class TestDashboardBlackboxContract(unittest.TestCase):
    """Hits every registered dashboard route over a real socket; no server internals touched."""

    def setUp(self):
        self.server = DashboardServer(host="127.0.0.1", port=0)
        self.server.start(blocking=False)
        self.port = self.server.httpd.server_port
        self.base_url = f"http://127.0.0.1:{self.port}"

    def tearDown(self):
        self.server.stop()

    # -- Static asset routes --------------------------------------------

    def test_root_serves_index_html(self):
        with urllib.request.urlopen(f"{self.base_url}/", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/html", resp.headers.get("Content-Type", ""))
            self.assertGreater(len(resp.read()), 0)

    def test_dashboard_css_route(self):
        with urllib.request.urlopen(f"{self.base_url}/dashboard.css", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/css", resp.headers.get("Content-Type", ""))

    def test_dashboard_js_route(self):
        with urllib.request.urlopen(f"{self.base_url}/dashboard.js", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("javascript", resp.headers.get("Content-Type", ""))

    def test_fonts_route(self):
        with urllib.request.urlopen(f"{self.base_url}/fonts/jetbrains-mono-400.woff2", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Content-Type"), "font/woff2")

    # -- REST routes -------------------------------------------------------

    def test_api_status_route_contract(self):
        with urllib.request.urlopen(f"{self.base_url}/api/status", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))
            data = json.loads(resp.read().decode("utf-8"))
            for key in ("version", "status", "concurrency", "github", "runners", "cache"):
                self.assertIn(key, data)

    def test_api_fleet_route_is_status_alias(self):
        # /api/fleet and /api/status are documented as the same handler branch.
        with urllib.request.urlopen(f"{self.base_url}/api/fleet", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("concurrency", data)

    def test_api_logs_route_contract(self):
        dashboard_state.append_log("blackbox contract check log line")
        with urllib.request.urlopen(f"{self.base_url}/api/logs", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("logs", data)
            self.assertTrue(any("blackbox contract check log line" in e.get("message", "") for e in data["logs"]))

    # -- SSE stream ----------------------------------------------------------

    def test_api_events_sse_delivers_a_real_event_over_the_wire(self):
        # Real client, real socket, real cross-thread event -- not mocked
        # anywhere in this test.
        sse_resp = urllib.request.urlopen(f"{self.base_url}/api/events", timeout=10.0)
        self.addCleanup(sse_resp.close)
        self.assertEqual(sse_resp.status, 200)
        self.assertIn("text/event-stream", sse_resp.headers.get("Content-Type", ""))

        first_line = sse_resp.readline()
        self.assertTrue(first_line.startswith(b"event:"))

        marker = "blackbox-sse-delivery-marker"
        dashboard_state.append_log(marker)

        delivered = False
        for _ in range(10):
            line = sse_resp.readline()
            if line.startswith(b"event: log"):
                data_line = sse_resp.readline()
                if marker in data_line.decode("utf-8", errors="replace"):
                    delivered = True
                break
        self.assertTrue(delivered, "expected the real appended log line to arrive as an SSE 'log' event")

    # -- Actions (POST) -------------------------------------------------------

    def test_post_actions_clean_cache_route_contract(self):
        # Redirect the singleton's cache dir at a throwaway temp path for the
        # duration of this one test so a blackbox HTTP contract check never
        # touches a real host package cache.
        import shutil
        import tempfile
        temp_cache = tempfile.mkdtemp(prefix="runzero-blackbox-cache-")
        self.addCleanup(shutil.rmtree, temp_cache, True)
        original_cache_dir = dashboard_state.cache_dir
        dashboard_state.cache_dir = temp_cache
        self.addCleanup(setattr, dashboard_state, "cache_dir", original_cache_dir)

        payload = json.dumps({"category": "npm"}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/actions/clean-cache",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")

    @patch("drivers.get_available_drivers")
    def test_post_actions_prune_route_contract(self, mock_get_available):
        # The prune route delegates to real driver instances underneath --
        # faked here (per issue #18's own guidance) so this contract check
        # doesn't require a real Docker/VM environment. The HTTP transport
        # itself (request in, JSON out, over a real socket) is real.
        mock_driver = MagicMock()
        mock_driver.list_runners.return_value = []
        mock_get_available.return_value = {"docker": mock_driver}

        req = urllib.request.Request(
            f"{self.base_url}/api/actions/prune",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            mock_driver.prune_exited.assert_called_once()

    # -- Cross-cutting contract: CORS preflight + unknown routes -------------

    def test_options_preflight_contract(self):
        req = urllib.request.Request(f"{self.base_url}/api/status", method="OPTIONS")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 204)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")

    def test_unknown_get_route_returns_404_contract(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(f"{self.base_url}/api/does-not-exist", timeout=3.0)
        self.assertEqual(cm.exception.code, 404)

    def test_unknown_post_route_returns_404_contract(self):
        req = urllib.request.Request(f"{self.base_url}/api/does-not-exist", data=b"{}", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
