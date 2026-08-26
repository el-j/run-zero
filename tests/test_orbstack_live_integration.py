"""
Real (non-mocked) integration test for OrbStack VM disk caching (issue #10).

Unlike every other driver test in this suite, this one does NOT mock subprocess/orb
calls -- it creates real, disposable OrbStack VMs and proves cache_mount_snippet()'s
bind mounts actually round-trip data through real host storage, and that data written
by one ephemeral VM is genuinely visible to a second VM mounting the same host
directory (the exact bar issue #10's Definition of Done asked for: "A real test proves
cache data written by one ephemeral VM is visible to the next VM spawned for the same
arch -- not just that a mount call was made").

Skipped by default -- this creates and destroys two real OrbStack VMs, which takes
roughly a minute even on the fast path, so it deliberately does NOT run as part of the
plain `python3 -m unittest discover` the pre-commit hook runs on every commit (that
would silently cost every future commit on an OrbStack-equipped dev machine an extra
minute). Opt in explicitly with `RUNZERO_LIVE_TESTS=1`, e.g.:

    RUNZERO_LIVE_TESTS=1 PYTHONPATH=src python3 -m unittest tests.test_orbstack_live_integration -v

Also skipped wherever `orbctl`/`orb` aren't on PATH or the OrbStack daemon isn't
running (e.g. inside `make test-suite`'s Linux container, or any CI runner without
OrbStack, even with the env var set) -- there is no way to fake this mechanism, so on
those hosts the coverage for cache_mount_snippet() itself comes from
test_orbstack_driver.py's mocked tests.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
import uuid

from drivers.orbstack_templates import cache_mount_snippet

VM_PREFIX = "runzero-test-livecache-"


def _live_tests_requested() -> bool:
    return os.getenv("RUNZERO_LIVE_TESTS", "").lower() in ("1", "true", "yes")


def _orbstack_available() -> bool:
    if not shutil.which("orbctl") or not shutil.which("orb"):
        return False
    try:
        res = subprocess.run(["orbctl", "status"], capture_output=True, text=True, timeout=5)
        return res.returncode == 0 and "running" in res.stdout.lower()
    except Exception:
        return False


@unittest.skipUnless(_live_tests_requested(), "set RUNZERO_LIVE_TESTS=1 to run real OrbStack VM lifecycle tests")
@unittest.skipUnless(_orbstack_available(), "orbctl/OrbStack daemon not available on this host")
class TestOrbStackLiveCacheSharing(unittest.TestCase):
    """Creates real, disposable OrbStack VMs -- slow (~10-30s) and host-dependent by design."""

    def setUp(self) -> None:
        self.host_dir = tempfile.mkdtemp(prefix="runzero-live-cache-test-")
        self.vm_names = []

    def tearDown(self) -> None:
        for name in self.vm_names:
            subprocess.run(["orbctl", "delete", "-f", name], capture_output=True)
        shutil.rmtree(self.host_dir, ignore_errors=True)

    def _create_vm(self) -> str:
        name = f"{VM_PREFIX}{uuid.uuid4().hex[:8]}"
        subprocess.run(
            ["orbctl", "create", "-a", "arm64", "-u", "runner", "ubuntu:24.04", name],
            check=True, capture_output=True, timeout=60,
        )
        self.vm_names.append(name)
        return name

    def _mount_cache(self, vm_name: str, container_path: str) -> None:
        snippet = cache_mount_snippet({self.host_dir: container_path})
        res = subprocess.run(
            ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", snippet],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(res.returncode, 0, f"cache_mount_snippet failed: {res.stderr}")

    def test_cache_data_written_by_one_vm_is_visible_to_next_vm_same_host_dir(self):
        container_path = "/home/runner/.npm"

        vm1 = self._create_vm()
        self._mount_cache(vm1, container_path)
        write_res = subprocess.run(
            ["orb", "-m", vm1, "-u", "runner", "bash", "-c",
             f'echo "written-by-{vm1}" > {container_path}/marker.txt'],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(write_res.returncode, 0, write_res.stderr)

        # A second, independent VM -- standing in for the next ephemeral job VM cloned
        # for the same architecture -- mounts the SAME host directory and must see the
        # exact data the first VM wrote, proving this is a real host-backed cache and
        # not per-VM-ephemeral storage.
        vm2 = self._create_vm()
        self._mount_cache(vm2, container_path)
        read_res = subprocess.run(
            ["orb", "-m", vm2, "-u", "runner", "bash", "-c", f"cat {container_path}/marker.txt"],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(read_res.returncode, 0, read_res.stderr)
        self.assertEqual(read_res.stdout.strip(), f"written-by-{vm1}")

        # And it's genuinely on real host disk, not just shared between the two VMs by
        # coincidence of both being VMs -- confirm the plain host filesystem sees it too.
        with open(f"{self.host_dir}/marker.txt") as f:
            self.assertEqual(f.read().strip(), f"written-by-{vm1}")


if __name__ == "__main__":
    unittest.main()
