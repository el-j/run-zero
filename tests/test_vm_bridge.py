import json
import signal
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import vm_bridge
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

    def test_options_preflight(self):
        req = urllib.request.Request(f"{self.base_url}/api/drivers/orbstack-vm/spawn", method="OPTIONS")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            self.assertEqual(resp.status, 204)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")

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

    def test_malformed_json_body_defaults_to_empty(self):
        # _read_json() must swallow a JSONDecodeError and behave as if no
        # body was sent, not raise / 500.
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/cleanup",
            data=b"not valid json{{{",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with patch("vm_bridge.get_driver", return_value=MagicMock()), urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")

    @patch("vm_bridge.get_driver")
    def test_get_runners_endpoint_invalid_driver_returns_500(self, mock_get_driver):
        mock_get_driver.side_effect = ValueError("Unknown runner backend driver: 'bogus'")
        req = urllib.request.Request(f"{self.base_url}/api/drivers/bogus/runners")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    @patch("vm_bridge.get_driver")
    def test_post_invalid_driver_returns_400(self, mock_get_driver):
        mock_get_driver.side_effect = ValueError("Unknown runner backend driver: 'bogus'")
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/bogus/spawn",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 400)

    @patch("vm_bridge.get_driver")
    def test_spawn_endpoint_driver_exception_returns_500(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.spawn_runner.side_effect = RuntimeError("boom")
        mock_get_driver.return_value = mock_driver
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/spawn",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    @patch("vm_bridge.get_driver")
    def test_prune_endpoint_driver_exception_returns_500(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.prune_exited.side_effect = RuntimeError("boom")
        mock_get_driver.return_value = mock_driver
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/prune",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    @patch("vm_bridge.get_driver")
    def test_destroy_endpoint_missing_runner_id_returns_400(self, mock_get_driver):
        mock_get_driver.return_value = MagicMock()
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/destroy",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 400)

    @patch("vm_bridge.get_driver")
    def test_destroy_endpoint_driver_exception_returns_500(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.destroy_runner.side_effect = RuntimeError("boom")
        mock_get_driver.return_value = mock_driver
        payload = json.dumps({"runner_id": "vm-1"}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/destroy",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    @patch("vm_bridge.get_driver")
    def test_cleanup_endpoint_driver_exception_returns_500(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.cleanup_all.side_effect = RuntimeError("boom")
        mock_get_driver.return_value = mock_driver
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/cleanup",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    @patch("vm_bridge.get_driver")
    def test_ensure_base_stopped_endpoint_success(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_get_driver.return_value = mock_driver
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/ensure-base-stopped",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            mock_driver.ensure_base_images_stopped.assert_called_once()

    @patch("vm_bridge.get_driver")
    def test_ensure_base_stopped_endpoint_exception_returns_500(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.ensure_base_images_stopped.side_effect = RuntimeError("boom")
        mock_get_driver.return_value = mock_driver
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/ensure-base-stopped",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    @patch("vm_bridge.get_driver")
    def test_build_base_endpoint_unsupported_driver_returns_400(self, mock_get_driver):
        # A driver without build_base_image (e.g. DockerDriver) must yield a
        # clean 400, not a 500/attribute error.
        mock_driver = MagicMock()
        del mock_driver.build_base_image
        mock_get_driver.return_value = mock_driver
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/docker/build-base",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 400)

    @patch("vm_bridge.get_driver")
    def test_build_base_endpoint_exception_returns_500(self, mock_get_driver):
        mock_driver = MagicMock()
        mock_driver.build_base_image.side_effect = RuntimeError("boom")
        mock_get_driver.return_value = mock_driver
        req = urllib.request.Request(
            f"{self.base_url}/api/drivers/orbstack-vm/build-base",
            data=b"{}", headers={"Content-Type": "application/json"}, method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=3.0)
        self.assertEqual(cm.exception.code, 500)

    def test_debug_log_message_does_not_crash(self):
        # RUNZERO_DEBUG=true switches log_message() to actually write to
        # stderr -- must not error, and every request triggers it via the
        # base handler's own request logging.
        with patch.dict("os.environ", {"RUNZERO_DEBUG": "true"}), \
             patch("vm_bridge.get_available_drivers", return_value={}):
            req = urllib.request.Request(f"{self.base_url}/health")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                self.assertEqual(resp.status, 200)


class TestVMBridgeServerLifecycle(unittest.TestCase):
    @patch("vm_bridge.ThreadingHTTPServer")
    def test_start_blocking_stops_cleanly_on_keyboard_interrupt(self, mock_server_cls):
        mock_httpd = MagicMock()
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt()
        mock_server_cls.return_value = mock_httpd

        server = VMBridgeServer(host="127.0.0.1", port=0)
        server.start(blocking=True)

        mock_httpd.shutdown.assert_called_once()
        mock_httpd.server_close.assert_called_once()

    def test_stop_joins_still_alive_serving_thread(self):
        # stop()'s thread.join() only fires if the serving thread is still
        # alive at the moment shutdown() returns -- in real runs that race
        # usually loses (the thread has already unwound), so it's exercised
        # directly here with a fake thread pinned to is_alive()=True.
        server = VMBridgeServer(host="127.0.0.1", port=0)
        server.httpd = MagicMock()
        server._is_running = True
        server.thread = MagicMock()
        server.thread.is_alive.return_value = True

        server.stop()

        server.thread.join.assert_called_once_with(timeout=2.0)

    @patch("vm_bridge.signal.signal")
    @patch("vm_bridge.VMBridgeServer")
    def test_main_starts_server_and_signal_handler_stops_it(self, mock_server_cls, mock_signal):
        mock_server = MagicMock()
        mock_server_cls.return_value = mock_server
        captured_handlers = {}

        def capture(sig, handler):
            captured_handlers[sig] = handler

        mock_signal.side_effect = capture

        with patch("vm_bridge.sys.exit") as mock_exit:
            vm_bridge.main()

            mock_server.start.assert_called_once_with(blocking=True)
            self.assertIn(signal.SIGINT, captured_handlers)
            self.assertIn(signal.SIGTERM, captured_handlers)

            captured_handlers[signal.SIGINT](signal.SIGINT, None)
            mock_server.stop.assert_called_once()
            mock_exit.assert_called_once_with(0)

    def test_send_json_swallows_broken_pipe(self):
        # A client that disconnects mid-response must not blow up the
        # handler -- _send_json() swallows BrokenPipeError/ConnectionResetError.
        mock_self = MagicMock()
        mock_self.wfile.write.side_effect = BrokenPipeError()
        # Calling the unbound method directly against a mock avoids needing
        # a real socket/connection for this handler instance.
        vm_bridge.VMBridgeRequestHandler._send_json(mock_self, 200, {"status": "ok"})
        mock_self.wfile.write.assert_called_once()


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


class TestBridgeVMDriverDirectUnit(unittest.TestCase):
    """Unit tests for BridgeVMDriver methods with `_request` mocked directly
    (no real HTTP server involved), covering methods the e2e-style
    TestBridgeVMDriver above doesn't exercise on its own."""

    def setUp(self):
        self.driver = BridgeVMDriver("orbstack-vm", bridge_url="http://127.0.0.1:1")

    @patch.object(BridgeVMDriver, "_request")
    def test_spawn_runner_returns_none_on_bridge_failure(self, mock_request):
        mock_request.return_value = {"error": "connection refused"}
        self.assertIsNone(self.driver.spawn_runner(repo="owner/repo", arch="arm64"))

    @patch.object(BridgeVMDriver, "_request")
    def test_destroy_runner_true(self, mock_request):
        mock_request.return_value = {"destroyed": True}
        self.assertTrue(self.driver.destroy_runner("vm-123"))
        mock_request.assert_called_once_with(
            "POST", "/api/drivers/orbstack-vm/destroy", data={"runner_id": "vm-123"}, timeout=30.0
        )

    @patch.object(BridgeVMDriver, "_request")
    def test_destroy_runner_false_on_bridge_failure(self, mock_request):
        mock_request.return_value = {"error": "connection refused"}
        self.assertFalse(self.driver.destroy_runner("vm-123"))

    @patch.object(BridgeVMDriver, "_request")
    def test_prune_exited_posts_serialized_runners(self, mock_request):
        mock_request.return_value = {}
        runners = [
            RunnerInfo(id="vm-1", name="vm-1", status="stopped", state="exited", target_repo="o/r", target_arch="arm64", backend="orbstack-vm")
        ]
        self.driver.prune_exited(runners)
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "/api/drivers/orbstack-vm/prune")
        self.assertEqual(len(kwargs["data"]["runners"]), 1)

    @patch.object(BridgeVMDriver, "_request")
    def test_ensure_base_images_stopped_posts_to_bridge(self, mock_request):
        mock_request.return_value = {}
        self.driver.ensure_base_images_stopped()
        mock_request.assert_called_once_with(
            "POST", "/api/drivers/orbstack-vm/ensure-base-stopped", timeout=15.0
        )

    @patch.object(BridgeVMDriver, "_request")
    def test_build_base_image_true(self, mock_request):
        mock_request.return_value = {"built": True}
        self.assertTrue(self.driver.build_base_image("amd64"))
        mock_request.assert_called_once_with(
            "POST", "/api/drivers/orbstack-vm/build-base", data={"arch": "amd64"}, timeout=300.0
        )

    @patch.object(BridgeVMDriver, "_request")
    def test_build_base_image_false_on_bridge_failure(self, mock_request):
        mock_request.return_value = {"error": "timeout"}
        self.assertFalse(self.driver.build_base_image("amd64"))
