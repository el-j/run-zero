import json
import threading
import time
import unittest
import urllib.request
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from drivers.bridge_driver import BridgeVMDriver
from vm_bridge import VMBridgeServer


class TestVMBridge(unittest.TestCase):
    def setUp(self):
        # _get_cached_driver() memoizes across calls (that's the fix under
        # test in test_get_driver_is_cached_across_requests below) -- clear
        # it per-test so one test's @patch("vm_bridge.get_driver") mock
        # can't leak into another test via a stale cache hit.
        import vm_bridge
        vm_bridge._driver_cache.clear()

        # Start bridge on ephemeral port for testing
        self.server = VMBridgeServer(host="127.0.0.1", port=0)
        self.server.start(blocking=False)
        self.port = self.server.httpd.server_port
        self.base_url = f"http://127.0.0.1:{self.port}"

    def tearDown(self):
        self.server.stop()

    @patch("vm_bridge.get_driver")
    def test_get_driver_is_cached_across_requests(self, mock_get_driver):
        # Regression test: get_driver() builds a brand-new driver instance
        # every call, with no memory of a prior instance's state. The bridge
        # used to call it fresh on EVERY incoming HTTP request, silently
        # discarding OrbStackVMDriver's own _building_arches/_build_retry_after
        # backoff state between one request and the next. Confirmed live: the
        # containerized autoscaler polls the bridge every ~5s, so each poll
        # was served by a backoff-unaware instance that deleted and recreated
        # the golden-image staging VM roughly every 5 seconds, forever --
        # provisioning never survived long enough to finish. Two requests for
        # the same driver name must now return the SAME instance.
        mock_driver = MagicMock()
        mock_driver.list_runners.return_value = []
        mock_get_driver.return_value = mock_driver

        for _ in range(3):
            req = urllib.request.Request(f"{self.base_url}/api/drivers/orbstack-vm/runners")
            with urllib.request.urlopen(req, timeout=3.0):
                pass

        mock_get_driver.assert_called_once_with("orbstack-vm")
        self.assertEqual(mock_driver.list_runners.call_count, 3)

    @patch("vm_bridge.get_available_drivers")
    def test_health_endpoint(self, mock_drivers):
        mock_drivers.return_value = {"orbstack-vm": MagicMock()}
        req = urllib.request.Request(f"{self.base_url}/health")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertEqual(data.get("service"), "runzero-vm-bridge")
            self.assertIn("available_vm_drivers", data)

    @patch("vm_bridge.get_available_drivers")
    def test_status_endpoint(self, mock_drivers):
        mock_drivers.return_value = {"orbstack-vm": MagicMock()}
        req = urllib.request.Request(f"{self.base_url}/api/status")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ok")
            self.assertIn("available_drivers", data)

    @patch("vm_bridge.get_available_drivers")
    @patch("vm_bridge.get_driver")
    def test_build_base_does_not_block_other_requests(self, mock_get_driver, mock_get_available):
        # Regression test: "build-base" calls driver.build_base_image()
        # synchronously in the handler -- a real golden-image build takes
        # 15-25 minutes. With a single-threaded server that means every OTHER
        # bridge request (health, spawn, list, prune -- for every driver/
        # repo/arch) is unreachable for that whole window, defeating the
        # point of build_base_image()'s own internal async-thread design.
        # Simulated here with a short sleep so the test itself stays fast.
        def slow_build(arch):
            time.sleep(1.5)
            return True

        mock_driver = MagicMock()
        mock_driver.build_base_image.side_effect = slow_build
        mock_get_driver.return_value = mock_driver
        mock_get_available.return_value = {"orbstack-vm": mock_driver}

        def call_build_base():
            payload = json.dumps({"arch": "arm64"}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/drivers/orbstack-vm/build-base",
                data=payload, headers={"Content-Type": "application/json"}, method="POST"
            )
            urllib.request.urlopen(req, timeout=5.0)

        build_thread = threading.Thread(target=call_build_base, daemon=True)
        build_thread.start()
        time.sleep(0.3)  # let build-base actually enter the (mocked) blocking call

        req = urllib.request.Request(f"{self.base_url}/health")
        start = time.monotonic()
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            elapsed = time.monotonic() - start
            self.assertEqual(resp.status, 200)
        self.assertLess(elapsed, 1.0)

        build_thread.join(timeout=5.0)

    @patch("vm_bridge.get_driver")
    def test_list_runners_endpoint(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.list_runners.return_value = [
            RunnerInfo(id="vm-1", name="runzero-vm-1", status="running", state="running", target_repo="owner/repo", target_arch="arm64", backend="orbstack-vm")
        ]
        mock_get_driver.return_value = mock_driver

        req = urllib.request.Request(f"{self.base_url}/api/drivers/orbstack-vm/runners")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("driver"), "orbstack-vm")
            self.assertEqual(len(data.get("runners")), 1)
            self.assertEqual(data["runners"][0]["id"], "vm-1")

    @patch("vm_bridge.get_driver")
    def test_spawn_runner_endpoint(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.spawn_runner.return_value = "runzero-vm-new"
        mock_get_driver.return_value = mock_driver

        payload = json.dumps({"repo": "owner/repo", "arch": "arm64"}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/spawn",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            self.assertEqual(data.get("runner_id"), "runzero-vm-new")

    @patch("vm_bridge.get_driver")
    def test_prune_endpoint(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        payload = json.dumps({"runners": [{"id": "vm-1", "name": "vm-1", "status": "exited", "state": "exited", "target_repo": "r", "target_arch": "arm64", "backend": "orbstack-vm"}]}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/prune",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            mock_driver.prune_exited.assert_called_once()

    @patch("vm_bridge.get_driver")
    def test_destroy_endpoint(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.destroy_runner.return_value = True
        mock_get_driver.return_value = mock_driver

        payload = json.dumps({"runner_id": "vm-123"}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/destroy",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            self.assertTrue(data.get("destroyed"))
            mock_driver.destroy_runner.assert_called_once_with("vm-123")

    @patch("vm_bridge.get_driver")
    def test_cleanup_endpoint(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver

        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/cleanup",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            mock_driver.cleanup_all.assert_called_once()


class TestBridgeVMDriver(unittest.TestCase):
    def setUp(self):
        # See TestVMBridge.setUp's comment -- _driver_cache is a module-level
        # global shared by every test in this process, not scoped per test
        # class, so it must be cleared here too.
        import vm_bridge
        vm_bridge._driver_cache.clear()

        self.server = VMBridgeServer(host="127.0.0.1", port=0)
        self.server.start(blocking=False)
        self.port = self.server.httpd.server_port
        self.bridge_url = f"http://127.0.0.1:{self.port}"
        self.driver = BridgeVMDriver("orbstack-vm", bridge_url=self.bridge_url)

    def tearDown(self):
        self.server.stop()

    def test_driver_name(self):
        self.assertEqual(self.driver.name(), "orbstack-vm")

    @patch("vm_bridge.get_available_drivers")
    def test_is_available(self, mock_get_avail):
        mock_avail = MagicMock()
        mock_avail.name.return_value = "orbstack-vm"
        mock_get_avail.return_value = {"orbstack-vm": mock_avail}
        self.assertTrue(self.driver.is_available())

    def test_is_available_when_bridge_unreachable(self):
        unreachable = BridgeVMDriver("orbstack-vm", bridge_url="http://127.0.0.1:59999")
        self.assertFalse(unreachable.is_available())

    @patch("vm_bridge.get_driver")
    def test_spawn_runner(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.spawn_runner.return_value = "runzero-vm-spawned"
        mock_get_driver.return_value = mock_driver

        runner_id = self.driver.spawn_runner(repo="owner/repo", arch="arm64")
        self.assertEqual(runner_id, "runzero-vm-spawned")

    @patch("vm_bridge.get_driver")
    def test_list_runners(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.list_runners.return_value = [
            RunnerInfo(id="vm-x", name="vm-x", status="running", state="running", target_repo="o/r", target_arch="arm64", backend="orbstack-vm")
        ]
        mock_get_driver.return_value = mock_driver

        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].id, "vm-x")

    @patch("vm_bridge.get_driver")
    def test_destroy_and_cleanup(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.destroy_runner.return_value = True
        mock_get_driver.return_value = mock_driver

        self.assertTrue(self.driver.destroy_runner("vm-123"))
        self.driver.cleanup_all()
        mock_driver.cleanup_all.assert_called_once()
