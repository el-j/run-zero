"""
Shared fixtures for the OrbStack driver/image test modules (not collected itself).
"""

import unittest
from unittest.mock import patch

from drivers.orbstack_vm_driver import OrbStackVMDriver


class OrbStackDriverTestCase(unittest.TestCase):
    """Base for OrbStack tests: a fresh driver per test, and no leaked background builds.

    Regression guard for issue #20: `_build_base_image_async` starts a real daemon thread. A
    thread left running past its test's mock.patch context would keep calling the module-global
    (by then differently patched, or real) subprocess.run from inside a LATER test, corrupting
    that test's mock bookkeeping non-deterministically -- this was the actual root cause of
    order-dependent flakiness in the spawn tests. tearDown joins every background thread the
    test's `self.driver` started and fails loudly if one is still alive, so a new test that
    forgets to mock `_build_base_image_async`/`build_base_image` fails at its own site.
    """

    def setUp(self):
        # Spawning exchanges the PAT for a registration token via the GitHub API; stub it.
        _reg = patch("drivers.create_registration_token", return_value="reg-token")
        self.create_registration_token = _reg.start()
        self.addCleanup(_reg.stop)
        self.driver = OrbStackVMDriver(distro="ubuntu:24.04")

    def tearDown(self):
        all_finished = self.driver.join_background_build_threads(timeout=15.0)
        self.assertTrue(
            all_finished,
            "A background build_base_image() thread outlived its test -- see issue #20. "
            "Mock _build_base_image_async (or build_base_image) in the test that just ran.",
        )

    def _run_async_build_and_wait(self, driver: OrbStackVMDriver, orb_arch: str) -> None:
        """Kick off _build_base_image_async and block until its background
        thread has actually finished (joined, not just polled via shared
        state) -- see issue #20 on why a real join matters here."""
        driver._build_base_image_async(orb_arch)
        if not driver.join_background_build_threads(timeout=5.0):
            self.fail("build_base_image_async did not finish in time")
