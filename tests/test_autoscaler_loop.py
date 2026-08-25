"""
Unit tests for autoscaler main execution loop and signal handling.
"""

import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import autoscaler


class TestAutoscalerLoop(unittest.TestCase):
    def setUp(self):
        self.temp_cache = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_cache, ignore_errors=True)

    def test_get_target_architectures(self):
        with patch.object(autoscaler, "RUNNER_ARCH", "both"):
            self.assertEqual(autoscaler.get_target_architectures(), ["arm64", "amd64"])
        with patch.object(autoscaler, "RUNNER_ARCH", "amd64"):
            self.assertEqual(autoscaler.get_target_architectures(), ["amd64"])
        with patch.object(autoscaler, "RUNNER_ARCH", "arm64"):
            self.assertEqual(autoscaler.get_target_architectures(), ["arm64"])

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.HOST_CACHE_DIR")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.discover_repositories", return_value=["el-j/run-zero", "el-j/custom-repo"])
    @patch("autoscaler.reconcile_zombie_runners")
    @patch("autoscaler.get_queued_job_details")
    @patch("autoscaler.time.sleep")
    def test_main_loop_repository_mode(
        self, mock_sleep, mock_jobs, mock_reconcile, mock_discover, mock_cache_dir
    ):
        mock_cache_dir.return_value = self.temp_cache

        # Queue has 1 job for el-j/run-zero
        mock_jobs.side_effect = [
            [{"id": 1, "name": "unit-test", "labels": ["self-hosted"]}],
            []
        ]

        def stop_after_one_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_after_one_loop

        with patch("autoscaler.get_driver") as mock_get_driver, \
             patch("autoscaler.get_available_drivers") as mock_avail:

            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_driver.spawn_runner.return_value = "local-runner-arm64-1"

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            mock_driver.spawn_runner.assert_called()
            mock_driver.cleanup_all.assert_called()

    @patch("autoscaler.ACCESS_TOKEN", "fake-token")
    @patch("autoscaler.ORG", "my-test-org")
    @patch("autoscaler.MIN_RUNNERS", 2)
    @patch("autoscaler.MAX_RUNNERS", 4)
    @patch("autoscaler.HOST_CACHE_DIR")
    @patch("autoscaler.CACHE_ENABLED", True)
    @patch("autoscaler.time.sleep")
    def test_main_loop_organization_mode(self, mock_sleep, mock_cache_dir):
        mock_cache_dir.return_value = self.temp_cache

        def stop_loop(*args, **kwargs):
            autoscaler.running = False

        mock_sleep.side_effect = stop_loop

        with patch("autoscaler.get_driver") as mock_get_driver, \
             patch("autoscaler.get_available_drivers") as mock_avail:

            mock_driver = MagicMock()
            mock_driver.name.return_value = "docker"
            mock_driver.list_runners.return_value = []
            mock_driver.spawn_runner.return_value = "local-runner-org-1"

            mock_get_driver.return_value = mock_driver
            mock_avail.return_value = {"docker": mock_driver}

            autoscaler.running = True
            autoscaler.main()

            self.assertEqual(mock_driver.spawn_runner.call_count, 2)


if __name__ == "__main__":
    unittest.main()
