"""
Unit tests for OrbStack Linux VM runner driver and templates.
"""

import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from drivers.orbstack_templates import docker_engine_snippet, registration_and_run_snippet, runner_download_snippet
from drivers.orbstack_vm_driver import OrbStackVMDriver


class TestOrbStackTemplates(unittest.TestCase):
    def test_snippets_generate_valid_bash(self):
        engine = docker_engine_snippet()
        self.assertIn("docker-ce", engine)
        self.assertIn("systemctl enable docker", engine)

        dl = runner_download_snippet("amd64", "2.336.0")
        self.assertIn("actions-runner-linux-${RUNNER_ARCH}-2.336.0.tar.gz", dl)

        reg = registration_and_run_snippet(
            "https://api.github.com/repos/owner/repo/actions/runners",
            "https://github.com/owner/repo",
            "pat-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1"
        )
        self.assertIn("registration-token", reg)
        self.assertIn("./config.sh", reg)
        self.assertIn("./run.sh", reg)


class TestOrbStackVMDriver(unittest.TestCase):
    def setUp(self):
        self.driver = OrbStackVMDriver(distro="ubuntu:22.04")

    def test_name(self):
        self.assertEqual(self.driver.name(), "orbstack-vm")

    @patch("shutil.which", return_value="/usr/local/bin/orbctl")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(stdout="OrbStack is running", returncode=0)
        self.assertTrue(self.driver.is_available())

    @patch("shutil.which", return_value=None)
    def test_is_available_when_missing(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/local/bin/orbctl")
    @patch("subprocess.run")
    def test_is_available_exception(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_list_runners_json_parser(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=json.dumps([
                {"name": "runzero-vm-arm64-el-j-run-zero-123", "state": "running"},
                {"name": "runzero-vm-amd64-my-org-456", "state": "stopped"},
                {"name": "unrelated-vm", "state": "running"}
            ]),
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)
        self.assertEqual(runners[0].name, "runzero-vm-arm64-el-j-run-zero-123")
        self.assertEqual(runners[0].target_arch, "arm64")
        self.assertEqual(runners[0].state, "running")
        self.assertEqual(runners[0].target_repo, "el-j-run-zero")

        self.assertEqual(runners[1].name, "runzero-vm-amd64-my-org-456")
        self.assertEqual(runners[1].target_arch, "amd64")
        self.assertEqual(runners[1].state, "exited")

    @patch("subprocess.run")
    def test_list_runners_creating_and_provisioning_are_pending_not_exited(self, mock_run):
        # Regression test: these are transient startup states, not terminal ones.
        # Misclassifying them as "exited" undercounts genuinely in-flight VMs in
        # the autoscaler's active-runner tally, causing a duplicate spawn for the
        # same job before the first VM finishes booting -- confirmed live: 3
        # runners registered for one real queued job, the 2 losers left idle
        # forever since ephemeral runners only self-terminate after completing a
        # job, never just for being unclaimed.
        mock_run.return_value = MagicMock(
            stdout=json.dumps([
                {"name": "runzero-vm-arm64-el-j-run-zero-aaa111", "state": "creating"},
                {"name": "runzero-vm-arm64-el-j-run-zero-bbb222", "state": "provisioning"},
            ]),
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "pending")
        self.assertEqual(runners[1].state, "pending")

    @patch("subprocess.run")
    def test_list_runners_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    def test_base_image_name(self):
        self.assertEqual(self.driver.base_image_name("amd64"), "runzero-vm-base-amd64")

    @patch("subprocess.run")
    def test_base_image_exists_true(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]),
            returncode=0
        )
        self.assertTrue(self.driver.base_image_exists("amd64"))

    @patch("subprocess.run")
    def test_base_image_exists_false(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([]), returncode=0)
        self.assertFalse(self.driver.base_image_exists("amd64"))

    def test_list_runners_excludes_base_image(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout=json.dumps([
                    {"name": "runzero-vm-base-amd64", "state": "stopped"},
                    {"name": "runzero-vm-amd64-el-j-run-zero-abc123", "state": "running"},
                ]),
                returncode=0
            )
            runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].name, "runzero-vm-amd64-el-j-run-zero-abc123")

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_clones_base_image_when_available(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),  # orbctl clone
        ]
        name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNotNone(name)
        clone_call = mock_run.call_args_list[1]
        self.assertEqual(clone_call[0][0][:2], ["orbctl", "clone"])

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_cold_provisions_when_no_base_image(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),
            MagicMock(returncode=0),  # orbctl create
        ]
        name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNotNone(name)
        create_call = mock_run.call_args_list[1]
        self.assertEqual(create_call[0][0][:2], ["orbctl", "create"])

    def test_build_base_image_missing_script_fails_gracefully(self):
        driver = OrbStackVMDriver(distro="ubuntu:22.04")
        driver._provision_script_path = "/nonexistent/provision-toolchain.sh"
        with patch("subprocess.run") as mock_run:
            result = driver.build_base_image("amd64")
        self.assertFalse(result)
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_build_base_image_create_failure(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0),
            subprocess.CalledProcessError(1, ["orbctl", "create"], stderr=b"Out of memory"),
        ]
        result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_success(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]
        result = self.driver.build_base_image("amd64")
        self.assertTrue(result)

    @patch("subprocess.run")
    def test_build_base_image_provision_timeout(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0),
            subprocess.TimeoutExpired(cmd="orb", timeout=1800),
        ]
        result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner(self, mock_run, mock_popen):
        mock_run.return_value = MagicMock(returncode=0)
        name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIn("runzero-vm-amd64-el-j-run-zero-", name)

    @patch("subprocess.run")
    def test_spawn_runner_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl", stderr=b"Out of memory")
        name = self.driver.spawn_runner(repo="el-j/run-zero")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="r1", name="runzero-vm-dead", status="stopped", state="exited", target_repo="", target_arch="arm64", backend="orbstack-vm"),
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runzero-vm-dead")
        self.driver.cleanup_all()


if __name__ == "__main__":
    unittest.main()
