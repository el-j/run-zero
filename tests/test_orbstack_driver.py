"""
Tests for the OrbStack VM driver's job-VM lifecycle: availability, spawn (clone + setup
script), listing, spawn circuit breaker, prune and destroy.
"""

import json
import subprocess
import sys
import time
import unittest
from unittest.mock import MagicMock, call, patch

from orbstack_test_base import OrbStackDriverTestCase

from drivers import RunnerInfo
from drivers.orbstack_vm_driver import (
    FAST_FAILURE_WINDOW_SECONDS,
    STARTUP_GRACE_PERIOD_SECONDS,
    OrbStackVMDriver,
)


class TestOrbStackVMDriver(OrbStackDriverTestCase):
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

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_is_available_when_orb_binary_missing(self, mock_which, mock_run):
        # Both executables are required. If orbctl exists but orb is missing,
        # we must return False without probing daemon status.
        mock_which.side_effect = ["/usr/local/bin/orbctl", None]
        self.assertFalse(self.driver.is_available())
        mock_run.assert_not_called()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_is_available_checks_expected_binaries_and_status_command(self, mock_which, mock_run):
        mock_which.side_effect = ["/usr/local/bin/orbctl", "/usr/local/bin/orb"]
        mock_run.return_value = MagicMock(stdout="RUNNING\n", returncode=0)

        self.assertTrue(self.driver.is_available())
        mock_which.assert_has_calls([call("orbctl"), call("orb")])
        mock_run.assert_called_once_with(
            ["orbctl", "status"],
            capture_output=True,
            text=True,
            check=True,
            timeout=3,
        )

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_is_available_false_when_status_not_running(self, mock_which, mock_run):
        mock_which.side_effect = ["/usr/local/bin/orbctl", "/usr/local/bin/orb"]
        mock_run.return_value = MagicMock(stdout="stopped", returncode=0)
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/local/bin/orbctl")
    @patch("subprocess.run")
    def test_is_available_exception(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_list_runners_json_parser(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                [
                    {"name": "runzero-vm-arm64-el-j-run-zero-123", "state": "running"},
                    {"name": "runzero-vm-amd64-my-org-456", "state": "stopped"},
                    {"name": "unrelated-vm", "state": "running"},
                ]
            ),
            returncode=0,
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
    def test_list_runners_starting_is_pending_not_exited(self, mock_run):
        # Regression test: "starting" is a real, observed transient OrbStack VM
        # state during boot (confirmed live via `orbctl list` polled every 2s on
        # a real clone), distinct from "creating"/"provisioning" but equally
        # non-terminal. Misclassifying it as "exited" is worse than just an
        # undercount: prune_exited() force-deletes anything "exited", so a VM
        # caught mid-boot here was destroyed before it could finish registering
        # with GitHub -- the job never ran, and the autoscaler kept spawning (and
        # killing) a fresh clone every poll forever.
        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                [
                    {"name": "runzero-vm-amd64-el-j-run-zero-ccc333", "state": "starting"},
                ]
            ),
            returncode=0,
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "pending")

    @patch("subprocess.run")
    def test_list_runners_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.run")
    def test_list_runners_derives_created_at_from_orbstack_ulid(self, mock_run):
        # This id is a real OrbStack VM id (a ULID) captured live; its first 10
        # characters decode to 2026-09-09 15:47:33.355 UTC == 1788968853.355.
        # See _vm_created_at_from_ulid()'s docstring: this is what makes a VM's
        # tracked age survive a driver-process restart instead of resetting to
        # "just created" every time -- confirmed live to have left 4 orphaned
        # VMs running for 16+ hours because reconciler.py's age-based cleanup
        # never saw them as old.
        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                [
                    {
                        "id": "01M23DMQVBY90E2BVMYBA1GAZT",
                        "name": "runzero-vm-amd64-el-j-herbful-858742",
                        "state": "running",
                    }
                ]
            ),
            returncode=0,
        )
        runners = self.driver.list_runners()
        assert runners[0].created_at is not None
        self.assertAlmostEqual(runners[0].created_at, 1788968853.355, places=2)

    @patch("subprocess.run")
    def test_list_runners_created_at_survives_simulated_process_restart(self, mock_run):
        # Simulates exactly the bug scenario: a brand new driver instance (as if the
        # Host VM Bridge process had just been restarted, wiping its in-memory
        # _runner_created_at cache) observes a VM that already existed. Its age must
        # come from OrbStack's own id, not from "now".
        vm_list = [
            {
                "id": "01M23DMQVBY90E2BVMYBA1GAZT",
                "name": "runzero-vm-amd64-el-j-herbful-858742",
                "state": "running",
            }
        ]
        mock_run.return_value = MagicMock(stdout=json.dumps(vm_list), returncode=0)

        fresh_driver = OrbStackVMDriver(distro="ubuntu:24.04")
        runners = fresh_driver.list_runners()
        assert runners[0].created_at is not None
        self.assertAlmostEqual(runners[0].created_at, 1788968853.355, places=2)

    @patch("subprocess.run")
    def test_list_runners_falls_back_when_id_is_not_a_ulid(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"id": "not-a-ulid", "name": "runzero-vm-amd64-el-j-run-zero-abc", "state": "running"}]),
            returncode=0,
        )
        before = time.time()
        runners = self.driver.list_runners()
        after = time.time()
        created_at = runners[0].created_at
        assert created_at is not None
        self.assertGreaterEqual(created_at, before)
        self.assertLessEqual(created_at, after)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_wires_cache_mounts_into_setup_script(self, mock_run, mock_popen):
        # Regression test for issue #10: cache_mounts used to be accepted and silently
        # discarded by this driver. It must now show up as a real bind-mount in the
        # script executed inside the cloned VM.
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),  # orbctl clone
        ]
        name = self.driver.spawn_runner(
            repo="el-j/run-zero",
            arch="amd64",
            access_token="token",
            cache_mounts={"/Users/dev/.local-github-runner/cache/npm": "/home/runner/.npm"},
        )
        self.assertIsNotNone(name)
        assert name is not None
        popen_args = mock_popen.call_args[0][0]
        self.assertEqual(popen_args[:5], ["orb", "-m", name, "-u", "runner"])
        setup_script = popen_args[-1]
        self.assertIn(
            "sudo mount --bind /mnt/mac/Users/dev/.local-github-runner/cache/npm /home/runner/.npm",
            setup_script,
        )
        # The cache env is exported before run.sh (#66-#68) ...
        env_at = setup_script.index("export PLAYWRIGHT_BROWSERS_PATH=/home/runner/.cache/ms-playwright")
        self.assertLess(env_at, setup_script.index("./run.sh"))
        self.assertIn("export pnpm_config_store_dir=/home/runner/.local/share/pnpm/store", setup_script)
        # ... and no recursive chown/chmod walks the host-backed caches after mounting (#67).
        after_mounts = setup_script[setup_script.index("mount --bind") :]
        self.assertNotIn("chown -R", after_mounts)
        self.assertNotIn("chmod -R", after_mounts)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_omits_cache_mount_lines_when_no_mounts(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertNotIn("mount --bind", setup_script)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_wires_pip_and_cargo_proxies_when_enabled(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token", proxies_enabled=True)
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertIn("export NPM_CONFIG_REGISTRY=http://host.orb.internal:49501/", setup_script)
        self.assertIn("export pnpm_config_registry=http://host.orb.internal:49501/", setup_script)
        self.assertIn('export PIP_INDEX_URL="http://host.orb.internal:49507/root/pypi/+simple/"', setup_script)
        self.assertIn('export UV_INDEX_URL="http://host.orb.internal:49507/root/pypi/+simple/"', setup_script)
        # pip refuses a plain-HTTP non-localhost index without this (verified live).
        self.assertIn('export PIP_TRUSTED_HOST="host.orb.internal"', setup_script)
        self.assertIn('Acquire::http::Proxy "http://host.orb.internal:49503";', setup_script)
        # Cargo has no working single-URL env var for a custom [source.*] table
        # (verified live) -- must write a real ~/.cargo/config.toml instead.
        self.assertIn("cat > /home/runner/.cargo/config.toml", setup_script)
        self.assertIn('replace-with = "kellnr-proxy"', setup_script)
        self.assertIn(
            'registry = "sparse+http://host.orb.internal:49506/api/v1/cratesio/"',
            setup_script,
        )

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_omits_proxy_wiring_when_disabled(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token", proxies_enabled=False)
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertNotIn("PIP_INDEX_URL", setup_script)
        self.assertNotIn("kellnr-proxy", setup_script)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_skips_duplicate_build_while_already_building(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),  # list VMs
        ]
        self.driver._backoff.in_progress.add("amd64")
        with patch.object(self.driver, "_build_base_image_async") as mock_async_build:
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)
        mock_async_build.assert_not_called()

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_does_not_reannounce_build_during_cooldown(self, mock_run, mock_popen):
        # spawn_runner()'s "Building it in the background" message implies an
        # attempt is actually starting -- must not print (or start one) while
        # a backoff cooldown from a prior failure is still in effect.
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),  # list VMs
        ]
        self.driver._backoff.retry_after["amd64"] = time.monotonic() + 60
        with patch.object(self.driver, "_build_base_image_async") as mock_async_build:
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)
        mock_async_build.assert_not_called()

    @patch("subprocess.run")
    def test_spawn_runner_failure(self, mock_run):
        # Root cause of issue #20's reproduction: with subprocess.run failing on
        # every call, _list_vm_names() reports no VMs -> base_image_exists() is
        # False -> spawn_runner() used to kick off a REAL _build_base_image_async
        # background thread here (unmocked), which then kept calling the
        # module-global subprocess.run via several real time.sleep-gated retry
        # loops for a couple of real seconds -- long after this test method (and
        # its @patch("subprocess.run") scope) had already returned, corrupting
        # whichever later test's own subprocess.run mock happened to be active by
        # then. This test only cares about spawn_runner()'s own return value
        # under a subprocess failure, not the async-build machinery (that has
        # its own dedicated tests), so mock it away entirely.
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl", stderr=b"Out of memory")
        with patch.object(self.driver, "_build_base_image_async") as mock_async_build:
            name = self.driver.spawn_runner(repo="el-j/run-zero")
        self.assertIsNone(name)
        mock_async_build.assert_called_once_with("arm64")

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="r1", name="runzero-vm-dead", status="stopped", state="exited", target_repo="", target_arch="arm64", backend="orbstack-vm"),
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runzero-vm-dead")
        self.driver.cleanup_all()

    @patch("subprocess.run")
    def test_prune_exited_ignores_stopped_runner_older_than_fast_failure_window(self, mock_run):
        # A clone that ran for a while before stopping (e.g. a real completed job)
        # is not evidence of a network failure and must not count toward the backoff.
        mock_run.return_value = MagicMock(returncode=0)
        old_runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-old",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 3600,
        )
        self.driver.prune_exited([old_runner])
        self.assertEqual(self.driver._spawn_failure_counts.get("amd64", 0), 0)

    @patch("subprocess.run")
    def test_prune_exited_ignores_stopped_runner_within_startup_grace_period(self, mock_run):
        # A newly cloned VM takes a few seconds to boot; if inspected during the
        # startup grace period (<15s), it must not be deleted or counted as a failure.
        mock_run.return_value = MagicMock(returncode=0)
        booting_runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-booting",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 5,
        )
        self.driver.prune_exited([booting_runner])
        self.assertEqual(self.driver._spawn_failure_counts.get("amd64", 0), 0)
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_prune_exited_counts_stopped_runner_younger_than_fast_failure_window(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        young_dead_runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-young",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 25,
        )
        self.driver.prune_exited([young_dead_runner])
        self.assertEqual(self.driver._spawn_failure_counts.get("amd64", 0), 1)

    @patch("subprocess.run")
    def test_prune_exited_resets_failure_count_when_a_clone_survives(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.driver._spawn_failure_counts["amd64"] = 2
        healthy_runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-healthy",
            status="running",
            state="running",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 3600,
        )
        self.driver.prune_exited([healthy_runner])
        self.assertEqual(self.driver._spawn_failure_counts.get("amd64", 0), 0)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_backs_off_after_consecutive_fast_failures(self, mock_run, mock_popen):
        # Regression test for the 2026-09-09 incident: OrbStack clones that never got a
        # network address were reclone'd every ~10s poll forever (355 clones in under 20
        # minutes, none of which could ever register). After MAX_CONSECUTIVE_FAST_FAILURES
        # stopped-while-still-young clones in a row, spawn_runner() must stop cloning for
        # that arch instead of repeating the same doomed attempt on every poll.
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]))
        for _ in range(3):
            dead_runner = RunnerInfo(
                id="r",
                name="runzero-vm-amd64-x",
                status="stopped",
                state="exited",
                target_repo="",
                target_arch="amd64",
                backend="orbstack-vm",
                created_at=time.time() - 25,
            )
            self.driver.prune_exited([dead_runner])

        mock_run.reset_mock()
        result = self.driver.spawn_runner(repo="el-j/herbful", arch="amd64", access_token="tok")

        self.assertIsNone(result)
        mock_popen.assert_not_called()
        clone_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "clone"]]
        self.assertEqual(clone_calls, [])

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_resumes_once_cooldown_elapses(self, mock_run, mock_popen):
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]))
        for _ in range(3):
            dead_runner = RunnerInfo(
                id="r",
                name="runzero-vm-amd64-x",
                status="stopped",
                state="exited",
                target_repo="",
                target_arch="amd64",
                backend="orbstack-vm",
                created_at=time.time() - 25,
            )
            self.driver.prune_exited([dead_runner])
        self.assertGreater(self.driver._spawn_cooldown_remaining("amd64"), 0)

        # Simulate the cooldown window having fully elapsed.
        self.driver._spawn_retry_after["amd64"] = time.monotonic() - 1

        mock_run.reset_mock()
        with patch.object(self.driver, "base_image_exists", return_value=True):
            result = self.driver.spawn_runner(repo="el-j/herbful", arch="amd64", access_token="tok")

        self.assertIsNotNone(result)
        mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_for_org_target(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),  # orbctl clone
        ]
        name = self.driver.spawn_runner(org="my-org", arch="amd64", access_token="token")
        self.assertIsNotNone(name)
        assert name is not None
        self.assertEqual(self.driver._runner_repos.get(name), "my-org")

    @patch("subprocess.run")
    def test_destroy_runner_returns_false_on_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        self.assertFalse(self.driver.destroy_runner("runzero-vm-el-j-run-zero-abc123"))

    @patch("subprocess.run")
    def test_cleanup_all_destroys_orbstack_backed_runners(self, mock_run):
        # Regression guard: cleanup_all() must only destroy runners whose
        # backend is actually "orbstack-vm" -- list_runners() itself is real
        # here (only subprocess.run is mocked), so this exercises the real
        # filtering loop rather than relying on list_runners() failing
        # closed to an empty list.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-amd64-el-j-run-zero-abc123", "state": "stopped"}]), returncode=0)
        self.driver.cleanup_all()
        delete_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "delete"]]
        self.assertEqual(len(delete_calls), 1)
        self.assertEqual(delete_calls[0][0][0], ["orbctl", "delete", "-f", "runzero-vm-amd64-el-j-run-zero-abc123"])

    def test_reset_spawn_cooldown_clears_specific_arch(self):
        self.driver._spawn_failure_counts = {"arm64": 3, "amd64": 2}
        self.driver._spawn_retry_after = {"arm64": 123.0, "amd64": 456.0}
        self.driver.reset_spawn_cooldown("arm64")
        self.assertEqual(self.driver._spawn_failure_counts["arm64"], 0)
        self.assertNotIn("arm64", self.driver._spawn_retry_after)
        self.assertEqual(self.driver._spawn_failure_counts["amd64"], 2)
        self.assertIn("amd64", self.driver._spawn_retry_after)

    def test_reset_spawn_cooldown_clears_all_arches_when_none_given(self):
        self.driver._spawn_failure_counts = {"arm64": 3, "amd64": 2}
        self.driver._spawn_retry_after = {"arm64": 123.0, "amd64": 456.0}
        self.driver.reset_spawn_cooldown()
        self.assertEqual(self.driver._spawn_failure_counts, {"arm64": 0, "amd64": 0})
        self.assertEqual(self.driver._spawn_retry_after, {})

    def test_init_default_distro_is_ubuntu_2404(self):
        driver = OrbStackVMDriver()
        self.assertEqual(driver.distro, "ubuntu:24.04")

    def test_vm_created_at_from_ulid_boundary_lengths(self):
        # Regression guard for the `len(vm_id) < 10` guard: boundary mutants
        # (`<=10`, `<11`, `or`->`and`) all passed silently because every existing
        # caller only ever exercises a real (26-char) ULID or the empty-string
        # fallback path. Directly pin the length-10 boundary here.
        from drivers.orbstack_vm_driver import _vm_created_at_from_ulid

        # Exactly 10 chars (all valid Crockford base32) must decode, not bounce.
        self.assertIsNotNone(_vm_created_at_from_ulid("01M23DMQVB"))
        # Fewer than 10 chars must bounce to None, regardless of content.
        self.assertIsNone(_vm_created_at_from_ulid("01M23"))
        self.assertIsNone(_vm_created_at_from_ulid(""))

    def test_build_cooldown_remaining_is_exactly_zero_with_no_prior_failure(self):
        # Regression guard: `.get(orb_arch, 0.0)` -- a mutant defaulting to 1.0
        # would report a phantom 1-second cooldown for an arch that never failed.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        self.assertEqual(driver._backoff.remaining("amd64"), 0.0)

    def test_list_vm_names_calls_orbctl_list_with_expected_args(self):
        # Regression guard: _list_vm_names() had ZERO direct tests despite its own
        # docstring explaining exactly why its retry-on-transient-failure behavior
        # matters (a false "no VMs" reading used to trigger build_base_image() to
        # destroy and rebuild a perfectly healthy golden image). Pinning the exact
        # subprocess.run call kills every kwarg-value/kwarg-omission/string-literal
        # mutant on this call in one shot.
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=json.dumps([]), returncode=0)
            self.driver._list_vm_names()
        mock_run.assert_called_once_with(
            ["orbctl", "list", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

    def test_list_vm_names_retries_exactly_three_times_then_gives_up(self):
        with patch("subprocess.run") as mock_run, patch("time.sleep") as mock_sleep:
            mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl", stderr=b"boom")
            names = self.driver._list_vm_names()
        self.assertEqual(names, [])
        self.assertEqual(mock_run.call_count, 3)
        # Sleeps between attempts only -- 2 sleeps for 3 attempts, never a
        # pointless sleep after the final (already-exhausted) attempt.
        self.assertEqual(mock_sleep.call_count, 2)

    def test_list_vm_names_treats_empty_stdout_as_no_vms(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0)
            names = self.driver._list_vm_names()
        self.assertEqual(names, [])

    def test_list_vm_names_defaults_missing_name_field_to_empty_string(self):
        # _list_vm_names()'s own return type is List[str] -- a vm dict missing
        # "name" must degrade to "", not None (which would break a caller's
        # .startswith() and violate the declared return type).
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=json.dumps([{"state": "running"}]), returncode=0)
            names = self.driver._list_vm_names()
        self.assertEqual(names, [""])

    def test_record_spawn_outcome_backoff_formula_exact_values(self):
        # Regression guard: `min(30 * (2 ** (failures - MAX_CONSECUTIVE_FAST_FAILURES)), 900)`
        # had zero value-level assertions (only that a cooldown was reached at
        # all), so a wrong base, wrong exponent sign/operator, or wrong cap
        # all survived -- same backoff-formula blind spot found and fixed for
        # build_base_image_async in this same module.
        expected_by_failure_count = {3: 30, 4: 60, 5: 120, 6: 240, 10: 900}
        for failures, expected_cooldown in expected_by_failure_count.items():
            driver = OrbStackVMDriver(distro="ubuntu:24.04")
            driver._spawn_failure_counts["amd64"] = failures - 1
            with patch("time.monotonic", return_value=1000.0), patch("builtins.print"):
                driver._record_spawn_outcome("amd64", got_network=False)
            self.assertAlmostEqual(
                driver._spawn_retry_after["amd64"] - 1000.0,
                expected_cooldown,
                msg=f"failures={failures}",
            )

    def test_record_spawn_outcome_success_pops_only_that_archs_retry_after(self):
        # Regression guard: `.pop(orb_arch, None)` -- a mutant popping a
        # hardcoded None key instead would leave a stale cooldown in place
        # for the arch that just proved itself healthy, needlessly blocking
        # spawn_runner() for up to 900s longer than necessary.
        self.driver._spawn_retry_after = {"amd64": 12345.0, "arm64": 6789.0}
        self.driver._record_spawn_outcome("amd64", got_network=True)
        self.assertNotIn("amd64", self.driver._spawn_retry_after)
        self.assertIn("arm64", self.driver._spawn_retry_after)
        self.assertEqual(self.driver._spawn_retry_after["arm64"], 6789.0)

    def test_spawn_cooldown_remaining_is_exactly_zero_with_no_prior_failure(self):
        self.assertEqual(self.driver._spawn_cooldown_remaining("amd64"), 0.0)

    @patch("subprocess.run")
    def test_destroy_runner_success_returns_true_and_cleans_up_state(self, mock_run):
        # Regression guard: no existing test asserted the success return value
        # (a mutant hardcoding `return False` on success survived), nor that
        # the tracking dicts are cleaned up for the EXACT runner_id (a mutant
        # popping a hardcoded None key would leave stale state behind).
        mock_run.return_value = MagicMock(returncode=0)
        self.driver._runner_created_at["runzero-vm-dead"] = 123.0
        self.driver._runner_repos["runzero-vm-dead"] = "el-j/run-zero"
        result = self.driver.destroy_runner("runzero-vm-dead")
        self.assertTrue(result)
        mock_run.assert_called_once_with(["orbctl", "delete", "-f", "runzero-vm-dead"], check=True, capture_output=True)
        self.assertNotIn("runzero-vm-dead", self.driver._runner_created_at)
        self.assertNotIn("runzero-vm-dead", self.driver._runner_repos)

    def test_ensure_runtime_assets_normalizes_arch_variants_to_amd64(self):
        # Regression guard: `orb_arch = "arm64" if arch == "arm64" else "amd64"`
        # -- covers both the "arm64" literal mutant and the "amd64" fallback
        # literal mutant by checking which base image name gets probed.
        with patch.object(self.driver, "base_image_exists", return_value=True) as mock_exists:
            self.driver.ensure_runtime_assets("arm64")
            mock_exists.assert_called_with("arm64")
            self.driver.ensure_runtime_assets("x64")
            mock_exists.assert_called_with("amd64")
            self.driver.ensure_runtime_assets()  # default param
            mock_exists.assert_called_with("arm64")

    def test_ensure_runtime_assets_starts_build_only_when_not_building_and_not_cooling(self):
        # Regression guard: `if not already_building and cooldown_remaining <= 0`
        # -- an `and`->inverted mutant (`if already_building and ...`) would
        # NEVER start a build for a genuinely idle, missing image (the normal
        # case), and would nonsensically try to "start" a build for an arch
        # already flagged as building. No existing test called
        # ensure_runtime_assets() directly with already_building explicitly
        # toggled both ways.
        with patch.object(self.driver, "base_image_exists", return_value=False), patch.object(self.driver, "_build_base_image_async") as mock_build:
            self.driver.ensure_runtime_assets("arm64")
        mock_build.assert_called_once_with("arm64")

    def test_ensure_runtime_assets_does_not_start_build_while_already_building(self):
        self.driver._backoff.in_progress.add("arm64")
        with (
            patch.object(self.driver, "base_image_exists", return_value=False),
            patch.object(self.driver, "_build_base_image_async") as mock_build,
            patch("builtins.print") as mock_print,
        ):
            result = self.driver.ensure_runtime_assets("arm64")
        self.assertFalse(result)
        mock_build.assert_not_called()
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("currently building", printed)
        self.assertIn("retried on the next poll", printed)

    def test_ensure_runtime_assets_cooldown_message_content(self):
        self.driver._backoff.retry_after["arm64"] = time.monotonic() + 42
        with (
            patch.object(self.driver, "base_image_exists", return_value=False),
            patch.object(self.driver, "_build_base_image_async") as mock_build,
            patch("builtins.print") as mock_print,
        ):
            result = self.driver.ensure_runtime_assets("arm64")
        self.assertFalse(result)
        mock_build.assert_not_called()
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("cooling down for", printed)
        self.assertIn("runzero-vm-base-arm64", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    def test_ensure_runtime_assets_build_start_message_content(self):
        with (
            patch.object(self.driver, "base_image_exists", return_value=False),
            patch.object(self.driver, "_build_base_image_async"),
            patch("builtins.print") as mock_print,
        ):
            self.driver.ensure_runtime_assets("arm64")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("not found", printed)
        self.assertIn("runzero-vm-base-arm64", printed)

    @patch("subprocess.run")
    def test_list_runners_treats_active_state_as_running(self, mock_run):
        # Regression guard: `status_lower in ("running", "active")` -- "active"
        # was never exercised by any existing test (only "running" was), so a
        # mutant mangling the "active" literal survived.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-amd64-el-j-run-zero-abc", "state": "active"}]), returncode=0)
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "running")

    @patch("subprocess.run")
    def test_list_runners_derives_target_repo_at_exact_3_part_boundary(self, mock_run):
        # Regression guard: `if len(body_parts) >= 3` -- with a name whose
        # body splits into EXACTLY 3 parts (arch-repo-uniqueid), `>= 3` derives
        # a repo but `> 3`/`>= 4` mutants leave target_repo empty. Every
        # existing fixture used names with >3 parts, hiding this boundary.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-amd64-myrepo-abc123", "state": "running"}]), returncode=0)
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].target_repo, "myrepo")

    @patch("subprocess.run")
    def test_list_runners_id_and_status_fields_exact_values(self, mock_run):
        # Regression guard: no existing test asserted `.id`/`.status` at all
        # (only `.name`/`.state`/`.target_arch`/`.target_repo`) -- a mutant
        # hardcoding id=None or status=None, or swapping which raw field feeds
        # them, went completely undetected.
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"name": "runzero-vm-amd64-el-j-run-zero-abc", "state": "provisioning"}]),
            returncode=0,
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].id, "runzero-vm-amd64-el-j-run-zero-abc")
        self.assertEqual(runners[0].status, "provisioning")

    @patch("subprocess.run")
    def test_list_runners_exception_message_content(self, mock_run):
        mock_run.side_effect = RuntimeError("orbctl daemon unreachable")
        with patch("builtins.print") as mock_print:
            runners = self.driver.list_runners()
        self.assertEqual(runners, [])
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("Error listing VMs", printed)
        self.assertIn("orbctl daemon unreachable", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_list_runners_subprocess_exact_args(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([]), returncode=0)
        self.driver.list_runners()
        mock_run.assert_called_once_with(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)

    @patch("subprocess.run")
    def test_prune_exited_continues_past_non_orbstack_runner_to_next(self, mock_run):
        # Regression guard: `if r.backend != "orbstack-vm" or ...: continue`
        # -- a mutant turning this into `break` would abort the whole prune
        # pass the first time it saw ANY non-OrbStack-backed runner (e.g. a
        # Docker-backed one, in a mixed-engine fleet), silently leaving every
        # later OrbStack VM un-pruned.
        mock_run.return_value = MagicMock(returncode=0)
        docker_runner = RunnerInfo(
            id="d1",
            name="local-github-runner-abc",
            status="exited",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="docker",
            created_at=time.time() - 3600,
        )
        old_orbstack_runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-old",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 3600,
        )
        self.driver.prune_exited([docker_runner, old_orbstack_runner])
        delete_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "delete"]]
        self.assertEqual(delete_calls, [call(["orbctl", "delete", "-f", "runzero-vm-amd64-old"], check=True, capture_output=True)])

    @patch("subprocess.run")
    def test_prune_exited_continues_past_grace_period_runner_to_next(self, mock_run):
        # Same `continue`-not-`break` risk for the startup-grace-period guard.
        mock_run.return_value = MagicMock(returncode=0)
        booting_runner = RunnerInfo(
            id="b1",
            name="runzero-vm-amd64-booting",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 5,
        )
        old_runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-old",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 3600,
        )
        self.driver.prune_exited([booting_runner, old_runner])
        delete_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "delete"]]
        self.assertEqual(delete_calls, [call(["orbctl", "delete", "-f", "runzero-vm-amd64-old"], check=True, capture_output=True)])

    @patch("subprocess.run")
    def test_prune_exited_destroys_stopped_and_dead_states_too(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        for state in ("stopped", "dead"):
            mock_run.reset_mock()
            runner = RunnerInfo(
                id="r1",
                name=f"runzero-vm-amd64-{state}",
                status=state,
                state=state,
                target_repo="",
                target_arch="amd64",
                backend="orbstack-vm",
                created_at=time.time() - 3600,
            )
            self.driver.prune_exited([runner])
            delete_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "delete"]]
            self.assertEqual(len(delete_calls), 1, f"state={state!r} was not destroyed")

    @patch("subprocess.run")
    def test_prune_exited_deleting_message_content(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-old",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 3600,
        )
        with patch("builtins.print") as mock_print:
            self.driver.prune_exited([runner])
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("Deleting stopped VM", printed)
        self.assertIn("runzero-vm-amd64-old", printed)

    def test_prune_exited_does_not_record_healthy_outcome_for_non_running_old_entry(self):
        # Regression guard: `elif r.state == "running" and age is not None and
        # age >= FAST_FAILURE_WINDOW_SECONDS` -- an `and`->`or` mutant on
        # either operator would spuriously call _record_spawn_outcome(healthy)
        # for an old runner in some OTHER (non-"running", non-exited/stopped/
        # dead) state, e.g. "pending", resetting a real failure streak based
        # on a runner that never proved it actually got a network address.
        pending_old_runner = RunnerInfo(
            id="p1",
            name="runzero-vm-amd64-stuck",
            status="creating",
            state="pending",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 3600,
        )
        self.driver._spawn_failure_counts["amd64"] = 2
        with patch.object(self.driver, "_record_spawn_outcome") as mock_record:
            self.driver.prune_exited([pending_old_runner])
        mock_record.assert_not_called()

    def test_prune_exited_records_got_network_true_exactly(self):
        healthy_runner = RunnerInfo(
            id="h1",
            name="runzero-vm-amd64-healthy",
            status="running",
            state="running",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 3600,
        )
        with patch.object(self.driver, "_record_spawn_outcome") as mock_record:
            self.driver.prune_exited([healthy_runner])
        mock_record.assert_called_once_with("amd64", got_network=True)

    @patch("subprocess.run")
    def test_prune_exited_records_got_network_false_exactly(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        young_dead_runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-young",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 25,
        )
        with patch.object(self.driver, "_record_spawn_outcome") as mock_record:
            self.driver.prune_exited([young_dead_runner])
        mock_record.assert_called_once_with("amd64", got_network=False)

    @patch("subprocess.run")
    def test_prune_exited_startup_grace_period_boundary_is_strictly_less_than(self, mock_run):
        # Regression guard: `age < STARTUP_GRACE_PERIOD_SECONDS` -- at EXACTLY
        # the boundary, the runner must NOT be protected (age is not < the
        # threshold), so it proceeds to be evaluated as dead/stopped.
        mock_run.return_value = MagicMock(returncode=0)
        runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-boundary",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - STARTUP_GRACE_PERIOD_SECONDS,
        )
        self.driver.prune_exited([runner])
        delete_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "delete"]]
        self.assertEqual(len(delete_calls), 1)

    def test_prune_exited_fast_failure_window_boundary_is_strictly_less_than(self):
        # Regression guard: `age < FAST_FAILURE_WINDOW_SECONDS` -- at EXACTLY
        # the boundary, this must NOT count as a fast failure (a `<=` mutant
        # would).
        runner = RunnerInfo(
            id="r1",
            name="runzero-vm-amd64-boundary",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - FAST_FAILURE_WINDOW_SECONDS,
        )
        with patch("subprocess.run", return_value=MagicMock(returncode=0)), patch.object(self.driver, "_record_spawn_outcome") as mock_record:
            self.driver.prune_exited([runner])
        mock_record.assert_not_called()

    def test_reset_spawn_cooldown_tolerates_arch_with_no_pending_retry(self):
        # Regression guard: `.pop(a, None)` -- a mutant dropping the default
        # (`.pop(a,)`, i.e. plain `.pop(a)`) raises KeyError for an arch that
        # has a failure count but never actually entered cooldown (failures <
        # MAX_CONSECUTIVE_FAST_FAILURES). No existing test exercised that
        # combination.
        self.driver._spawn_failure_counts["amd64"] = 1
        self.assertNotIn("amd64", self.driver._spawn_retry_after)
        self.driver.reset_spawn_cooldown("amd64")  # must not raise
        self.assertEqual(self.driver._spawn_failure_counts["amd64"], 0)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_default_labels_include_rosetta_for_amd64(self, mock_run, mock_popen):
        # Regression guard: `if arch in ("amd64", "x64", "x86_64"): default_labels
        # += ",rosetta"` -- a mutant inverting the membership check, or using `=`
        # instead of `+=` (discarding "self-hosted,local,vm,amd64"), or mangling
        # the "amd64"/"x64"/"x86_64" literals, all survived because no test ever
        # inspected the actual labels value reaching the runner registration
        # script.
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertIn("self-hosted,local,vm,amd64,rosetta", setup_script)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_default_labels_omit_rosetta_for_arm64(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-arm64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="token")
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertIn("self-hosted,local,vm,arm64", setup_script)
        self.assertNotIn("rosetta", setup_script)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_job_labels_are_merged_with_defaults(self, mock_run, mock_popen):
        # #46: union of the VM defaults (incl. routing labels like "vm"/"rosetta") and the job's labels.
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token", labels="my,custom,vm")
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertIn("--labels self-hosted,local,vm,amd64,rosetta,my,custom", setup_script)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_registration_snippet_called_with_exact_args(self, mock_run, mock_popen):
        # Regression guard: the 7-positional-arg call to registration_and_run_snippet()
        # had zero exact-argument assertions -- an argument swap/omission/None
        # substitution on api_base/runner_url/access_token/vm_name/runner_labels/
        # proxy_env_block/cache_mount_block all survived.
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        with patch("drivers.orbstack_vm_driver.registration_and_run_snippet", return_value="REG_SNIPPET") as mock_reg:
            name = self.driver.spawn_runner(
                repo="el-j/run-zero",
                arch="amd64",
                access_token="tok123",
                cache_mounts=None,
                proxies_enabled=False,
            )
        self.create_registration_token.assert_called_once_with("el-j/run-zero", None, "tok123")
        mock_reg.assert_called_once_with(
            "https://github.com/el-j/run-zero",
            "reg-token",
            name,
            "self-hosted,local,vm,amd64,rosetta",
            "",
            "",
            runner_env={"RUNZERO": "1", "RUNNER_TOOL_CACHE": "/opt/hostedtoolcache", "AGENT_TOOLSDIRECTORY": "/opt/hostedtoolcache"},
        )

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_org_target_api_base_and_url(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        with patch("drivers.orbstack_vm_driver.registration_and_run_snippet", return_value="REG_SNIPPET") as mock_reg:
            self.driver.spawn_runner(org="my-org", arch="amd64", access_token="tok123")
        called_args = mock_reg.call_args[0]
        self.assertEqual(called_args[0], "https://github.com/my-org")
        self.create_registration_token.assert_called_once_with(None, "my-org", "tok123")

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_cooldown_message_content_and_exact_failure_count(self, mock_run, mock_popen):
        self.driver._spawn_failure_counts["amd64"] = 5
        self.driver._spawn_retry_after["amd64"] = time.monotonic() + 42
        with patch("builtins.print") as mock_print:
            result = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        self.assertIsNone(result)
        mock_run.assert_not_called()
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("cooling down for", printed)
        self.assertIn("5", printed)
        self.assertIn("consecutive clones failed", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_spawning_message_content(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        with patch("builtins.print") as mock_print:
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        printed_calls = [" ".join(str(a) for a in c.args) for c in mock_print.call_args_list]
        spawn_msgs = [p for p in printed_calls if "Spawning ephemeral" in p]
        self.assertEqual(len(spawn_msgs), 1)
        self.assertIn("[AMD64]", spawn_msgs[0])
        self.assertIn(name, spawn_msgs[0])
        self.assertIn("runzero-vm-base-amd64", spawn_msgs[0])

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_clone_subprocess_exact_args_and_state_updates(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        before = time.time()
        name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        assert name is not None
        after = time.time()
        mock_run.assert_called_with(["orbctl", "clone", "runzero-vm-base-amd64", name], check=True, capture_output=True)
        self.assertIn(name, self.driver._runner_created_at)
        self.assertGreaterEqual(self.driver._runner_created_at[name], before)
        self.assertLessEqual(self.driver._runner_created_at[name], after)
        self.assertEqual(self.driver._runner_repos[name], "el-j/run-zero")

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_tracks_org_in_runner_repos_when_no_repo_given(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        name = self.driver.spawn_runner(org="my-org", arch="amd64", access_token="tok")
        assert name is not None
        self.assertEqual(self.driver._runner_repos[name], "my-org")

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_popen_exact_args(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        mock_popen.assert_called_once()
        call_args, call_kwargs = mock_popen.call_args
        self.assertEqual(call_args[0][:5], ["orb", "-m", name, "-u", "runner"])
        self.assertEqual(call_args[0][5], "bash")
        self.assertEqual(call_args[0][6], "-c")
        self.assertEqual(call_kwargs.get("stdout"), subprocess.DEVNULL)
        self.assertEqual(call_kwargs.get("stderr"), subprocess.DEVNULL)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_clone_failure_decodes_bytes_stderr(self, mock_run, mock_popen):
        error = subprocess.CalledProcessError(1, ["orbctl", "clone"], stderr=b"no space left on device")
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            error,
        ]
        with patch("builtins.print") as mock_print:
            result = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        self.assertIsNone(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("no space left on device", printed)
        self.assertIn("Error creating VM", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_clone_failure_falls_back_to_str_when_no_stderr(self, mock_run, mock_popen):
        # Regression guard for the same "ternary fallback to str(e)" pattern
        # as build_base_image()'s CalledProcessError handling -- every
        # existing clone-failure test used real bytes stderr.
        error = subprocess.CalledProcessError(1, ["orbctl", "clone"], stderr=None)
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            error,
        ]
        with patch("builtins.print") as mock_print:
            result = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        self.assertIsNone(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn(str(error), printed)


if __name__ == "__main__":
    unittest.main()
