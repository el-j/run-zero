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
        # get_queued_job_details() always sets declares_services explicitly
        # (True/False/None) -- a real "no services" job looks like this, not
        # like a bare dict missing the key entirely.
        job = {"name": "unit-tests", "labels": ["self-hosted", "local"], "declares_services": False}
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

    def test_select_driver_declares_services_true_routes_to_vm(self):
        # Regression test: a job whose NAME matches nothing in
        # VM_TRIGGER_LABELS but whose workflow YAML actually declares a
        # `services:` block (resolved by get_queued_job_details() via
        # workflow_inspector) must still be VM-routed -- this is exactly
        # what "API — Tests" (a real herbful CI job with a postgres
        # services: block) was missing before declares_services existed,
        # while "User Service — Tests" only worked by naming coincidence.
        job = {"name": "API — Tests", "labels": ["self-hosted", "local", "amd64"], "declares_services": True}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=True)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")

    def test_select_driver_declares_services_false_no_name_match_stays_container(self):
        job = {"name": "API — Lint", "labels": ["self-hosted", "local"], "declares_services": False}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=True)
        self.assertEqual(driver.name(), "docker")
        self.assertEqual(mode, "container")

    def test_select_driver_declares_services_none_falls_back_to_name_heuristic(self):
        # None means "workflow file couldn't be resolved/parsed" -- must NOT
        # be treated as False, only as "defer to the name/label heuristic".
        job = {"name": "run-lighthouse-audit", "labels": ["self-hosted"], "declares_services": None}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=True)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")

    def test_select_driver_declares_services_none_and_no_name_match_still_routes_to_vm(self):
        # Regression test: this is the actual bug, isolated. The test above
        # doesn't distinguish "None is fail-safe" from "None is treated as
        # False" because its job name ALSO matches the name heuristic on its
        # own -- that overlap is exactly how `needs_vm = name_or_label_match
        # or bool(declares_services)` shipped and stayed broken: it passed
        # every existing test while still silently losing VM routing for any
        # job whose name/labels don't happen to match anything, the moment
        # the workflow-YAML lookup returns "unknown" (confirmed live: a real
        # `services: postgres:` herbful job, name "API — Tests", landed on
        # the Docker driver whenever declares_services resolved to None).
        job = {"name": "API — Tests", "labels": ["self-hosted", "local", "amd64"], "declares_services": None}
        driver, mode = select_driver_for_job(job, self.docker_driver, self.available_drivers, auto_route_vm=True)
        self.assertEqual(driver.name(), "orbstack-vm")
        self.assertEqual(mode, "vm")

    def test_select_driver_declares_services_true_but_no_vm_driver_falls_back_and_warns(self):
        job = {"name": "API — Tests", "labels": ["self-hosted"], "declares_services": True}
        driver, mode = select_driver_for_job(job, self.docker_driver, {"docker": self.docker_driver}, auto_route_vm=True)
        self.assertEqual(driver.name(), "docker")
        self.assertEqual(mode, "container")


if __name__ == "__main__":
    unittest.main()
