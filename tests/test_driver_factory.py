"""
Unit tests for Driver Factory and RunnerInfo model.
"""

import unittest
from unittest.mock import patch

from drivers import RunnerInfo, get_available_drivers, get_driver
from drivers.bridge_driver import BridgeVMDriver
from drivers.docker_driver import DockerDriver
from drivers.multipass_driver import MultipassDriver
from drivers.orbstack_vm_driver import OrbStackVMDriver
from drivers.wsl_driver import WSL2Driver


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
    """
    All tests here must fully mock `is_available()` on every native driver
    class AND on `BridgeVMDriver` -- `get_driver()`/`get_available_drivers()`
    fall through to `BridgeVMDriver(name).is_available()` (a real HTTP call,
    see bridge_driver.py) whenever a native driver reports unavailable, so
    any code path that reaches that fallback without a mock in place would
    depend on whatever host-VM-bridge process happens to be reachable on the
    machine running the tests. See GitHub issue #9.
    """

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=True)
    @patch.object(WSL2Driver, "is_available", return_value=True)
    @patch.object(MultipassDriver, "is_available", return_value=True)
    def test_get_driver_explicit_names(self, mock_mp, mock_wsl, mock_orb, mock_bridge):
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

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_wsl(self, mock_wsl, mock_orb, mock_docker, mock_bridge):
        driver = get_driver("auto")
        self.assertIsInstance(driver, WSL2Driver)

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=True)
    def test_get_driver_auto_falls_back_to_multipass(self, mock_mp, mock_wsl, mock_orb, mock_docker, mock_bridge):
        driver = get_driver("auto")
        self.assertIsInstance(driver, MultipassDriver)

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_driver_auto_falls_back_to_docker_when_nothing_available(self, mock_mp, mock_wsl, mock_orb, mock_docker, mock_bridge):
        # get_driver("auto")'s documented final fallback (see src/drivers/__init__.py) is the
        # Docker driver itself, even though DockerDriver.is_available() is False here -- this
        # locks in that "give up and return docker anyway" behavior as an intentional contract,
        # not an accident.
        driver = get_driver("auto")
        self.assertIsInstance(driver, DockerDriver)

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(DockerDriver, "is_available", return_value=True)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_available_drivers_returns_dict(self, mock_mp, mock_wsl, mock_orb, mock_docker, mock_bridge):
        avail = get_available_drivers()
        self.assertIn("docker", avail)
        self.assertNotIn("orbstack-vm", avail)
        self.assertNotIn("wsl2", avail)
        self.assertNotIn("multipass", avail)

    @patch.object(BridgeVMDriver, "is_available")
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    def test_get_driver_falls_through_to_bridge_when_native_unavailable(self, mock_orb, mock_bridge_avail):
        # Regression test for the fallback documented in src/drivers/__init__.py: when a native
        # driver is unavailable but the Host VM Bridge reports the same backend as available,
        # get_driver() must hand back a BridgeVMDriver wrapping that backend instead of the
        # (unavailable) native driver. Previously this path was only ever exercised by accident
        # (see #9), never asserted directly.
        mock_bridge_avail.return_value = True
        driver = get_driver("orbstack-vm")
        self.assertIsInstance(driver, BridgeVMDriver)
        self.assertEqual(driver.name(), "orbstack-vm")

    @patch.object(BridgeVMDriver, "is_available", return_value=True)
    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_available_drivers_uses_bridge_when_native_unavailable(self, mock_mp, mock_wsl, mock_orb, mock_docker, mock_bridge):
        # Mirrors the regression above but through get_available_drivers()'s own loop: every
        # native driver is unavailable, but the bridge reports every backend as available, so
        # all four keys should be populated with BridgeVMDriver instances.
        avail = get_available_drivers()
        self.assertEqual(set(avail.keys()), {"docker", "orbstack-vm", "wsl2", "multipass"})
        for driver in avail.values():
            self.assertIsInstance(driver, BridgeVMDriver)

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    def test_get_driver_orbstack_falls_back_to_native_when_bridge_unavailable(self, mock_orb, mock_bridge):
        # Both the native orbstack driver AND the bridge are unavailable --
        # get_driver("orbstack-vm") must still hand back the (unavailable)
        # native instance rather than raising or returning None.
        driver = get_driver("orbstack-vm")
        self.assertIsInstance(driver, OrbStackVMDriver)
        self.assertNotIsInstance(driver, BridgeVMDriver)

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    def test_get_driver_wsl_falls_back_to_native_when_bridge_unavailable(self, mock_wsl, mock_bridge):
        driver = get_driver("wsl2")
        self.assertIsInstance(driver, WSL2Driver)
        self.assertNotIsInstance(driver, BridgeVMDriver)

    @patch.object(BridgeVMDriver, "is_available", return_value=True)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    def test_get_driver_wsl_falls_through_to_bridge_when_native_unavailable(self, mock_wsl, mock_bridge):
        driver = get_driver("wsl2")
        self.assertIsInstance(driver, BridgeVMDriver)
        self.assertEqual(driver.name(), "wsl2")

    @patch.object(BridgeVMDriver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_driver_multipass_falls_back_to_native_when_bridge_unavailable(self, mock_mp, mock_bridge):
        driver = get_driver("multipass")
        self.assertIsInstance(driver, MultipassDriver)
        self.assertNotIsInstance(driver, BridgeVMDriver)

    @patch.object(BridgeVMDriver, "is_available", return_value=True)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_driver_multipass_falls_through_to_bridge_when_native_unavailable(self, mock_mp, mock_bridge):
        driver = get_driver("multipass")
        self.assertIsInstance(driver, BridgeVMDriver)
        self.assertEqual(driver.name(), "multipass")

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_driver_auto_falls_through_orbstack_bridge(
        self, mock_mp, mock_wsl, mock_orb, mock_docker
    ):
        # Auto-selection: docker/orb-native/wsl-native/mp-native all
        # unavailable, but the bridge reports orbstack-vm as available --
        # auto must pick the orbstack-vm bridge instance, not fall further
        # down the chain to WSL/multipass.
        def bridge_is_available(self):
            return self.target_backend == "orbstack-vm"

        with patch.object(BridgeVMDriver, "is_available", bridge_is_available):
            driver = get_driver("auto")
        self.assertIsInstance(driver, BridgeVMDriver)
        self.assertEqual(driver.name(), "orbstack-vm")

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_driver_auto_falls_through_wsl_bridge(
        self, mock_mp, mock_wsl, mock_orb, mock_docker
    ):
        # Same idea, one step further down the chain: orbstack-vm bridge is
        # also unavailable, but wsl2's bridge is available.
        def bridge_is_available(self):
            return self.target_backend == "wsl2"

        with patch.object(BridgeVMDriver, "is_available", bridge_is_available):
            driver = get_driver("auto")
        self.assertIsInstance(driver, BridgeVMDriver)
        self.assertEqual(driver.name(), "wsl2")

    @patch.object(DockerDriver, "is_available", return_value=False)
    @patch.object(OrbStackVMDriver, "is_available", return_value=False)
    @patch.object(WSL2Driver, "is_available", return_value=False)
    @patch.object(MultipassDriver, "is_available", return_value=False)
    def test_get_driver_auto_falls_through_multipass_bridge(
        self, mock_mp, mock_wsl, mock_orb, mock_docker
    ):
        # Last step of the auto chain: only multipass's bridge is available.
        def bridge_is_available(self):
            return self.target_backend == "multipass"

        with patch.object(BridgeVMDriver, "is_available", bridge_is_available):
            driver = get_driver("auto")
        self.assertIsInstance(driver, BridgeVMDriver)
        self.assertEqual(driver.name(), "multipass")


if __name__ == "__main__":
    unittest.main()
