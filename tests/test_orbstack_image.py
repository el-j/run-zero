"""
Tests for OrbStack golden base images: build, staging promotion, idle stop, orphan resume,
and the async, backoff-gated build trigger (drivers.orbstack_image + OrbStackVMDriver hooks).
"""

import json
import os
import subprocess
import sys
import threading
import time
import unittest
from typing import Any
from unittest.mock import MagicMock, call, mock_open, patch

from orbstack_test_base import OrbStackDriverTestCase

from drivers import RunnerInfo
from drivers.orbstack_templates import (
    docker_engine_snippet,
    runner_download_snippet,
)
from drivers.orbstack_vm_driver import (
    OrbStackVMDriver,
)
from drivers.sizing import HostCapacity


class TestOrbStackImages(OrbStackDriverTestCase):
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
            stdout=json.dumps(
                [
                    {"name": "runzero-vm-arm64-el-j-run-zero-aaa111", "state": "creating"},
                    {"name": "runzero-vm-arm64-el-j-run-zero-bbb222", "state": "provisioning"},
                ]
            ),
            returncode=0,
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "pending")
        self.assertEqual(runners[1].state, "pending")

    def test_base_image_name(self):
        self.assertEqual(self.driver.base_image_name("amd64"), "runzero-vm-base-amd64")

    @patch("subprocess.run")
    def test_base_image_exists_true(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0)
        self.assertTrue(self.driver.base_image_exists("amd64"))

    @patch("subprocess.run")
    def test_base_image_exists_false(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([]), returncode=0)
        self.assertFalse(self.driver.base_image_exists("amd64"))

    def test_list_runners_excludes_base_image(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout=json.dumps(
                    [
                        {"name": "runzero-vm-base-amd64", "state": "stopped"},
                        {"name": "runzero-vm-amd64-el-j-run-zero-abc123", "state": "running"},
                    ]
                ),
                returncode=0,
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
        assert name is not None
        clone_call = mock_run.call_args_list[1]
        self.assertEqual(clone_call[0][0][:2], ["orbctl", "clone"])

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_builds_base_image_in_background_when_missing(self, mock_run, mock_popen):
        # base_image_exists() -> [] (no golden image yet). spawn_runner must NOT
        # block the caller building it in-line (that used to freeze the whole
        # autoscaler poll loop for up to 30 min) -- it kicks off the build on a
        # background thread and returns None immediately so this poll's other
        # jobs/repos still get served; the job is retried on a later poll.
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),  # list VMs
        ]
        with patch.object(self.driver, "_build_base_image_async") as mock_async_build:
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)
        mock_async_build.assert_called_once_with("amd64")
        mock_popen.assert_not_called()

    def test_build_base_image_async_runs_in_background_and_dedupes_per_arch(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        calls = []

        def fake_build(arch):
            calls.append(arch)
            time.sleep(0.05)
            return True

        with patch.object(driver, "build_base_image", side_effect=fake_build):
            driver._build_base_image_async("amd64")
            # Called again immediately, while the first build is still "in
            # flight" -- must be deduped, not queue a second build.
            driver._build_base_image_async("amd64")

            # Join (not just poll shared state) so the background thread is
            # provably finished -- and thus can never leak into a later test
            # -- before this mock.patch context exits. See issue #20.
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

        self.assertEqual(calls, ["amd64"])
        self.assertNotIn("amd64", driver._backoff.in_progress)

    def test_join_background_build_threads_reports_false_for_still_running_thread(self):
        # join_background_build_threads() must distinguish "finished" from
        # "gave up waiting" -- a caller (like a test tearDown) that treats a
        # timed-out join as success would defeat the whole point of issue
        # #20's fix: it needs an honest signal that a thread is still alive.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        started = threading.Event()
        release = threading.Event()

        def slow_build(arch):
            started.set()
            release.wait(timeout=5.0)
            return True

        with patch.object(driver, "build_base_image", side_effect=slow_build):
            driver._build_base_image_async("amd64")
            self.assertTrue(started.wait(timeout=5.0), "background thread never started")

            # Still blocked on release -- a short timeout must report False,
            # not hang indefinitely or silently claim success.
            self.assertFalse(driver.join_background_build_threads(timeout=0.05))

            release.set()
            # Let it actually finish so no thread survives past this test.
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

    def test_build_base_image_async_backs_off_after_repeated_failures(self):
        # Regression test: a non-transient failure (confirmed live -- OrbStack
        # itself failing every `orbctl create`, no run-zero code involved)
        # used to retry on every single poll tick forever. A failed build must
        # now enter a cooldown so an immediate follow-up poll does NOT start
        # another attempt.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        calls = []

        def fake_build(arch):
            calls.append(arch)
            return False

        with patch.object(driver, "build_base_image", side_effect=fake_build):
            self._run_async_build_and_wait(driver, "amd64")
            self.assertEqual(calls, ["amd64"])
            self.assertEqual(driver._backoff.failure_counts["amd64"], 1)
            self.assertGreater(driver._backoff.remaining("amd64"), 0)

            # Immediate follow-up poll (what the real poll loop does every
            # ~15-20s) must be a no-op while the cooldown is in effect.
            driver._build_base_image_async("amd64")
            self.assertEqual(calls, ["amd64"])

    def test_build_base_image_async_cooldown_escalates_and_resets_on_success(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        outcomes = iter([False, False])

        with patch.object(driver, "build_base_image", side_effect=lambda arch: next(outcomes)):
            self._run_async_build_and_wait(driver, "amd64")
            first_cooldown = driver._backoff.remaining("amd64")

            # Force the cooldown to have already elapsed so the second
            # attempt is actually allowed to run.
            driver._backoff.retry_after["amd64"] = time.monotonic()
            self._run_async_build_and_wait(driver, "amd64")
            second_cooldown = driver._backoff.remaining("amd64")

        self.assertEqual(driver._backoff.failure_counts["amd64"], 2)
        self.assertGreater(second_cooldown, first_cooldown)

        # A subsequent success must clear both the failure count and cooldown
        # -- a build that starts working again shouldn't stay throttled.
        driver._backoff.retry_after["amd64"] = time.monotonic()
        with patch.object(driver, "build_base_image", return_value=True):
            self._run_async_build_and_wait(driver, "amd64")
        self.assertEqual(driver._backoff.failure_counts["amd64"], 0)
        self.assertEqual(driver._backoff.remaining("amd64"), 0.0)

    @patch("subprocess.run")
    def test_build_base_image_missing_script_fails_gracefully(self, mock_run):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        driver.images._provision_script_path = "/nonexistent/provision-toolchain.sh"
        result = driver.build_base_image("amd64")
        self.assertFalse(result)
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_build_base_image_skips_when_already_exists(self, mock_run):
        # Guards against ever deleting/rebuilding a golden image that's already
        # there, regardless of why build_base_image() got called.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0)
        result = self.driver.build_base_image("amd64")
        self.assertTrue(result)
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[0][0][:2], ["orbctl", "list"])

    @patch("subprocess.run")
    def test_build_base_image_create_failure(self, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),  # base_image_exists() -> False
            MagicMock(returncode=0),  # orbctl delete -f (no-op)
            subprocess.CalledProcessError(1, ["orbctl", "create"], stderr=b"Out of memory"),
        ]
        result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_success(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "list"]:
                return MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
            elif cmd[:2] == ["orbctl", "rename"]:
                return MagicMock(returncode=0)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        with patch.object(self.driver, "base_image_exists", return_value=False), patch.object(self.driver.images, "_stop_vm", return_value=True):
            result = self.driver.build_base_image("amd64")
            self.assertTrue(result)
            rename_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "rename"]]
            self.assertEqual(len(rename_calls), 1)
            self.assertEqual(rename_calls[0][0][0], ["orbctl", "rename", "runzero-vm-base-amd64-building", "runzero-vm-base-amd64"])

    @patch("subprocess.run")
    def test_build_base_image_rename_failure(self, mock_run):
        # When rename fails across all retries and clone fallback also fails,
        # build_base_image returns False.
        mock_run.return_value = MagicMock(returncode=1, stderr=b"persistent error", stdout=json.dumps([]))
        with patch.object(self.driver, "base_image_exists", return_value=False), patch.object(self.driver.images, "_stop_vm", return_value=True):
            result = self.driver.build_base_image("amd64")
            self.assertFalse(result)

    @patch("subprocess.run")
    def test_promote_staging_to_base_clone_fallback(self, mock_run):
        # If orbctl rename fails with error, fallback to orbctl clone succeeds
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "rename"]:
                return MagicMock(returncode=1, stderr="rename locked")
            elif cmd[:2] == ["orbctl", "clone"] or cmd[:2] == ["orbctl", "delete"]:
                return MagicMock(returncode=0)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        with patch.object(self.driver.images, "_stop_vm", return_value=True):
            res = self.driver.images._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
            self.assertTrue(res)

    @patch("subprocess.run")
    def test_base_image_exists_auto_promotes_completed_staging(self, mock_run):
        # If base image is missing but completed staging VM exists, base_image_exists auto-promotes it
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
        with (
            patch.object(self.driver.images, "_is_staging_provisioned", return_value=True),
            patch.object(self.driver.images, "_promote_staging_to_base", return_value=True) as mock_promote,
        ):
            self.assertTrue(self.driver.base_image_exists("amd64"))
            mock_promote.assert_called_once_with("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")

    @patch("subprocess.run")
    def test_build_base_image_provision_timeout(self, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),  # base_image_exists() -> False
            MagicMock(returncode=0),  # orbctl delete -f (no-op)
            MagicMock(returncode=0),  # orbctl create
            subprocess.TimeoutExpired(cmd="orb", timeout=1800),
        ]
        result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_without_base_image_defers_to_background_build(self, mock_run, mock_popen):
        # No golden base image yet -- spawn_runner must not block on a
        # synchronous build; it defers to the background build and returns
        # None so the caller retries this job on a later poll.
        mock_run.return_value = MagicMock(stdout=json.dumps([]), returncode=0)
        with patch.object(self.driver, "_build_base_image_async") as mock_async_build:
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)
        mock_async_build.assert_called_once_with("amd64")

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_stops_idle_running_base(self, mock_run):
        mock_run.side_effect = [
            MagicMock(
                stdout=json.dumps(
                    [  # _list_vm_names() in ensure_base_images_stopped
                        {"name": "runzero-vm-base-amd64", "state": "running"},
                        {"name": "runzero-vm-amd64-el-j-run-zero-abc", "state": "running"},
                    ]
                ),
                returncode=0,
            ),
            MagicMock(returncode=0),  # orbctl stop
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
        ]
        self.driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(len(stop_calls), 1)
        self.assertEqual(stop_calls[0][0][0], ["orbctl", "stop", "runzero-vm-base-amd64"])

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_leaves_stopped_base_alone(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0)
        self.driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(stop_calls, [])

    def test_ensure_base_images_stopped_skips_arch_currently_being_built(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        driver._backoff.in_progress.add("amd64")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "running"}]), returncode=0)
            driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(stop_calls, [])

    def test_ensure_base_images_stopped_skips_staging_vm_currently_being_built(self):
        # Regression test: the staging VM is named "<base_name>-building" while
        # a build is in progress, and is legitimately running for the entire
        # 15-25 min provisioning window. Without stripping the "-building"
        # suffix before checking _building_arches, this would stop the VM out
        # from under its own provisioning script.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        driver._backoff.in_progress.add("amd64")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "running"}]), returncode=0)
            driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(stop_calls, [])

    def test_ensure_base_images_stopped_resumes_orphaned_stopped_staging_vm(self):
        # Regression test: a "-building" VM with no live builder tracked in
        # THIS process (e.g. the bridge process was restarted mid-build, a
        # normal maintenance operation -- the background thread dies with the
        # old process, but the half-provisioned staging VM survives on disk)
        # used to get silently woken up by _is_staging_provisioned()'s exec
        # probe (confirmed live: `orb -m <stopped-vm> exec ...` boots a
        # stopped VM as a side effect) and then stopped again next tick --
        # forever, with zero provisioning progress. A stopped, untracked
        # "-building" VM must now resume its build instead of being probed.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        with (
            patch("subprocess.run") as mock_run,
            patch.object(driver.images, "_is_staging_provisioned") as mock_probe,
            patch.object(driver, "_build_base_image_async") as mock_resume,
        ):
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "stopped"}]), returncode=0)
            driver.ensure_base_images_stopped()
        mock_probe.assert_not_called()
        mock_resume.assert_called_once_with("arm64")
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(stop_calls, [])

    def test_ensure_base_images_stopped_probes_running_orphaned_staging_vm(self):
        # A "-building" VM that's already running (not woken by our own probe)
        # is still safe to probe for completed provisioning -- this preserves
        # the existing promote-if-done / stop-if-idle behavior for that case.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        with (
            patch("subprocess.run") as mock_run,
            patch.object(driver.images, "_is_staging_provisioned", return_value=False) as mock_probe,
            patch.object(driver.images, "_stop_vm", return_value=True) as mock_stop,
            patch.object(driver, "_build_base_image_async") as mock_resume,
        ):
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "running"}]), returncode=0)
            driver.ensure_base_images_stopped()
        mock_probe.assert_called_once_with("runzero-vm-base-arm64-building")
        mock_stop.assert_called_once_with("runzero-vm-base-arm64-building")
        mock_resume.assert_not_called()

    @patch("subprocess.run")
    def test_prune_exited_ignores_golden_base_image_entries(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        staging_image = RunnerInfo(
            id="r1",
            name="runzero-vm-base-amd64-building",
            status="stopped",
            state="exited",
            target_repo="",
            target_arch="amd64",
            backend="orbstack-vm",
            created_at=time.time() - 25,
        )
        self.driver.prune_exited([staging_image])
        self.assertEqual(self.driver._spawn_failure_counts.get("amd64", 0), 0)
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_is_staging_provisioned_tolerates_exception(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="orb", timeout=25)
        self.assertFalse(self.driver.images._is_staging_provisioned("runzero-vm-base-amd64-building"))

    @patch("subprocess.run")
    def test_is_staging_provisioned_true_and_expected_orb_exec_args(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        self.assertTrue(self.driver.images._is_staging_provisioned("runzero-vm-base-amd64-building"))
        mock_run.assert_called_once_with(
            [
                "orb",
                "-m",
                "runzero-vm-base-amd64-building",
                "-u",
                "runner",
                "bash",
                "-c",
                "test -f /home/runner/actions-runner/run.sh || grep -q 'Base image provisioning complete' /home/runner/provision.log 2>/dev/null",
            ],
            capture_output=True,
            timeout=25,
        )

    @patch("subprocess.run")
    def test_is_staging_provisioned_false_on_nonzero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=7)
        self.assertFalse(self.driver.images._is_staging_provisioned("runzero-vm-base-amd64-building"))

    @patch("subprocess.run")
    def test_promote_staging_to_base_deletes_pre_existing_destination(self, mock_run):
        # If base_name already exists (stale/broken copy), _promote_staging_to_base
        # must delete it before attempting the rename, to avoid a
        # "destination already exists" collision.
        calls = []

        def fake_run(cmd, *args, **kwargs):
            calls.append(cmd)
            if cmd[:2] == ["orbctl", "rename"]:
                return MagicMock(returncode=0)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        with (
            patch.object(self.driver.images, "_stop_vm", return_value=True),
            patch.object(self.driver, "_list_vm_names", return_value=["runzero-vm-base-amd64"]),
        ):
            result = self.driver.images._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        self.assertTrue(result)
        delete_calls = [c for c in calls if c[:2] == ["orbctl", "delete"] and c[-1] == "runzero-vm-base-amd64"]
        self.assertEqual(len(delete_calls), 1)

    @patch("subprocess.run")
    def test_promote_staging_to_base_fails_when_rename_and_clone_both_fail(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] in (["orbctl", "rename"], ["orbctl", "clone"]):
                return MagicMock(returncode=1, stderr="locked")
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        with patch.object(self.driver.images, "_stop_vm", return_value=True), patch("time.sleep"):
            result = self.driver.images._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_create_raises_called_process_error(self, mock_run):
        # Regression-safe unit test isolating the "orbctl create" failure
        # branch: base_image_exists() and the staging-VM lookup are patched
        # directly so the only real subprocess.run call is the failing
        # "orbctl create" itself.
        with patch.object(self.driver, "base_image_exists", return_value=False), patch.object(self.driver, "_list_vm_names", return_value=[]):
            mock_run.side_effect = [
                MagicMock(returncode=0),  # orbctl delete -f staging (no-op)
                subprocess.CalledProcessError(1, ["orbctl", "create"], stderr=b"Out of memory"),
            ]
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_provisioning_times_out(self, mock_run):
        with patch.object(self.driver, "base_image_exists", return_value=False), patch.object(self.driver, "_list_vm_names", return_value=[]):
            mock_run.side_effect = [
                MagicMock(returncode=0),  # orbctl delete -f staging (no-op)
                MagicMock(returncode=0),  # orbctl create
                subprocess.TimeoutExpired(cmd="orb", timeout=1800),  # orb exec provisioning
            ]
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_provisioning_succeeds_but_promote_fails(self, mock_run):
        with (
            patch.object(self.driver, "base_image_exists", return_value=False),
            patch.object(self.driver, "_list_vm_names", return_value=[]),
            patch.object(self.driver.images, "_promote_staging_to_base", return_value=False) as mock_promote,
        ):
            mock_run.side_effect = [
                MagicMock(returncode=0),  # orbctl delete -f staging (no-op)
                MagicMock(returncode=0),  # orbctl create
                MagicMock(returncode=0),  # orb exec provisioning succeeds
            ]
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)
        mock_promote.assert_called_once_with("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")

    @patch("subprocess.run")
    def test_build_base_image_full_success_path(self, mock_run):
        with (
            patch.object(self.driver, "base_image_exists", return_value=False),
            patch.object(self.driver, "_list_vm_names", return_value=[]),
            patch.object(self.driver.images, "_promote_staging_to_base", return_value=True) as mock_promote,
        ):
            mock_run.side_effect = [
                MagicMock(returncode=0),  # orbctl delete -f staging (no-op)
                MagicMock(returncode=0),  # orbctl create
                MagicMock(returncode=0),  # orb exec provisioning succeeds
            ]
            result = self.driver.build_base_image("amd64")
        self.assertTrue(result)
        mock_promote.assert_called_once()

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_tolerates_list_command_failure_during_poll(self, mock_run, mock_sleep):
        list_call_count = {"n": 0}

        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "stop"]:
                return MagicMock(returncode=0)
            if cmd[:2] == ["orbctl", "list"]:
                list_call_count["n"] += 1
                if list_call_count["n"] == 1:
                    raise subprocess.CalledProcessError(1, "orbctl")
                return MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "stopped"}]), returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = fake_run
        result = self.driver.images._stop_vm("test-vm")
        self.assertTrue(result)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_gives_up_after_repeated_attempts(self, mock_run, mock_sleep):
        # VM never actually reports "stopped" -- _stop_vm must exhaust its
        # retries and return False rather than hang or raise.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "running"}]), returncode=0)
        result = self.driver.images._stop_vm("test-vm")
        self.assertFalse(result)
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(len(stop_calls), 3)

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_bails_out_on_list_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        # Must not raise -- just silently gives up for this poll.
        self.driver.ensure_base_images_stopped()

    def test_ensure_base_images_stopped_promotes_provisioned_running_staging_vm(self):
        # A "-building" VM that's running AND already fully provisioned must
        # be promoted directly, not just probed-and-left-running.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        with (
            patch("subprocess.run") as mock_run,
            patch.object(driver.images, "_is_staging_provisioned", return_value=True) as mock_probe,
            patch.object(driver.images, "_promote_staging_to_base", return_value=True) as mock_promote,
            patch.object(driver.images, "_stop_vm") as mock_stop,
        ):
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "running"}]), returncode=0)
            driver.ensure_base_images_stopped()
        mock_probe.assert_called_once_with("runzero-vm-base-arm64-building")
        mock_promote.assert_called_once_with("runzero-vm-base-arm64-building", "runzero-vm-base-arm64")
        mock_stop.assert_not_called()

    @patch("subprocess.run")
    def test_spawn_runner_clone_failure_with_existing_base_image(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, ["orbctl", "clone"], stderr=b"Disk full")
        with patch.object(self.driver, "base_image_exists", return_value=True):
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)

    def test_destroy_runner_refuses_to_delete_base_image(self):
        self.assertFalse(self.driver.destroy_runner("runzero-vm-base-amd64"))

    def test_report_image_event_swallows_callback_exception(self):
        driver = OrbStackVMDriver(on_image_event=lambda event: (_ for _ in ()).throw(RuntimeError("boom")))
        driver._report_image_event("ready", "arm64", "detail")  # must not raise

    def test_init_sets_distro_and_provision_script_path_exactly(self):
        # Regression guard: __init__ previously had zero direct assertions on its
        # own constructor-set attributes. A mutant that hardcoded self.distro to
        # None, or broke the module-relative path resolution for
        # _provision_script_path (e.g. dropping the dirname() walk-up, or
        # corrupting the "docker"/"provision-toolchain.sh" literals), went
        # completely undetected -- despite self.distro feeding directly into a
        # real `orbctl create` subprocess argument, and _provision_script_path
        # gating whether build_base_image() can find its provisioning script at
        # all (the same class of bug as the 2026-09-22 docker-compose.yml outage).
        driver = OrbStackVMDriver(distro="debian:12")
        self.assertEqual(driver.distro, "debian:12")
        self.assertTrue(os.path.isabs(driver.images._provision_script_path))
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        expected_path = os.path.join(repo_root, "docker", "provision-toolchain.sh")
        self.assertEqual(driver.images._provision_script_path, expected_path)

    def test_init_wires_custom_on_image_event_callback(self):
        # Regression guard: `on_image_event or (lambda event: None)` -- an
        # `or`->`and` mutation here would silently DISCARD any real caller-supplied
        # callback and replace it with the no-op lambda instead (since `X and Y`
        # returns Y when X is truthy), completely breaking image-build-status
        # visibility. The existing
        # test_report_image_event_swallows_callback_exception only proved a broken
        # callback doesn't raise -- it never proved the callback was actually the
        # one invoked, since _report_image_event swallows every exception,
        # including "NoneType is not callable".
        events: list[dict[str, Any]] = []
        driver = OrbStackVMDriver(on_image_event=events.append)
        driver._report_image_event("building", "arm64", "detail-here")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["status"], "building")
        self.assertEqual(events[0]["arch"], "arm64")
        self.assertEqual(events[0]["detail"], "detail-here")

    def test_init_default_on_image_event_is_a_real_noop_callable(self):
        driver = OrbStackVMDriver()
        self.assertIsNotNone(driver._on_image_event)
        self.assertIsNone(driver._on_image_event({"anything": 1}))

    def test_build_base_image_async_ok_initial_value_treats_exception_as_failure(self):
        # Regression guard: `ok = False` before the try/finally means an
        # exception raised BY build_base_image() itself (not just a `False`
        # return) still counts as a failure and enters backoff. A mutant that
        # initialized `ok = True` would instead silently treat a crashing build
        # as a success -- resetting the failure count/cooldown and letting the
        # poll loop hot-retry a build that is actually raising every time.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")

        def boom(arch):
            raise RuntimeError("simulated crash inside build_base_image")

        with patch.object(driver, "build_base_image", side_effect=boom):
            driver._build_base_image_async("amd64")
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

        self.assertEqual(driver._backoff.failure_counts.get("amd64", 0), 1)
        self.assertGreater(driver._backoff.remaining("amd64"), 0)

    def test_build_base_image_async_success_from_clean_state_does_not_raise_in_thread(self):
        # Regression guard: on the success path, `self._backoff.retry_after.pop(orb_arch,
        # None)` must tolerate orb_arch never having failed before (empty dict). A
        # `.pop(orb_arch)` without the default would raise KeyError *inside* the
        # background thread on the very first ever successful build -- which Python
        # swallows silently (only a stderr traceback via threading.excepthook, no
        # visible test failure, since daemon-thread exceptions never propagate to the
        # caller). No existing test asserted "no uncaught exception happened in the
        # background thread" -- so this exact class of crash was invisible.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        captured = []
        orig_hook = threading.excepthook
        threading.excepthook = lambda args: captured.append(args)
        try:
            with patch.object(driver, "build_base_image", return_value=True):
                driver._build_base_image_async("amd64")
                self.assertTrue(driver.join_background_build_threads(timeout=5.0))
        finally:
            threading.excepthook = orig_hook
        self.assertEqual(captured, [], f"background thread raised an uncaught exception: {captured}")

    def test_build_base_image_async_skips_when_any_positive_cooldown_remains(self):
        # Regression guard for the `_build_cooldown_remaining(orb_arch) > 0` gate:
        # a `> 1` mutant would let a build through with e.g. 0.5s of cooldown left.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        driver._backoff.retry_after["amd64"] = time.monotonic() + 0.5
        with patch.object(driver, "build_base_image") as mock_build:
            driver._build_base_image_async("amd64")
            driver.join_background_build_threads(timeout=5.0)
        mock_build.assert_not_called()

    def test_build_base_image_async_backoff_formula_exact_values(self):
        # Regression guard: `min(30 * (2 ** (failures - 1)), 900)` had zero
        # value-level assertions (only "second cooldown > first cooldown"), so a
        # wrong base, wrong exponent sign, or wrong cap all survived silently --
        # the same backoff-formula blind spot the sibling docker_driver.py/
        # autoscaler.py triage pass (issue #33) found and fixed.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        expected_by_failure_count = {1: 30, 2: 60, 3: 120, 4: 240, 5: 480, 6: 900, 7: 900}
        with patch.object(driver, "build_base_image", return_value=False):
            for n in sorted(expected_by_failure_count):
                driver._backoff.retry_after["amd64"] = time.monotonic()  # bypass prior cooldown gate
                driver._build_base_image_async("amd64")
                self.assertTrue(driver.join_background_build_threads(timeout=5.0))
                self.assertEqual(driver._backoff.failure_counts["amd64"], n)
                remaining = driver._backoff.remaining("amd64")
                self.assertAlmostEqual(remaining, expected_by_failure_count[n], delta=2)

    def test_build_base_image_async_backoff_hint_appears_only_after_three_failures(self):
        # Regression guard: the diagnostic hint (only shown once failures >= 3)
        # had no test asserting its presence/absence or content -- a mutant that
        # hardcoded hint=None, inverted the >=3 condition, or mangled the hint
        # text all survived. Also pins the exact status/arch/detail arguments
        # passed to _report_image_event, killing the argument-swap/omission
        # mutants on that call.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        events: list[dict[str, Any]] = []
        driver._on_image_event = events.append
        with patch.object(driver, "build_base_image", return_value=False):
            for _ in range(2):
                driver._build_base_image_async("amd64")
                self.assertTrue(driver.join_background_build_threads(timeout=5.0))
                driver._backoff.retry_after["amd64"] = time.monotonic()
            self.assertNotIn("orbctl create", events[-1]["detail"])

            driver._build_base_image_async("amd64")  # 3rd consecutive failure
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

        last_event = events[-1]
        self.assertEqual(last_event["status"], "cooldown")
        self.assertEqual(last_event["arch"], "amd64")
        self.assertIn(
            "This many consecutive failures usually isn't transient -- if 'orbctl create' is "
            "failing with a 'missing IP address' timeout, a plain OrbStack app restart often "
            "doesn't clear it, but a full host reboot usually does",
            last_event["detail"],
        )
        self.assertIn("this is a run-zero bug.", last_event["detail"])

    def test_build_base_image_async_thread_is_named_and_daemonized(self):
        # Regression guard: a non-daemon background build thread would block the
        # whole process from exiting while a (possibly hung, 30-minute) build is
        # in flight -- confirmed a real risk class by the "-building" staging VM
        # orphan scenario documented in ensure_base_images_stopped()'s comments.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        with patch.object(driver, "build_base_image", return_value=True):
            driver._build_base_image_async("amd64")
            thread = driver._backoff.threads["amd64"]
            self.assertEqual(thread.name, "runzero-build-base-amd64")
            self.assertTrue(thread.daemon, "background build thread must be a daemon thread")
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

    def test_promote_staging_to_base_stops_the_staging_vm_by_name(self):
        # Regression guard: existing promote tests all patch _stop_vm with
        # return_value=True, never asserting WHAT it was called with -- a mutant
        # that passed None (or base_name) instead of staging_name went
        # undetected despite _stop_vm shelling out to real `orbctl stop
        # <arg>` in production.
        with patch("subprocess.run") as mock_run, patch.object(self.driver.images, "_stop_vm", return_value=True) as mock_stop:
            mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([]))
            self.driver.images._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        mock_stop.assert_called_once_with("runzero-vm-base-amd64-building")

    def test_promote_staging_to_base_subprocess_calls_have_expected_args(self):
        # Regression guard: every subprocess.run call site in this function
        # (pre-existing-destination delete, rename attempt, clone fallback,
        # post-clone staging delete) had zero exact-arg assertions -- kwarg
        # omission/None/False mutants on capture_output/text, and CLI flag
        # typos ("-f" -> "-F"), all survived silently.
        with patch("subprocess.run") as mock_run, patch.object(self.driver.images, "_stop_vm", return_value=True):
            mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([]))
            self.driver.images._promote_staging_to_base("staging-vm", "base-vm")
        mock_run.assert_any_call(
            ["orbctl", "rename", "staging-vm", "base-vm"],
            capture_output=True,
            text=True,
        )

    def test_promote_staging_to_base_deletes_existing_destination_with_expected_args(self):
        with (
            patch("subprocess.run") as mock_run,
            patch.object(self.driver.images, "_stop_vm", return_value=True),
            patch.object(self.driver, "_list_vm_names", return_value=["base-vm"]),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            self.driver.images._promote_staging_to_base("staging-vm", "base-vm")
        mock_run.assert_any_call(["orbctl", "delete", "-f", "base-vm"], capture_output=True)

    def test_promote_staging_to_base_clone_and_cleanup_calls_have_expected_args(self):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "rename"]:
                return MagicMock(returncode=1, stderr="locked")
            return MagicMock(returncode=0, stdout=json.dumps([]))

        with patch("subprocess.run") as mock_run, patch.object(self.driver.images, "_stop_vm", return_value=True), patch("time.sleep"):
            mock_run.side_effect = fake_run
            result = self.driver.images._promote_staging_to_base("staging-vm", "base-vm")
        self.assertTrue(result)
        mock_run.assert_any_call(["orbctl", "clone", "staging-vm", "base-vm"], capture_output=True, text=True)
        mock_run.assert_any_call(["orbctl", "delete", "-f", "staging-vm"], capture_output=True)

    def test_promote_staging_to_base_retries_rename_exactly_5_times(self):
        with patch("subprocess.run") as mock_run, patch.object(self.driver.images, "_stop_vm", return_value=True), patch("time.sleep"):

            def fake_run(cmd, *args, **kwargs):
                if cmd[:2] == ["orbctl", "rename"]:
                    return MagicMock(returncode=1, stderr="locked")
                return MagicMock(returncode=1, stdout=json.dumps([]))

            mock_run.side_effect = fake_run
            self.driver.images._promote_staging_to_base("staging-vm", "base-vm")
        rename_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "rename"]]
        self.assertEqual(len(rename_calls), 5)

    def test_promote_staging_to_base_rename_backoff_sleep_formula(self):
        # Regression guard: `time.sleep(1.0 + attempt * 0.5)` had no value
        # assertions -- wrong base, wrong operator (* -> /), or wrong
        # multiplier all survived.
        with patch("subprocess.run") as mock_run, patch.object(self.driver.images, "_stop_vm", return_value=True), patch("time.sleep") as mock_sleep:

            def fake_run(cmd, *args, **kwargs):
                if cmd[:2] == ["orbctl", "rename"]:
                    return MagicMock(returncode=1, stderr="locked")
                return MagicMock(returncode=1, stdout=json.dumps([]))

            mock_run.side_effect = fake_run
            self.driver.images._promote_staging_to_base("staging-vm", "base-vm")
        expected = [call(1.0 + attempt * 0.5) for attempt in range(5)]
        mock_sleep.assert_has_calls(expected)

    def test_read_provision_script_missing_file_error_message(self):
        with patch("os.path.isfile", return_value=False), patch("builtins.print") as mock_print:
            result = self.driver.images._read_provision_script()
        self.assertIsNone(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("shared provisioning script not found at", printed)
        self.assertIn(self.driver.images._provision_script_path, printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    def test_read_provision_script_opens_exact_path_and_returns_contents(self):
        with patch("os.path.isfile", return_value=True), patch("builtins.open", mock_open(read_data="script contents")) as mock_file:
            result = self.driver.images._read_provision_script()
        self.assertEqual(result, "script contents")
        mock_file.assert_called_once_with(self.driver.images._provision_script_path)

    def test_report_image_event_passes_exact_structured_dict(self):
        # Regression guard: every dict key here (driver/arch/profile/status/
        # detail/ts) had zero direct assertions -- a key-name typo or a
        # value swapped for the wrong field went completely undetected.
        events: list[dict[str, Any]] = []
        driver = OrbStackVMDriver(distro="ubuntu:24.04", on_image_event=events.append)
        with patch("time.time", return_value=1700000000.0):
            driver._report_image_event("building", "arm64", "some detail", profile="cuda")
        self.assertEqual(len(events), 1)
        self.assertEqual(
            events[0],
            {
                "driver": "orbstack-vm",
                "arch": "arm64",
                "profile": "cuda",
                "status": "building",
                "detail": "some detail",
                "ts": 1700000000.0,
            },
        )

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_returns_true_immediately_when_vm_missing_from_list(self, mock_run, mock_sleep):
        # Regression guard: `.get(vm_name, "stopped")` -- a VM that's already
        # gone from `orbctl list`'s output (deleted/renamed between polls)
        # must be treated as "stopped" (the safe default), not queried again
        # for the full 3x10 retry budget. A mutant defaulting to None instead
        # would force every one of those 30 iterations before giving up.
        mock_run.return_value = MagicMock(stdout=json.dumps([]), returncode=0)
        result = self.driver.images._stop_vm("already-gone-vm")
        self.assertTrue(result)
        list_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "list"]]
        self.assertEqual(len(list_calls), 1)

    @patch("subprocess.run")
    def test_stop_vm_subprocess_calls_have_expected_args(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "stopped"}]), returncode=0)
        self.driver.images._stop_vm("test-vm")
        mock_run.assert_any_call(["orbctl", "stop", "test-vm"], capture_output=True)
        mock_run.assert_any_call(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_polls_exactly_10_times_per_attempt_with_1s_sleep(self, mock_run, mock_sleep):
        # Regression guard: the inner `for _ in range(10)` poll loop and the
        # `time.sleep(1)` between polls both had zero value assertions.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "running"}]), returncode=0)
        self.driver.images._stop_vm("test-vm")
        list_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "list"]]
        self.assertEqual(len(list_calls), 30)  # 3 outer attempts x 10 inner polls
        mock_sleep.assert_called_with(1)
        self.assertEqual(mock_sleep.call_count, 30)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_gives_up_message_content(self, mock_run, mock_sleep):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "running"}]), returncode=0)
        with patch("builtins.print") as mock_print:
            result = self.driver.images._stop_vm("test-vm")
        self.assertFalse(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("test-vm", printed)
        self.assertIn("did not confirm stopped", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_base_image_exists_skips_promotion_while_actively_building(self, mock_run):
        # Regression guard: `being_built = orb_arch in self._backoff.in_progress`
        # gates whether a fully-provisioned staging VM gets auto-promoted.
        # No existing test exercised the branch where a build IS actively
        # in progress for this arch -- an `and`->`or` mutant, or the guard
        # being replaced outright, would let this auto-promote a staging VM
        # out from under a build that's still running against it.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
        self.driver._backoff.in_progress.add("amd64")
        with (
            patch.object(self.driver.images, "_is_staging_provisioned", return_value=True) as mock_provisioned,
            patch.object(self.driver.images, "_promote_staging_to_base") as mock_promote,
        ):
            result = self.driver.base_image_exists("amd64")
        self.assertFalse(result)
        mock_promote.assert_not_called()
        # Regression guard for mutant 12: _is_staging_provisioned must be
        # called with the real staging_name, not None -- but here being_built
        # short-circuits `and` before it's even reached, so it must not be
        # called at all.
        mock_provisioned.assert_not_called()

    @patch("subprocess.run")
    def test_base_image_exists_promotes_when_provisioned_and_not_building(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
        with (
            patch.object(self.driver.images, "_is_staging_provisioned", return_value=True) as mock_provisioned,
            patch.object(self.driver.images, "_promote_staging_to_base", return_value=True) as mock_promote,
            patch("builtins.print") as mock_print,
        ):
            result = self.driver.base_image_exists("amd64")
        self.assertTrue(result)
        mock_provisioned.assert_called_once_with("runzero-vm-base-amd64-building")
        mock_promote.assert_called_once_with("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("runzero-vm-base-amd64-building", printed)
        self.assertIn("promoting to golden base image", printed)
        self.assertIn("runzero-vm-base-amd64", printed)

    @patch("subprocess.run")
    def test_base_image_exists_does_not_promote_when_staging_not_yet_provisioned(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
        with (
            patch.object(self.driver.images, "_is_staging_provisioned", return_value=False),
            patch.object(self.driver.images, "_promote_staging_to_base") as mock_promote,
        ):
            result = self.driver.base_image_exists("amd64")
        self.assertFalse(result)
        mock_promote.assert_not_called()

    @patch("subprocess.run")
    def test_build_base_image_already_exists_reports_exact_event_and_message(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0)
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with patch("builtins.print") as mock_print:
            result = self.driver.build_base_image("amd64")
        self.assertTrue(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("runzero-vm-base-amd64", printed)
        self.assertIn("already exists", printed)
        self.assertEqual(events[-1]["status"], "ready")
        self.assertEqual(events[-1]["arch"], "amd64")
        self.assertEqual(events[-1]["detail"], "Already built -- skipping.")

    def test_build_base_image_promotes_already_provisioned_staging_immediately(self):
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with (
            patch.object(self.driver.images, "base_image_exists", return_value=False),
            patch.object(self.driver, "_list_vm_names", return_value=["runzero-vm-base-amd64-building"]),
            patch.object(self.driver.images, "_is_staging_provisioned", return_value=True) as mock_provisioned,
            patch.object(self.driver.images, "_promote_staging_to_base", return_value=True) as mock_promote,
            patch("builtins.print") as mock_print,
        ):
            result = self.driver.build_base_image("amd64")
        self.assertTrue(result)
        mock_provisioned.assert_called_once_with("runzero-vm-base-amd64-building")
        mock_promote.assert_called_once_with("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("already completed provisioning", printed)
        self.assertEqual(
            events[-1],
            {
                **events[-1],
                "status": "ready",
                "arch": "amd64",
                "detail": "Promoted completed staging VM.",
            },
        )

    def test_build_base_image_building_start_reports_exact_event_and_message(self):
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with (
            patch.object(self.driver, "base_image_exists", return_value=False),
            patch.object(self.driver, "_list_vm_names", return_value=[]),
            patch("subprocess.run", side_effect=Exception("stop here")),
            patch("builtins.print") as mock_print,
        ):
            self.driver.build_base_image("amd64")
        printed_calls = [" ".join(str(a) for a in c.args) for c in mock_print.call_args_list]
        self.assertTrue(any("Building golden base image" in p and "runzero-vm-base-amd64" in p for p in printed_calls))
        building_events = [e for e in events if e["status"] == "building"]
        self.assertEqual(len(building_events), 1)
        self.assertEqual(building_events[0]["arch"], "amd64")
        self.assertIn("Building 'runzero-vm-base-amd64'", building_events[0]["detail"])

    @patch("subprocess.run")
    def test_build_base_image_delete_and_create_subprocess_exact_args(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "create"]:
                raise Exception("stop after create")
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        self.driver.build_base_image("amd64")
        mock_run.assert_any_call(["orbctl", "delete", "-f", "runzero-vm-base-amd64-building"], capture_output=True)
        mock_run.assert_any_call(
            ["orbctl", "create", "-a", "amd64", "-u", "runner", "ubuntu:24.04", "runzero-vm-base-amd64-building"],
            check=True,
            capture_output=True,
        )

    @patch.dict(os.environ, {"RUNNER_CPUS": "2", "RUNNER_MEMORY": "4g", "RUNNER_SIZING": "auto"})
    @patch("drivers.orbstack_image.orbstack_capacity", return_value=HostCapacity(11, 16384))
    @patch("subprocess.run")
    def test_build_base_image_passes_configured_resource_limits_to_create(self, mock_run, _capacity):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "create"]:
                raise Exception("stop after create")
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        driver.build_base_image("amd64")
        mock_run.assert_any_call(
            [
                "orbctl",
                "create",
                "-a",
                "amd64",
                "-u",
                "runner",
                "--cpus",
                "2",
                "--memory",
                "4096M",
                "ubuntu:24.04",
                "runzero-vm-base-amd64-building",
            ],
            check=True,
            capture_output=True,
        )

    @patch("subprocess.run")
    def test_build_base_image_create_called_process_error_decodes_bytes_stderr(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "create"]:
                raise subprocess.CalledProcessError(1, cmd, stderr=b"disk full")
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with patch("builtins.print") as mock_print:
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)
        self.assertEqual(events[-1]["status"], "failed")
        self.assertEqual(events[-1]["arch"], "amd64")
        self.assertEqual(events[-1]["detail"], "Error creating base image: disk full")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("disk full", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_build_base_image_create_called_process_error_falls_back_to_str_when_no_stderr(self, mock_run):
        # Regression guard for the `e.stderr.decode() if e.stderr else str(e)`
        # ternary -- a mutant that always used `str(e)` (or always tried
        # `.decode()`, crashing on None) went undetected because every
        # existing test's CalledProcessError carried real bytes stderr.
        error = subprocess.CalledProcessError(1, ["orbctl", "create"], stderr=None)

        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "create"]:
                raise error
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        self.driver.build_base_image("amd64")
        self.assertEqual(events[-1]["detail"], f"Error creating base image: {error}")

    @patch("subprocess.run")
    def test_build_base_image_create_generic_exception_reports_exact_event_and_message(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "create"]:
                raise RuntimeError("orbctl daemon unreachable")
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with patch("builtins.print") as mock_print:
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)
        self.assertEqual(
            events[-1],
            {
                **events[-1],
                "status": "failed",
                "arch": "amd64",
                "detail": "Error creating base image: orbctl daemon unreachable",
            },
        )
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("orbctl daemon unreachable", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_build_base_image_provision_script_full_content_and_exec_args(self, mock_run):
        # Regression guard: the full_script assembled from docker_engine_snippet(),
        # the raw provisioning script content, and runner_download_snippet(orb_arch,
        # RUNNER_VERSION) had zero content assertions -- a mutant dropping an
        # argument (e.g. runner_download_snippet(RUNNER_VERSION) with orb_arch
        # missing entirely) or passing the wrong arch/version survived.
        captured = {}

        def fake_run(cmd, *args, **kwargs):
            if cmd[0] == "orb":
                captured["cmd"] = cmd
                captured["kwargs"] = kwargs
                return MagicMock(returncode=0)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        with (
            patch.object(self.driver.images, "_read_provision_script", return_value="echo hello-provision-marker"),
            patch.object(self.driver.images, "_promote_staging_to_base", return_value=True),
        ):
            self.driver.build_base_image("arm64")

        self.assertIn("cmd", captured, "the `orb -m ... bash -c <full_script>` call was never reached")
        cmd = captured["cmd"]
        self.assertEqual(cmd[:6], ["orb", "-m", "runzero-vm-base-arm64-building", "-u", "runner", "bash"])
        self.assertEqual(cmd[6], "-c")
        full_script = cmd[7]
        self.assertIn('export ARCH="arm64"', full_script)
        self.assertIn('set -- "arm64"', full_script)
        self.assertIn("echo hello-provision-marker", full_script)
        self.assertIn(docker_engine_snippet(), full_script)
        self.assertIn(runner_download_snippet("arm64", "2.336.0"), full_script)
        self.assertIn("Base image provisioning complete.", full_script)
        self.assertEqual(captured["kwargs"].get("timeout"), 1800)
        self.assertTrue(captured["kwargs"].get("capture_output"))

    @patch("subprocess.run")
    def test_build_base_image_provisioning_nonzero_exit_reports_exact_event_and_message(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd and cmd[0] == "orb":
                return MagicMock(returncode=7)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with patch("builtins.print") as mock_print:
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)
        expected_detail = "Base image provisioning failed (exit 7). Check /home/runner/provision.log inside 'runzero-vm-base-amd64-building' for details."
        self.assertEqual(events[-1]["detail"], expected_detail)
        self.assertEqual(events[-1]["status"], "failed")
        self.assertEqual(events[-1]["arch"], "amd64")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn(expected_detail, printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_build_base_image_provisioning_timeout_reports_exact_event_and_message(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd and cmd[0] == "orb":
                raise subprocess.TimeoutExpired(cmd="orb", timeout=1800)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with patch("builtins.print") as mock_print:
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)
        self.assertEqual(events[-1]["detail"], "Base image provisioning timed out after 30 minutes.")
        self.assertEqual(events[-1]["status"], "failed")
        self.assertEqual(events[-1]["arch"], "amd64")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("timed out after 30 minutes", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_build_base_image_promote_failure_reports_exact_event(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd and cmd[0] == "orb":
                return MagicMock(returncode=0)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with patch.object(self.driver.images, "_promote_staging_to_base", return_value=False):
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)
        self.assertEqual(
            events[-1],
            {
                **events[-1],
                "status": "failed",
                "arch": "amd64",
                "detail": "Failed to promote staging VM to base image.",
            },
        )

    @patch("subprocess.run")
    def test_build_base_image_full_success_reports_exact_event_and_message(self, mock_run):
        def fake_run(cmd, *args, **kwargs):
            if cmd and cmd[0] == "orb":
                return MagicMock(returncode=0)
            return MagicMock(returncode=0, stdout=json.dumps([]))

        mock_run.side_effect = fake_run
        events: list[dict[str, Any]] = []
        self.driver._on_image_event = events.append
        with patch.object(self.driver.images, "_promote_staging_to_base", return_value=True), patch("builtins.print") as mock_print:
            result = self.driver.build_base_image("amd64")
        self.assertTrue(result)
        self.assertEqual(
            events[-1],
            {
                **events[-1],
                "status": "ready",
                "arch": "amd64",
                "detail": "Build succeeded.",
            },
        )
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("runzero-vm-base-amd64", printed)
        self.assertIn("ready", printed)

    def test_destroy_runner_refuses_to_delete_base_image_message_content(self):
        with patch("builtins.print") as mock_print:
            result = self.driver.destroy_runner("runzero-vm-base-amd64")
        self.assertFalse(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("Refusing to delete", printed)
        self.assertIn("runzero-vm-base-amd64", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_list_call_exact_args_and_defaults(self, mock_run):
        # Regression guard: no test asserted the exact `orbctl list` call args,
        # nor the dict-construction defaults (vm.get("name", "")/("state", "")) --
        # a VM entry missing either key must degrade to "", not None/crash.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"other_field": "x"}]), returncode=0)
        self.driver.ensure_base_images_stopped()
        mock_run.assert_called_once_with(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_continues_past_non_base_vm_to_later_base_vm(self, mock_run):
        # Regression guard: `if not name.startswith(BASE_IMAGE_PREFIX): continue`
        # -- a mutant turning this `continue` into `break` would abort the
        # WHOLE loop the first time it saw an ordinary (non-base-image) job
        # VM, silently leaving every later golden base image un-managed. Put
        # a non-base VM first so only `continue` (not `break`) reaches the
        # base image after it.
        mock_run.side_effect = [
            MagicMock(
                stdout=json.dumps(
                    [
                        {"name": "runzero-vm-amd64-el-j-run-zero-abc", "state": "running"},
                        {"name": "runzero-vm-base-amd64", "state": "running"},
                    ]
                ),
                returncode=0,
            ),
            MagicMock(returncode=0),  # orbctl stop
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
        ]
        self.driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "stop"]]
        self.assertEqual(stop_calls, [call(["orbctl", "stop", "runzero-vm-base-amd64"], capture_output=True)])

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_continues_past_currently_building_arch(self, mock_run):
        # Regression guard: same `continue`-not-`break` risk for the
        # `if being_built: continue` guard -- an arch actively building must
        # be skipped WITHOUT aborting the loop for every other tracked arch.
        self.driver._backoff.in_progress.add("amd64")
        mock_run.side_effect = [
            MagicMock(
                stdout=json.dumps(
                    [
                        {"name": "runzero-vm-base-amd64", "state": "running"},  # building -- must be skipped, not abort
                        {"name": "runzero-vm-base-arm64", "state": "running"},  # idle -- must still be stopped
                    ]
                ),
                returncode=0,
            ),
            MagicMock(returncode=0),  # orbctl stop arm64
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-arm64", "state": "stopped"}]), returncode=0),
        ]
        self.driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "stop"]]
        self.assertEqual(stop_calls, [call(["orbctl", "stop", "runzero-vm-base-arm64"], capture_output=True)])

    def test_ensure_base_images_stopped_continues_past_resumed_orphan_to_next_vm(self):
        # Regression guard: after resuming an orphaned "-building" VM's build,
        # `continue` (not `break`) must let the loop keep processing every
        # OTHER base image VM that comes after it.
        with (
            patch("subprocess.run") as mock_run,
            patch.object(self.driver, "_build_base_image_async") as mock_resume,
            patch.object(self.driver.images, "_stop_vm") as mock_stop,
        ):
            mock_run.return_value = MagicMock(
                stdout=json.dumps(
                    [
                        {"name": "runzero-vm-base-amd64-building", "state": "stopped"},  # orphaned -- resume
                        {"name": "runzero-vm-base-arm64", "state": "running"},  # idle -- must still be stopped
                    ]
                ),
                returncode=0,
            )
            self.driver.ensure_base_images_stopped()
        mock_resume.assert_called_once_with("amd64")
        mock_stop.assert_called_once_with("runzero-vm-base-arm64")

    def test_ensure_base_images_stopped_idle_staging_promotion_message_content(self):
        with (
            patch("subprocess.run") as mock_run,
            patch.object(self.driver.images, "_is_staging_provisioned", return_value=True),
            patch.object(self.driver.images, "_promote_staging_to_base") as mock_promote,
            patch("builtins.print") as mock_print,
        ):
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "running"}]), returncode=0)
            self.driver.ensure_base_images_stopped()
        mock_promote.assert_called_once_with("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("already provisioned", printed)
        self.assertIn("runzero-vm-base-amd64-building", printed)
        self.assertIn("runzero-vm-base-amd64", printed)

    def test_ensure_base_images_stopped_orphaned_resume_message_content(self):
        with patch("subprocess.run") as mock_run, patch.object(self.driver, "_build_base_image_async") as mock_resume, patch("builtins.print") as mock_print:
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
            self.driver.ensure_base_images_stopped()
        mock_resume.assert_called_once_with("amd64")
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("orphaned staging VM", printed)
        self.assertIn("runzero-vm-base-amd64-building", printed)

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_idle_running_base_message_content(self, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "running"}]), returncode=0),
            MagicMock(returncode=0),
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
        ]
        with patch("builtins.print") as mock_print:
            self.driver.ensure_base_images_stopped()
        printed = " ".join(str(a) for a in mock_print.call_args_list[0].args)
        self.assertIn("running idle", printed)
        self.assertIn("runzero-vm-base-amd64", printed)

    def test_join_background_build_threads_default_timeout_is_10_seconds(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        release = threading.Event()

        def blocked(arch):
            release.wait(timeout=5)
            return True

        with patch.object(driver, "build_base_image", side_effect=blocked):
            driver._build_base_image_async("amd64")
            thread = driver._backoff.threads["amd64"]
            with patch.object(thread, "join") as mock_join:
                driver.join_background_build_threads()
            mock_join.assert_called_once_with(timeout=10.0)
            release.set()
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

    def test_join_background_build_threads_returns_exactly_false_not_none(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        still_running = threading.Event()

        def blocked(arch):
            still_running.wait(timeout=5)
            return True

        with patch.object(driver, "build_base_image", side_effect=blocked):
            driver._build_base_image_async("amd64")
            result = driver.join_background_build_threads(timeout=0.05)
            self.assertIs(result, False)
            still_running.set()
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))


if __name__ == "__main__":
    unittest.main()
