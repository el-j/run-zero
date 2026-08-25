"""
Unit tests for Docker container runner driver.
"""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from drivers.docker_driver import DockerDriver


class TestDockerDriver(unittest.TestCase):
    def setUp(self):
        self.driver = DockerDriver()

    def test_name(self):
        self.assertEqual(self.driver.name(), "docker")

    @patch("shutil.which", return_value="/usr/local/bin/docker")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())

    @patch("shutil.which", return_value=None)
    def test_is_available_when_no_binary(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/local/bin/docker")
    @patch("subprocess.run")
    def test_is_available_when_error(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_list_runners_parsing(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="runner1|Up 2 hours|local-runner-arm64-el-j-run-zero-123|running|el-j/run-zero|arm64|docker\nrunner2|Exited (0)|local-runner-amd64-my-org-456|exited|my-org|amd64|docker\n",
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)
        self.assertEqual(runners[0].name, "local-runner-arm64-el-j-run-zero-123")
        self.assertEqual(runners[0].target_arch, "arm64")
        self.assertEqual(runners[0].state, "running")
        self.assertEqual(runners[0].target_repo, "el-j/run-zero")

        self.assertEqual(runners[1].name, "local-runner-amd64-my-org-456")
        self.assertEqual(runners[1].target_arch, "amd64")
        self.assertEqual(runners[1].state, "exited")

    @patch("subprocess.run")
    def test_list_runners_created_and_restarting_are_pending(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="r1|Created|c1|created|el-j/run-zero|arm64|docker\nr2|Restarting|c2|restarting|el-j/run-zero|arm64|docker\n",
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "pending")
        self.assertEqual(runners[1].state, "pending")

    @patch("subprocess.run")
    def test_list_runners_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.run")
    def test_spawn_runner_arm64_and_amd64(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        # Spawn for Repo
        name_arm = self.driver.spawn_runner(
            repo="el-j/run-zero",
            arch="arm64",
            access_token="secret-pat",
            cache_mounts={"/host/cache": "/home/runner/.cache"},
            proxies_enabled=True
        )
        self.assertIn("local-runner-arm64-el-j-run-zero-", name_arm)

        # Spawn for Org
        name_amd = self.driver.spawn_runner(
            org="my-org",
            arch="amd64",
            access_token="secret-pat",
            proxies_enabled=False
        )
        self.assertIn("local-runner-amd64-my-org-", name_amd)

    @patch("subprocess.run")
    def test_spawn_runner_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker", stderr=b"Docker daemon error")
        name = self.driver.spawn_runner(repo="el-j/run-zero")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="r1", name="runner-dead", status="exited", state="exited", target_repo="", target_arch="arm64", backend="docker"),
            RunnerInfo(id="r2", name="runner-live", status="running", state="running", target_repo="", target_arch="arm64", backend="docker"),
            RunnerInfo(id="r3", name="runner-vm", status="exited", state="exited", target_repo="", target_arch="arm64", backend="orbstack-vm"),
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runner-dead")
        self.driver.cleanup_all()


if __name__ == "__main__":
    unittest.main()
