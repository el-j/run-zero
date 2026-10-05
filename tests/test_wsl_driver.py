"""
Unit tests for Windows WSL2 runner driver.
"""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from drivers.wsl_driver import WSL2Driver


class TestWSL2Driver(unittest.TestCase):
    def setUp(self):
        # Spawning exchanges the PAT for a registration token via the GitHub API; stub it.
        _reg = patch("drivers.create_registration_token", return_value="reg-token")
        self.create_registration_token = _reg.start()
        self.addCleanup(_reg.stop)
        self.driver = WSL2Driver()

    def test_name(self):
        self.assertEqual(self.driver.name(), "wsl2")

    @patch("shutil.which", return_value="/mnt/c/Windows/System32/wsl.exe")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())

    @patch("shutil.which", return_value=None)
    def test_is_available_missing(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/mnt/c/Windows/System32/wsl.exe")
    @patch("subprocess.run")
    def test_is_available_exception(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(1, "wsl.exe")
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_list_runners_parser(self, mock_run):
        mock_run.return_value = MagicMock(stdout="runzero-wsl-el-j-run-zero-123\nunrelated-distro\n", returncode=0)
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].name, "runzero-wsl-el-j-run-zero-123")
        self.assertEqual(runners[0].state, "running")

    @patch("subprocess.run")
    def test_list_runners_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "wsl.exe")
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.Popen")
    def test_spawn_runner(self, mock_popen):
        name = self.driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        assert name is not None
        self.assertTrue(name.startswith("runzero-wsl-") and "-el-j-run-zero-" in name)

    @patch("subprocess.Popen")
    def test_spawn_runner_wires_proxy_stack_when_enabled(self, mock_popen):
        self.driver.spawn_runner(repo="el-j/run-zero", access_token="token", proxies_enabled=True)
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertIn('export YARN_REGISTRY="http://${HOST_IP}:49501/"', setup_script)
        self.assertIn('export pnpm_config_registry="http://${HOST_IP}:49501/"', setup_script)
        self.assertIn("export RUNNER_TOOL_CACHE=/opt/hostedtoolcache", setup_script)
        self.assertIn('export PIP_INDEX_URL="http://${HOST_IP}:49507/root/pypi/+simple/"', setup_script)
        self.assertIn('export UV_INDEX_URL="${PIP_INDEX_URL}"', setup_script)
        self.assertIn('export PIP_TRUSTED_HOST="${HOST_IP}"', setup_script)
        self.assertIn('Acquire::http::Proxy "http://${HOST_IP}:49503";', setup_script)
        self.assertIn('replace-with = "kellnr-proxy"', setup_script)

    @patch("subprocess.Popen")
    def test_spawn_runner_omits_proxy_stack_when_disabled(self, mock_popen):
        self.driver.spawn_runner(repo="el-j/run-zero", access_token="token", proxies_enabled=False)
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertNotIn("PIP_INDEX_URL", setup_script)
        self.assertNotIn("kellnr-proxy", setup_script)
        self.assertNotIn("01runzero-proxy", setup_script)

    @patch("subprocess.Popen")
    def test_spawn_runner_failure(self, mock_popen):
        mock_popen.side_effect = OSError("Launch failed")
        name = self.driver.spawn_runner(repo="el-j/run-zero")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="r1", name="runzero-wsl-dead", status="stopped", state="exited", target_repo="", target_arch="x64", backend="wsl2"),
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runzero-wsl-dead")
        self.driver.cleanup_all()

    @patch("subprocess.run")
    def test_destroy_runner_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "wsl.exe", stderr=b"Terminate error")
        self.assertFalse(self.driver.destroy_runner("runzero-wsl-dead"))

    @patch("subprocess.run")
    def test_cleanup_all_terminates_wsl2_backed_runners(self, mock_run):
        # Regression guard: cleanup_all() must only terminate runners whose
        # backend is actually "wsl2" -- list_runners() itself is real here
        # (only subprocess.run is mocked), so this exercises the real
        # filtering loop rather than relying on list_runners() failing
        # closed to an empty list.
        mock_run.return_value = MagicMock(stdout="runzero-wsl-el-j-run-zero-abc123\n", returncode=0)
        self.driver.cleanup_all()
        terminate_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["wsl", "--terminate"]]
        self.assertEqual(len(terminate_calls), 1)
        self.assertEqual(terminate_calls[0][0][0], ["wsl", "--terminate", "runzero-wsl-el-j-run-zero-abc123"])

    def test_windows_to_wsl_path(self):
        from drivers.runner_bootstrap import windows_to_wsl_path

        self.assertEqual(windows_to_wsl_path(r"C:\Users\admin\cache\npm"), "/mnt/c/Users/admin/cache/npm")
        self.assertEqual(windows_to_wsl_path("D:/cache/go-mod"), "/mnt/d/cache/go-mod")
        self.assertEqual(windows_to_wsl_path("/home/runner/.cache"), "/home/runner/.cache")

    @patch("subprocess.Popen")
    def test_spawn_runner_mounts_cache_dirs_when_provided(self, mock_popen):
        self.driver.spawn_runner(
            repo="el-j/run-zero",
            access_token="token",
            cache_mounts={r"C:\Users\admin\.cache\npm": "/home/runner/.npm"},
        )
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertIn("/mnt/c/Users/admin/.cache/npm", setup_script)
        self.assertIn("mount --bind /mnt/c/Users/admin/.cache/npm /home/runner/.npm", setup_script)
        self.assertIn("export PLAYWRIGHT_BROWSERS_PATH=/home/runner/.cache/ms-playwright", setup_script)

    def test_spawn_runner_refuses_mismatched_arch(self):
        with patch("drivers.wsl_driver.host_arch", return_value="amd64"), patch("sys.stderr"):
            res = self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="token")
            self.assertIsNone(res)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_with_base_tarball(self, mock_run, mock_popen):
        mock_run.return_value = MagicMock(returncode=0)
        driver = WSL2Driver(base_tarball="/path/to/base.tar")
        name = driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNotNone(name)
        import_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["wsl", "--import"]]
        self.assertEqual(len(import_calls), 1)
        self.assertEqual(import_calls[0][0][0][1], "--import")
        self.assertEqual(import_calls[0][0][0][2], name)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_with_base_tarball_import_failure(self, mock_run, mock_popen):
        mock_run.side_effect = subprocess.CalledProcessError(1, "wsl --import", stderr=b"import failed")
        driver = WSL2Driver(base_tarball="/path/to/base.tar")
        with patch("sys.stderr"):
            name = driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNone(name)
        mock_popen.assert_not_called()

    @patch("subprocess.run")
    def test_destroy_runner_with_base_tarball_unregisters(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        driver = WSL2Driver(base_tarball="/path/to/base.tar")
        self.assertTrue(driver.destroy_runner("runzero-wsl-dead"))
        unregister_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["wsl", "--unregister"]]
        self.assertEqual(len(unregister_calls), 1)
        self.assertEqual(unregister_calls[0][0][0], ["wsl", "--unregister", "runzero-wsl-dead"])

    @patch("subprocess.run")
    def test_list_runners_with_store_metadata(self, mock_run):
        mock_run.return_value = MagicMock(stdout="runzero-wsl-amd64-my-org-123\n", returncode=0)
        self.driver.store.put("runzero-wsl-amd64-my-org-123", target="my-org", arch="amd64", created_at=12345.0)
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].name, "runzero-wsl-amd64-my-org-123")
        self.assertEqual(runners[0].target_repo, "my-org")
        self.assertEqual(runners[0].target_arch, "amd64")
        self.assertEqual(runners[0].created_at, 12345.0)


if __name__ == "__main__":
    unittest.main()
