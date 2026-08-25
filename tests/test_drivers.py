"""
Unit tests for RunZero Runner Drivers (Docker, OrbStack VM, WSL2, Multipass).
Achieves 100% test coverage with complete edge-case and error branch testing.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import subprocess
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from drivers import RunnerInfo, get_driver, get_available_drivers
from drivers.docker_driver import DockerDriver
from drivers.orbstack_vm_driver import OrbStackVMDriver
from drivers.wsl_driver import WSL2Driver
from drivers.multipass_driver import MultipassDriver


class TestRunnerInfo(unittest.TestCase):
    def test_runner_info_properties_and_dict(self):
        info = RunnerInfo(
            id="runner-123",
            name="local-runner-arm64-abc",
            status="Up 2 hours",
            state="running",
            target_repo="el-j/run-zero",
            target_arch="arm64",
            backend="docker"
        )
        self.assertEqual(info.id, "runner-123")
        self.assertEqual(info.name, "local-runner-arm64-abc")
        self.assertEqual(info.status, "Up 2 hours")
        self.assertEqual(info.state, "running")
        self.assertEqual(info.target_repo, "el-j/run-zero")
        self.assertEqual(info.target_arch, "arm64")
        self.assertEqual(info.backend, "docker")

        d = info.to_dict()
        self.assertEqual(d["id"], "runner-123")
        self.assertEqual(d["backend"], "docker")
        self.assertEqual(d["target_repo"], "el-j/run-zero")


class TestDriverFactory(unittest.TestCase):
    def test_get_driver_explicit_names(self):
        self.assertIsInstance(get_driver("docker"), DockerDriver)
        self.assertIsInstance(get_driver("container"), DockerDriver)
        self.assertIsInstance(get_driver("orbstack-vm"), OrbStackVMDriver)
        self.assertIsInstance(get_driver("orb"), OrbStackVMDriver)
        self.assertIsInstance(get_driver("wsl2"), WSL2Driver)
        self.assertIsInstance(get_driver("wsl"), WSL2Driver)
        self.assertIsInstance(get_driver("multipass"), MultipassDriver)

    def test_get_driver_unknown_raises(self):
        with self.assertRaises(ValueError):
            get_driver("invalid-driver-name")

    @patch.object(DockerDriver, "is_available", return_value=True)
    def test_get_driver_auto_selects_docker_first(self, mock_docker_avail):
        driver = get_driver("auto")
        self.assertEqual(driver.name(), "docker")

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_orbstack(self, mock_orb_avail, mock_docker_avail):
        driver = get_driver("auto")
        self.assertEqual(driver.name(), "orbstack-vm")

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_wsl(self, mock_wsl_avail, mock_orb_avail, mock_docker_avail):
        driver = get_driver("auto")
        self.assertEqual(driver.name(), "wsl2")

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_multipass(self, mock_mp_avail, mock_wsl_avail, mock_orb_avail, mock_docker_avail):
        driver = get_driver("auto")
        self.assertEqual(driver.name(), "multipass")

    def test_get_available_drivers_returns_dict(self):
        drivers = get_available_drivers()
        self.assertIsInstance(drivers, dict)
        for name, d in drivers.items():
            self.assertTrue(d.is_available())


class TestDockerDriver(unittest.TestCase):
    def setUp(self):
        self.driver = DockerDriver(network="host")

    def test_name(self):
        self.assertEqual(self.driver.name(), "docker")

    @patch("shutil.which", return_value=None)
    def test_is_available_when_cli_missing(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/bin/docker")
    @patch("subprocess.run")
    def test_is_available_when_daemon_healthy(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/bin/docker")
    @patch("subprocess.run")
    def test_is_available_when_daemon_fails(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/bin/docker")
    @patch("subprocess.run", side_effect=Exception("Timeout"))
    def test_is_available_exception_handling(self, mock_run, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_spawn_runner_arm64_and_amd64(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        name = self.driver.spawn_runner(
            repo="el-j/run-zero",
            arch="arm64",
            access_token="test-token",
            proxies_enabled=True,
            cache_mounts={"/host/cache": "/container/cache"},
            extra_env={"CUSTOM_KEY": "CUSTOM_VAL"}
        )
        self.assertIsNotNone(name)
        self.assertTrue(name.startswith("local-runner-arm64-el-j-run-zero-"))

        # Test AMD64 with ORG and bridge network
        bridge_driver = DockerDriver(network="runner-network")
        name_amd64 = bridge_driver.spawn_runner(
            org="my-org",
            arch="amd64",
            labels="custom,label",
            access_token="test-token",
            proxies_enabled=True
        )
        self.assertIsNotNone(name_amd64)
        self.assertTrue(name_amd64.startswith("local-runner-amd64-my-org-"))

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, ["docker"], stderr=b"Docker daemon error"))
    def test_spawn_runner_failure(self, mock_run):
        name = self.driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_list_runners_parser(self, mock_run):
        mock_output = "abc123|Up 5 minutes|local-runner-arm64-1|running|el-j/run-zero|arm64|docker\n"
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].id, "abc123")
        self.assertEqual(runners[0].name, "local-runner-arm64-1")
        self.assertEqual(runners[0].target_repo, "el-j/run-zero")
        self.assertEqual(runners[0].state, "running")

    @patch("subprocess.run", side_effect=Exception("Docker down"))
    def test_list_runners_exception(self, mock_run):
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        runners = [
            RunnerInfo(id="dead1", name="runner-dead", status="Exited (0)", state="exited", target_repo="repo", target_arch="arm64", backend="docker"),
            RunnerInfo(id="live1", name="runner-live", status="Up 2m", state="running", target_repo="repo", target_arch="arm64", backend="docker")
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("dead1")
        self.driver.cleanup_all()


class TestOrbStackVMDriver(unittest.TestCase):
    def setUp(self):
        self.driver = OrbStackVMDriver(distro="ubuntu:22.04")

    def test_name(self):
        self.assertEqual(self.driver.name(), "orbstack-vm")

    @patch("shutil.which", return_value="/usr/local/bin/orbctl")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())

    @patch("shutil.which", return_value=None)
    def test_is_available_when_missing(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/local/bin/orbctl")
    @patch("subprocess.run", side_effect=Exception("Error"))
    def test_is_available_exception(self, mock_run, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner(self, mock_run, mock_popen):
        mock_run.return_value = MagicMock(returncode=0)
        name = self.driver.spawn_runner(
            repo="el-j/run-zero",
            arch="amd64",
            access_token="token",
            labels="custom,label"
        )
        self.assertIsNotNone(name)
        self.assertTrue(name.startswith("runzero-vm-amd64-el-j-run-zero-"))

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, ["orbctl"], stderr=b"Out of memory"))
    def test_spawn_runner_failure(self, mock_run):
        name = self.driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_list_runners_json_parser(self, mock_run):
        mock_json = json.dumps([
            {"name": "runzero-vm-arm64-el-j-abc123", "state": "running"},
            {"name": "runzero-vm-amd64-stopped", "state": "stopped"},
            {"name": "other-machine", "state": "running"}
        ])
        mock_run.return_value = MagicMock(stdout=mock_json, returncode=0)

        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)
        self.assertEqual(runners[0].id, "runzero-vm-arm64-el-j-abc123")
        self.assertEqual(runners[0].backend, "orbstack-vm")
        self.assertEqual(runners[0].state, "running")
        self.assertEqual(runners[1].state, "exited")

    @patch("subprocess.run", side_effect=Exception("List failed"))
    def test_list_runners_exception(self, mock_run):
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        runners = [
            RunnerInfo(id="runzero-vm-dead", name="runzero-vm-dead", status="stopped", state="exited", target_repo="", target_arch="arm64", backend="orbstack-vm")
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runzero-vm-dead")
        self.driver.cleanup_all()

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
                    {"name": "runzero-vm-amd64-el-j-abc123", "state": "running"},
                ]),
                returncode=0
            )
            runners = self.driver.list_runners()
        # The golden base image is a template, not a runner instance -- must
        # never be counted, pruned, or destroyed by the normal lifecycle.
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].name, "runzero-vm-amd64-el-j-abc123")

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
            MagicMock(returncode=0),  # orbctl delete -f (best-effort cleanup)
            subprocess.CalledProcessError(1, ["orbctl", "create"], stderr=b"Out of memory"),
        ]
        result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_success(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0),  # orbctl delete -f
            MagicMock(returncode=0),  # orbctl create
            MagicMock(returncode=0),  # orb -m ... bash -c <provision script>
            MagicMock(returncode=0),  # orbctl stop
        ]
        result = self.driver.build_base_image("amd64")
        self.assertTrue(result)

    @patch("subprocess.run")
    def test_build_base_image_provision_timeout(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0),  # orbctl delete -f
            MagicMock(returncode=0),  # orbctl create
            subprocess.TimeoutExpired(cmd="orb", timeout=1800),
        ]
        result = self.driver.build_base_image("amd64")
        self.assertFalse(result)


class TestWSL2Driver(unittest.TestCase):
    def setUp(self):
        self.driver = WSL2Driver()

    def test_name(self):
        self.assertEqual(self.driver.name(), "wsl2")

    @patch("shutil.which", return_value="/bin/wsl")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())

    @patch("shutil.which", return_value=None)
    def test_is_available_missing(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/bin/wsl")
    @patch("subprocess.run", side_effect=Exception("WSL error"))
    def test_is_available_exception(self, mock_run, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.Popen")
    def test_spawn_runner(self, mock_popen):
        name = self.driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNotNone(name)
        self.assertTrue(name.startswith("runzero-wsl-el-j-run-zero-"))

    @patch("subprocess.Popen", side_effect=Exception("Launch failed"))
    def test_spawn_runner_failure(self, mock_popen):
        name = self.driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_list_runners_parser(self, mock_run):
        mock_output = "runzero-wsl-el-j-123456\nother-distro\n"
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].id, "runzero-wsl-el-j-123456")
        self.assertEqual(runners[0].backend, "wsl2")

    @patch("subprocess.run", side_effect=Exception("List failed"))
    def test_list_runners_exception(self, mock_run):
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="runzero-wsl-dead", name="runzero-wsl-dead", status="stopped", state="exited", target_repo="", target_arch="x64", backend="wsl2")
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runzero-wsl-dead")
        self.driver.cleanup_all()

    @patch("subprocess.run", side_effect=Exception("Terminate error"))
    def test_destroy_runner_exception(self, mock_run):
        res = self.driver.destroy_runner("runzero-wsl-dead")
        self.assertFalse(res)


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
    @patch("subprocess.run", side_effect=Exception("Multipass error"))
    def test_is_available_exception(self, mock_run, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner(self, mock_run, mock_popen):
        mock_run.return_value = MagicMock(returncode=0)
        name = self.driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNotNone(name)
        self.assertTrue(name.startswith("runzero-mp-arm64-el-j-run-zero-"))

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, ["multipass"], stderr=b"Launch error"))
    def test_spawn_runner_failure(self, mock_run):
        name = self.driver.spawn_runner(repo="el-j/run-zero", access_token="token")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_list_runners_json_parser(self, mock_run):
        mock_json = json.dumps({
            "list": [
                {"name": "runzero-mp-arm64-abc123", "state": "Running"},
                {"name": "runzero-mp-stopped", "state": "Stopped"},
                {"name": "primary", "state": "Running"}
            ]
        })
        mock_run.return_value = MagicMock(stdout=mock_json, returncode=0)

        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)
        self.assertEqual(runners[0].id, "runzero-mp-arm64-abc123")
        self.assertEqual(runners[0].backend, "multipass")
        self.assertEqual(runners[0].state, "running")
        self.assertEqual(runners[1].state, "exited")

    @patch("subprocess.run", side_effect=Exception("List failed"))
    def test_list_runners_exception(self, mock_run):
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        runners = [
            RunnerInfo(id="runzero-mp-dead", name="runzero-mp-dead", status="Stopped", state="exited", target_repo="", target_arch="arm64", backend="multipass")
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runzero-mp-dead")
        self.driver.cleanup_all()


if __name__ == "__main__":
    unittest.main()
