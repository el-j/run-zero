import json
import unittest
import urllib.request
from unittest.mock import MagicMock, patch

from dashboard.server import DashboardServer
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
