"""
Blackbox / process-boundary contract tests for the Host VM Bridge HTTP API (issue #18).

Same three-layer split documented in tests/test_blackbox_dashboard.py's module
docstring applies here:

  1. White-box unit tests (tests/test_vm_bridge.py) -- pin specific
     implementation bugs (the driver-instance caching regression, the
     build-base non-blocking regression, individual error branches).

  2. THIS FILE -- blackbox contract tests. Every route registered in
     vm_bridge.py's do_GET/do_POST is walked exactly once with a real
     `urllib` HTTP client against a REAL ThreadingHTTPServer bound to an
     ephemeral local port. Per issue #18's own scope: the real driver's
     underlying `orbctl`/subprocess calls ARE mocked (no real OrbStack VM or
     Docker container is created here -- that's #10/#14's job), but the HTTP
     transport itself -- request in, JSON out, over a real socket -- is
     never faked or called in-process.

  3. tests/test_e2e_docker.py (issue #14) -- true end-to-end tests against a
     real external pipeline. Not this file's concern.

No external dependencies are needed (one free local port, no real GitHub/
Docker/VM access), so these run unconditionally as part of default
`pytest`/`unittest discover` collection.
"""

import json
import unittest
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import vm_bridge
from drivers import RunnerInfo
from vm_bridge import VMBridgeServer


class TestVMBridgeBlackboxContract(unittest.TestCase):
    """Hits every registered VM Bridge route over a real socket; drivers mocked underneath only."""

    def setUp(self):
        # _driver_cache is a module-level global (see vm_bridge.py's own
        # comment on why it exists) shared across the whole test process --
        # clear it so a mock installed by one test can't leak into another
        # via a stale cached instance.
        vm_bridge._driver_cache.clear()
        self.server = VMBridgeServer(host="127.0.0.1", port=0)
        self.server.start(blocking=False)
        self.port = self.server.httpd.server_port
        self.base_url = f"http://127.0.0.1:{self.port}"

    def tearDown(self):
        self.server.stop()

    # -- GET routes ------------------------------------------------------

    @patch("vm_bridge.get_available_drivers")
    def test_root_and_health_aliases_contract(self, mock_get_available):
        mock_get_available.return_value = {"docker": MagicMock()}
        for path in ("/", "/health", "/api/health"):
            with self.subTest(path=path), urllib.request.urlopen(f"{self.base_url}{path}", timeout=3.0) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data.get("status"), "ok")
                self.assertEqual(data.get("service"), "runzero-vm-bridge")
                self.assertIn("available_vm_drivers", data)

    @patch("vm_bridge.get_available_drivers")
    def test_api_status_route_contract(self, mock_get_available):
        mock_get_available.return_value = {"docker": MagicMock()}
        with urllib.request.urlopen(f"{self.base_url}/api/status", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertIn("available_drivers", data)

    @patch("vm_bridge.get_driver")
    def test_get_driver_runners_route_contract(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.list_runners.return_value = [
            RunnerInfo(
                id="vm-contract-1", name="vm-contract-1", status="running", state="running",
                target_repo="owner/repo", target_arch="arm64", backend="orbstack-vm",
            )
        ]
        mock_get_driver.return_value = mock_driver

        with urllib.request.urlopen(f"{self.base_url}/api/drivers/orbstack-vm/runners", timeout=3.0) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("driver"), "orbstack-vm")
            self.assertEqual(len(data.get("runners")), 1)
            self.assertEqual(data["runners"][0]["id"], "vm-contract-1")

    # -- POST routes -------------------------------------------------------

    def _post(self, path, body):
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urllib.request.urlopen(req, timeout=5.0)

    @patch("vm_bridge.get_driver")
    def test_spawn_route_contract(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.spawn_runner.return_value = "runzero-vm-contract-spawned"
        mock_get_driver.return_value = mock_driver

        with self._post("/api/drivers/orbstack-vm/spawn", {"repo": "owner/repo", "arch": "arm64"}) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            self.assertEqual(data.get("runner_id"), "runzero-vm-contract-spawned")

    @patch("vm_bridge.get_driver")
    def test_prune_route_contract(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        runner = {
            "id": "vm-1", "name": "vm-1", "status": "exited", "state": "exited",
            "target_repo": "o/r", "target_arch": "arm64", "backend": "orbstack-vm",
        }
        with self._post("/api/drivers/orbstack-vm/prune", {"runners": [runner]}) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            mock_driver.prune_exited.assert_called_once()

    @patch("vm_bridge.get_driver")
    def test_destroy_route_contract(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.destroy_runner.return_value = True
        mock_get_driver.return_value = mock_driver

        with self._post("/api/drivers/orbstack-vm/destroy", {"runner_id": "vm-contract-123"}) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            self.assertTrue(data.get("destroyed"))

    @patch("vm_bridge.get_driver")
    def test_cleanup_route_contract(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        with self._post("/api/drivers/orbstack-vm/cleanup", {}) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            mock_driver.cleanup_all.assert_called_once()

    @patch("vm_bridge.get_driver")
    def test_ensure_base_stopped_route_contract(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        with self._post("/api/drivers/orbstack-vm/ensure-base-stopped", {}) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            mock_driver.ensure_base_images_stopped.assert_called_once()

    @patch("vm_bridge.get_driver")
    def test_build_base_route_contract(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.build_base_image.return_value = True
        mock_get_driver.return_value = mock_driver

        with self._post("/api/drivers/orbstack-vm/build-base", {"arch": "arm64"}) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            self.assertTrue(data.get("built"))

    # -- Cross-cutting: CORS preflight + unknown routes ----------------------

    def test_options_preflight_contract(self):
        req = urllib.request.Request(f"{self.base_url}/api/drivers/orbstack-vm/spawn", method="OPTIONS")
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
