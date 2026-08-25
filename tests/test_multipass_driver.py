"""
Unit tests for Canonical Multipass runner driver.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import subprocess
from drivers.multipass_driver import MultipassDriver
from drivers import RunnerInfo


class TestMultipassDriver(unittest.TestCase):
    def setUp(self):
        self.driver = MultipassDriver()

    def test_name(self):
        self.assertEqual(self.driver.name(), "multipass")

    @patch("shutil.which", return_value="/usr/local/bin/multipass")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())

    @patch("shutil.which", return_value=None)
    def test_is_available_missing(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/local/bin/multipass")
    @patch("subprocess.run")
    def test_is_available_exception(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(1, "multipass")
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_list_runners_json(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=json.dumps({
                "list": [
                    {"name": "runzero-mp-arm64-el-j-run-zero-123", "state": "Running"},
                    {"name": "runzero-mp-amd64-my-org-456", "state": "Stopped"},
                    {"name": "unrelated-instance", "state": "Running"}
                ]
            }),
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)
        self.assertEqual(runners[0].name, "runzero-mp-arm64-el-j-run-zero-123")
        self.assertEqual(runners[0].target_arch, "arm64")
        self.assertEqual(runners[0].state, "running")

        self.assertEqual(runners[1].name, "runzero-mp-amd64-my-org-456")
        self.assertEqual(runners[1].target_arch, "arm64")
        self.assertEqual(runners[1].state, "exited")

    @patch("subprocess.run")
    def test_list_runners_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "multipass")
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner(self, mock_run, mock_popen):
        mock_run.return_value = MagicMock(returncode=0)
        name = self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="token", proxies_enabled=True)
        self.assertIn("runzero-mp-arm64-el-j-run-zero-", name)

    @patch("subprocess.run")
    def test_spawn_runner_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "multipass", stderr=b"Launch failed")
        name = self.driver.spawn_runner(repo="el-j/run-zero")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="r1", name="runzero-mp-dead", status="Stopped", state="exited", target_repo="", target_arch="arm64", backend="multipass"),
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runzero-mp-dead")
        self.driver.cleanup_all()


if __name__ == "__main__":
    unittest.main()
