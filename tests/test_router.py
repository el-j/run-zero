"""
Unit tests for hybrid runner routing engine.
"""

import unittest

from drivers.docker_driver import DockerDriver
from drivers.orbstack_vm_driver import OrbStackVMDriver
from router import select_driver_for_job


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.docker_driver = DockerDriver()
        self.orbstack_driver = OrbStackVMDriver()
        self.available_drivers = {
            "docker": self.docker_driver,
            "orbstack-vm": self.orbstack_driver
        }

    def test_select_driver_standard_unit_test(self):
        job = {"name": "unit-tests", "labels": ["self-hosted", "local"]}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=True)
        self.assertEqual(driver.name(), "docker")
        self.assertEqual(mode, "container")

    def test_select_driver_browser_label(self):
        job = {"name": "e2e", "labels": ["self-hosted", "browser"]}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=True)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")

    def test_select_driver_job_name_tokenization(self):
        job = {"name": "run-lighthouse-audit", "labels": ["self-hosted"]}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=True)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")

    def test_select_driver_auto_route_disabled(self):
        job = {"name": "chrome-e2e", "labels": ["browser"]}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=False)
        self.assertEqual(driver.name(), "docker")
        self.assertEqual(mode, "container")


if __name__ == "__main__":
    unittest.main()
