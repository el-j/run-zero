"""
Unit tests for BridgeVMDriver client-side HTTP request logic.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from drivers.bridge_driver import BridgeVMDriver


class TestBridgeVMDriver(unittest.TestCase):
    def setUp(self):
        self.driver = BridgeVMDriver("orbstack-vm", bridge_url="http://localhost:49504")

    def test_name_returns_target_backend(self):
        self.assertEqual(self.driver.name(), "orbstack-vm")

    @patch("urllib.request.urlopen")
    def test_is_available_returns_true_when_backend_in_available_drivers(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"status": "ok", "available_vm_drivers": ["orbstack-vm", "multipass-vm"], "all_drivers": ["docker"]}
        ).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertTrue(self.driver.is_available())

    @patch("urllib.request.urlopen")
    def test_is_available_returns_true_when_backend_in_all_drivers(self, mock_urlopen):
        # Fallback when backend is not in available_vm_drivers but is in all_drivers
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "ok", "available_vm_drivers": [], "all_drivers": ["docker", "orbstack-vm"]}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertTrue(self.driver.is_available())

    @patch("urllib.request.urlopen")
    def test_is_available_returns_false_when_backend_not_in_either_list(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "ok", "available_vm_drivers": ["multipass-vm"], "all_drivers": ["docker"]}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertFalse(self.driver.is_available())

    @patch("urllib.request.urlopen")
    def test_is_available_returns_false_when_status_not_ok(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "error", "available_vm_drivers": ["orbstack-vm"]}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertFalse(self.driver.is_available())

    @patch("urllib.request.urlopen")
    def test_is_available_returns_false_on_network_error(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        self.assertFalse(self.driver.is_available())

    @patch("urllib.request.urlopen")
    def test_spawn_runner_returns_runner_id_on_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "success", "runner_id": "orbstack-runner-123"}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="token")

        self.assertEqual(result, "orbstack-runner-123")
        # Verify request was made to correct endpoint
        call_args = mock_urlopen.call_args
        self.assertIn("orbstack-vm/spawn", call_args[0][0].get_full_url())

    @patch("urllib.request.urlopen")
    def test_spawn_runner_returns_none_when_status_not_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"status": "error", "error": "Failed to spawn"}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="token")

        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_spawn_runner_returns_none_on_network_error(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Connection timeout")

        result = self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="token")

        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_destroy_runner_returns_true_when_destroyed_true(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"destroyed": True}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.destroy_runner("runner-id")

        self.assertTrue(result)

    @patch("urllib.request.urlopen")
    def test_destroy_runner_returns_false_when_destroyed_false(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"destroyed": False}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.destroy_runner("runner-id")

        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_destroy_runner_returns_false_when_destroyed_key_missing(self, mock_urlopen):
        # Key mutation target: bool(dict.get("destroyed", False)) returns False when key is missing
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.destroy_runner("runner-id")

        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_destroy_runner_returns_false_on_network_error(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Connection error")

        result = self.driver.destroy_runner("runner-id")

        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_build_base_image_returns_true_when_built_true(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"built": True}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.build_base_image(arch="arm64")

        self.assertTrue(result)

    @patch("urllib.request.urlopen")
    def test_build_base_image_returns_false_when_built_false(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"built": False}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.build_base_image(arch="arm64")

        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_build_base_image_returns_false_when_built_key_missing(self, mock_urlopen):
        # Key mutation target: bool(dict.get("built", False)) returns False when key is missing
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.build_base_image(arch="arm64")

        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    def test_list_runners_returns_empty_list_when_no_runners(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"runners": []}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.list_runners()

        self.assertEqual(result, [])

    @patch("urllib.request.urlopen")
    def test_list_runners_parses_runner_data(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {
                "runners": [
                    {
                        "id": "runner-1",
                        "name": "orbstack-runner-1",
                        "status": "online",
                        "state": "running",
                        "target_repo": "el-j/run-zero",
                        "target_arch": "arm64",
                        "backend": "orbstack-vm",
                        "created_at": 1234567890,
                    }
                ]
            }
        ).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.list_runners()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "runner-1")
        self.assertEqual(result[0].name, "orbstack-runner-1")
        self.assertEqual(result[0].target_arch, "arm64")

    @patch("urllib.request.urlopen")
    def test_list_runners_defaults_backend_to_target_backend(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {
                "runners": [
                    {
                        "id": "runner-1",
                        "name": "orbstack-runner-1",
                        "status": "online",
                        "state": "running",
                        "target_repo": "el-j/run-zero",
                        "target_arch": "arm64",
                        # Note: backend field is missing
                    }
                ]
            }
        ).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.list_runners()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].backend, "orbstack-vm")

    @patch("urllib.request.urlopen")
    def test_list_runners_returns_empty_when_runners_key_missing(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.driver.list_runners()

        self.assertEqual(result, [])

    @patch("urllib.request.urlopen")
    def test_prune_exited_sends_correct_payload(self, mock_urlopen):
        from drivers import RunnerInfo

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        runners = [RunnerInfo(id="1", name="r1", status="exited", state="exited", target_repo="repo", target_arch="arm64", backend="orbstack-vm")]
        self.driver.prune_exited(runners)

        # Verify the request was made
        call_args = mock_urlopen.call_args
        self.assertIn("prune", call_args[0][0].get_full_url())

    @patch("urllib.request.urlopen")
    def test_cleanup_all_sends_cleanup_request(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.driver.cleanup_all()

        # Verify cleanup endpoint was called
        call_args = mock_urlopen.call_args
        self.assertIn("cleanup", call_args[0][0].get_full_url())

    @patch("urllib.request.urlopen")
    def test_ensure_base_images_stopped_sends_request(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode("utf-8")
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.driver.ensure_base_images_stopped()

        # Verify ensure-base-stopped endpoint was called
        call_args = mock_urlopen.call_args
        self.assertIn("ensure-base-stopped", call_args[0][0].get_full_url())


if __name__ == "__main__":
    unittest.main()
