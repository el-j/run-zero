"""
Unit tests for Driver Factory and RunnerInfo model.
"""

import unittest
from unittest.mock import patch
from drivers import get_driver, get_available_drivers, RunnerInfo
from drivers.docker_driver import DockerDriver
from drivers.orbstack_vm_driver import OrbStackVMDriver
from drivers.wsl_driver import WSL2Driver
from drivers.multipass_driver import MultipassDriver


class TestRunnerInfo(unittest.TestCase):
    def test_runner_info_properties_and_dict(self):
        info = RunnerInfo(
            id="runner-123",
            name="runner-123",
            status="running",
            state="running",
            target_repo="el-j/run-zero",
            target_arch="arm64",
            backend="docker"
        )
        self.assertEqual(info.id, "runner-123")
        self.assertEqual(info.name, "runner-123")
        self.assertEqual(info.status, "running")
        self.assertEqual(info.state, "running")
        self.assertEqual(info.target_arch, "arm64")
        self.assertEqual(info.backend, "docker")
        self.assertEqual(info.target_repo, "el-j/run-zero")

        d = info.to_dict()
        self.assertEqual(d["id"], "runner-123")
        self.assertEqual(d["target_repo"], "el-j/run-zero")


class TestDriverFactory(unittest.TestCase):
    def test_get_driver_explicit_names(self):
        self.assertIsInstance(get_driver("docker"), DockerDriver)
        self.assertIsInstance(get_driver("orbstack-vm"), OrbStackVMDriver)
        self.assertIsInstance(get_driver("wsl2"), WSL2Driver)
        self.assertIsInstance(get_driver("multipass"), MultipassDriver)

    def test_get_driver_unknown_raises(self):
        with self.assertRaises(ValueError):
            get_driver("unsupported-backend-xyz")

    @patch.object(DockerDriver, "is_available", return_value=True)
    def test_get_driver_auto_selects_docker_first(self, mock_avail):
        driver = get_driver("auto")
        self.assertIsInstance(driver, DockerDriver)

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_orbstack(self, mock_orb, mock_docker):
        driver = get_driver("auto")
        self.assertIsInstance(driver, OrbStackVMDriver)

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_wsl(self, mock_wsl, mock_orb, mock_docker):
        driver = get_driver("auto")
        self.assertIsInstance(driver, WSL2Driver)

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_multipass(self, mock_mp, mock_wsl, mock_orb, mock_docker):
        driver = get_driver("auto")
        self.assertIsInstance(driver, MultipassDriver)

    @patch.object(DockerDriver, "is_available", return_value=True)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    def test_get_available_drivers_returns_dict(self, mock_orb, mock_docker):
        avail = get_available_drivers()
        self.assertIn("docker", avail)
        self.assertNotIn("orbstack-vm", avail)


if __name__ == "__main__":
    unittest.main()
