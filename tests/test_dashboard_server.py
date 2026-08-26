import json
import os
import shutil
import signal
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import dashboard.server
from dashboard.server import DashboardRequestHandler, DashboardServer
from dashboard.state import DashboardState, dashboard_state


class TestDashboardState(unittest.TestCase):
    def setUp(self):
        self.state = DashboardState(max_log_lines=50)

    def test_append_log(self):
        self.state.append_log("Test log line 1")
        self.assertEqual(len(self.state.log_buffer), 1)
        entry = self.state.log_buffer[0]
        self.assertEqual(entry["message"], "Test log line 1")
        self.assertTrue("timestamp" in entry)

    def test_routing_stats(self):
        self.state.record_routing_decision("docker")
        self.state.record_routing_decision("orbstack-vm", "services")
        self.state.record_routing_decision("orbstack-vm", "dind")
        self.state.record_routing_decision("orbstack-vm", "browser")
        self.state.record_routing_decision("orbstack-vm", "e2e")
        self.state.record_routing_decision("orbstack-vm", "systemd")
        self.state.record_routing_decision("orbstack-vm", "custom")

        self.assertEqual(self.state.routing_stats["docker_jobs"], 1)
        self.assertEqual(self.state.routing_stats["vm_jobs"], 6)
        self.assertEqual(self.state.routing_stats["vm_triggers_breakdown"]["services"], 1)
        self.assertEqual(self.state.routing_stats["vm_triggers_breakdown"]["dind"], 1)
        self.assertEqual(self.state.routing_stats["vm_triggers_breakdown"]["browser"], 1)
        self.assertEqual(self.state.routing_stats["vm_triggers_breakdown"]["e2e"], 1)
        self.assertEqual(self.state.routing_stats["vm_triggers_breakdown"]["systemd"], 1)
        self.assertEqual(self.state.routing_stats["vm_triggers_breakdown"]["custom_label"], 1)

    def test_update_fleet_and_snapshot(self):
        mock_runner = MagicMock()
        mock_runner.to_dict.return_value = {
            "id": "r1",
            "name": "r1",
            "status": "running",
            "state": "running",
            "target_repo": "owner/repo",
            "target_arch": "arm64",
            "backend": "docker",
            "created_at": 1000.0
        }
        self.state.update_fleet(
            runners=[mock_runner],
            rate_limit=4800,
            queued_jobs=[{"repo": "owner/repo", "name": "build"}],
            monitored_repos=["owner/repo"],
            available_drivers=["docker", "orbstack-vm"],
            default_engine="docker",
            version="0.1.0"
        )
        snapshot = self.state.get_snapshot()
        self.assertEqual(snapshot["github"]["rate_limit_remaining"], 4800)
        self.assertEqual(snapshot["github"]["queued_jobs_count"], 1)
        self.assertEqual(len(snapshot["runners"]), 1)
        self.assertEqual(snapshot["default_engine"], "docker")
        self.assertIn("uptime", snapshot)


class TestDashboardStateGaps(unittest.TestCase):
    """Covers error/edge paths in DashboardState not exercised by TestDashboardState above."""

    def setUp(self):
        self.state = DashboardState(max_log_lines=50)
        self.temp_cache = tempfile.mkdtemp()
        self.state.cache_dir = self.temp_cache

    def tearDown(self):
        shutil.rmtree(self.temp_cache, ignore_errors=True)

    def test_append_log_blank_line_is_noop(self):
        self.state.append_log("   ")
        self.assertEqual(len(self.state.log_buffer), 0)

    def test_append_log_removes_dead_subscriber_on_full_queue(self):
        q = self.state.subscribe()
        for _ in range(100):  # fill the queue to its maxsize=100
            q.put_nowait({"type": "log", "data": {}})
        self.state.append_log("triggers dead-subscriber cleanup")
        self.assertNotIn(q, self.state.subscribers)

    def test_broadcast_state_removes_dead_subscriber_on_full_queue(self):
        q = self.state.subscribe()
        for _ in range(100):
            q.put_nowait({"type": "state", "data": {}})
        self.state.broadcast_state()
        self.assertNotIn(q, self.state.subscribers)

    def test_update_fleet_accepts_plain_dict_runner(self):
        self.state.update_fleet(
            runners=[{"id": "r1", "name": "r1", "status": "running", "state": "running"}],
            rate_limit=5000, queued_jobs=[], monitored_repos=[], available_drivers=["docker"]
        )
        self.assertEqual(self.state.active_runners[0]["id"], "r1")
        # No created_at on the dict -> falls back to "active".
        self.assertEqual(self.state.active_runners[0]["duration"], "active")

    def test_update_fleet_accepts_arbitrary_object_runner(self):
        class Plain:
            def __str__(self):
                return "weird-runner"

        self.state.update_fleet(
            runners=[Plain()], rate_limit=5000, queued_jobs=[], monitored_repos=[], available_drivers=["docker"]
        )
        self.assertEqual(self.state.active_runners[0]["id"], "weird-runner")

    def test_format_bytes_scales_through_kb_mb_gb(self):
        self.assertEqual(self.state._format_bytes(500), "500 B")
        self.assertIn("KB", self.state._format_bytes(2048))
        self.assertIn("MB", self.state._format_bytes(5 * 1024 ** 2))
        self.assertIn("GB", self.state._format_bytes(3 * 1024 ** 3))

    def test_get_dir_size_walks_real_files(self):
        sub = os.path.join(self.temp_cache, "npm")
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "file.txt"), "wb") as f:
            f.write(b"x" * 100)
        size = self.state._get_dir_size(sub)
        self.assertEqual(size, 100)

    def test_get_dir_size_swallows_walk_errors(self):
        with patch("os.walk", side_effect=OSError("permission denied")):
            size = self.state._get_dir_size(self.temp_cache)
        self.assertEqual(size, 0)

    def test_clean_cache_all_recreates_every_mapped_dir(self):
        npm_dir = os.path.join(self.temp_cache, "npm")
        os.makedirs(npm_dir, exist_ok=True)
        with open(os.path.join(npm_dir, "leftover.txt"), "w") as f:
            f.write("data")
        result = self.state.clean_cache("all")
        self.assertIn("npm", result["cleared"])
        self.assertTrue(os.path.isdir(npm_dir))
        self.assertEqual(os.listdir(npm_dir), [])

    def test_clean_cache_specific_category(self):
        pip_dir = os.path.join(self.temp_cache, "pip")
        os.makedirs(pip_dir, exist_ok=True)
        with open(os.path.join(pip_dir, "leftover.whl"), "w") as f:
            f.write("data")
        result = self.state.clean_cache("pip")
        self.assertEqual(result["cleared"], ["pip"])
        self.assertTrue(os.path.isdir(pip_dir))
        self.assertEqual(os.listdir(pip_dir), [])


class TestDashboardServer(unittest.TestCase):
    def setUp(self):
        self.server = DashboardServer(host="127.0.0.1", port=0)
        self.server.start(blocking=False)
        self.port = self.server.httpd.server_port
        self.base_url = f"http://127.0.0.1:{self.port}"

    def tearDown(self):
        self.server.stop()

    def test_serve_index_html(self):
        req = urllib.request.Request(f"{self.base_url}/")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            content = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("RunZero", content)
            self.assertIn("text/html", resp.headers.get("Content-Type", ""))

    def test_serve_css(self):
        req = urllib.request.Request(f"{self.base_url}/dashboard.css")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            content = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("--bg-base", content)
            self.assertIn("text/css", resp.headers.get("Content-Type", ""))

    def test_serve_js(self):
        req = urllib.request.Request(f"{self.base_url}/dashboard.js")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            content = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("connectSSE", content)
            self.assertIn("javascript", resp.headers.get("Content-Type", ""))

    def test_serve_font(self):
        req = urllib.request.Request(f"{self.base_url}/fonts/jetbrains-mono-400.woff2")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = resp.read()
            self.assertEqual(resp.status, 200)
            self.assertGreater(len(data), 1000)
            self.assertEqual(resp.headers.get("Content-Type"), "font/woff2")

    def test_sse_stream_does_not_block_other_requests(self):
        # Regression test: plain HTTPServer handles one request at a time,
        # and /api/events runs an infinite loop for the life of the
        # connection -- confirmed live, opening this endpoint permanently
        # wedged the server, so the container's OWN healthcheck against
        # /api/status could never be answered again (curl connected, then
        # hung until the 5s healthcheck timeout, forever). ThreadingHTTPServer
        # fixes this; this test would have failed (timed out) before that fix.
        sse_req = urllib.request.Request(f"{self.base_url}/api/events")
        sse_resp = urllib.request.urlopen(sse_req, timeout=10.0)
        self.addCleanup(sse_resp.close)
        # Read the initial event so we know the handler is actually inside
        # its streaming loop, not just mid-connect.
        first_line = sse_resp.readline()
        self.assertTrue(first_line.startswith(b"event:"))

        status_req = urllib.request.Request(f"{self.base_url}/api/status")
        with urllib.request.urlopen(status_req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)

    def test_api_status(self):
        req = urllib.request.Request(f"{self.base_url}/api/status")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(resp.status, 200)
            self.assertIn("concurrency", data)
            self.assertIn("github", data)

    def test_api_logs(self):
        dashboard_state.append_log("Hello server log")
        req = urllib.request.Request(f"{self.base_url}/api/logs")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(resp.status, 200)
            self.assertIn("logs", data)

    def test_action_clean_cache(self):
        payload = json.dumps({"category": "npm"}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/actions/clean-cache",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(resp.status, 200)
            self.assertEqual(data.get("status"), "success")

    @patch("drivers.get_available_drivers")
    def test_action_prune(self, mock_get_avail):
        mock_driver = MagicMock()
        mock_driver.list_runners.return_value = []
        mock_get_avail.return_value = {"docker": mock_driver}

        payload = b"{}"
        req = urllib.request.Request(
            f"{self.base_url}/api/actions/prune",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(resp.status, 200)
            self.assertEqual(data.get("status"), "success")
            mock_driver.prune_exited.assert_called_once()

    @patch("drivers.get_available_drivers")
    def test_action_prune_exception_returns_500(self, mock_get_avail):
        mock_get_avail.side_effect = RuntimeError("driver discovery failed")
        req = urllib.request.Request(
            f"{self.base_url}/api/actions/prune",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    def test_unknown_get_path_returns_404(self):
        req = urllib.request.Request(f"{self.base_url}/nonexistent")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 404)

    def test_unknown_post_path_returns_404(self):
        req = urllib.request.Request(f"{self.base_url}/nonexistent", data=b"{}", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 404)

    def test_serve_font_404_for_missing_file(self):
        req = urllib.request.Request(f"{self.base_url}/fonts/does-not-exist.woff2")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 404)

    def test_options_preflight(self):
        req = urllib.request.Request(f"{self.base_url}/api/status", method="OPTIONS")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 204)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")
            self.assertIn("GET", resp.headers.get("Access-Control-Allow-Methods", ""))

    def test_malformed_json_body_defaults_to_empty(self):
        req = urllib.request.Request(
            f"{self.base_url}/api/actions/clean-cache",
            data=b"not valid json{{{",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(resp.status, 200)
            # _read_json() swallowed the bad body -> defaults category to "all".
            self.assertEqual(data.get("status"), "success")

    def test_post_with_no_body_defaults_to_empty_dict(self):
        # _read_json() with Content-Length 0 (no body at all, not even "{}")
        # must return {} rather than erroring.
        req = urllib.request.Request(
            f"{self.base_url}/api/actions/clean-cache",
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(resp.status, 200)
            self.assertEqual(data.get("status"), "success")

    def test_debug_log_message_does_not_crash(self):
        with patch.dict("os.environ", {"RUNZERO_DEBUG": "true"}):
            req = urllib.request.Request(f"{self.base_url}/api/status")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                self.assertEqual(resp.status, 200)

    def test_sse_stream_delivers_a_real_log_event(self):
        # Regression coverage for the SSE loop's actual-message branch (not
        # just the heartbeat-on-timeout branch already covered elsewhere):
        # push a real log line while a client is connected and confirm it
        # arrives as an "event: log" frame.
        sse_req = urllib.request.Request(f"{self.base_url}/api/events")
        sse_resp = urllib.request.urlopen(sse_req, timeout=10.0)
        self.addCleanup(sse_resp.close)
        first_line = sse_resp.readline()
        self.assertTrue(first_line.startswith(b"event:"))

        dashboard_state.append_log("a real SSE-delivered log line")

        # Read forward until we see the log event (skip the blank line
        # terminating the initial "state" frame).
        found = False
        for _ in range(10):
            line = sse_resp.readline()
            if line.startswith(b"event: log"):
                found = True
                break
        self.assertTrue(found)

    def test_serve_file_500_on_read_error(self):
        # _serve_file()'s exception branch: the file exists (os.path.isfile
        # is real and true for index.html) but open() itself fails.
        mock_handler = MagicMock()
        with patch("builtins.open", side_effect=OSError("disk read error")):
            DashboardRequestHandler._serve_file(mock_handler, "index.html", "text/html; charset=utf-8")
        mock_handler.send_response.assert_called_once_with(500)
        mock_handler.wfile.write.assert_called_once()


class TestDashboardServerLifecycle(unittest.TestCase):
    @patch("dashboard.server.ThreadingHTTPServer")
    def test_start_blocking_stops_cleanly_on_keyboard_interrupt(self, mock_server_cls):
        mock_httpd = MagicMock()
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt()
        mock_server_cls.return_value = mock_httpd

        server = DashboardServer(host="127.0.0.1", port=0)
        server.start(blocking=True)

        mock_httpd.shutdown.assert_called_once()
        mock_httpd.server_close.assert_called_once()

    def test_stop_joins_still_alive_serving_thread(self):
        # stop()'s thread.join() only fires if the serving thread is still
        # alive at the moment shutdown() returns -- in real runs that race
        # usually loses (the thread has already unwound), so it's exercised
        # directly here with a fake thread pinned to is_alive()=True.
        server = DashboardServer(host="127.0.0.1", port=0)
        server.httpd = MagicMock()
        server._is_running = True
        server.thread = MagicMock()
        server.thread.is_alive.return_value = True

        server.stop()

        server.thread.join.assert_called_once_with(timeout=2.0)

    @patch("dashboard.server.signal.signal")
    @patch("dashboard.server.DashboardServer")
    def test_main_starts_server_and_signal_handler_stops_it(self, mock_server_cls, mock_signal):
        mock_server = MagicMock()
        mock_server_cls.return_value = mock_server
        captured_handlers = {}

        def capture(sig, handler):
            captured_handlers[sig] = handler

        mock_signal.side_effect = capture

        with patch("dashboard.server.sys.exit") as mock_exit:
            dashboard.server.main()

            mock_server.start.assert_called_once_with(blocking=True)
            self.assertIn(signal.SIGINT, captured_handlers)
            self.assertIn(signal.SIGTERM, captured_handlers)

            captured_handlers[signal.SIGINT](signal.SIGINT, None)
            mock_server.stop.assert_called_once()
            mock_exit.assert_called_once_with(0)
