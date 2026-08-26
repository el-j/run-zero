"""
Unit tests for OrbStack Linux VM runner driver and templates.
"""

import json
import subprocess
import time
import unittest
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from drivers.orbstack_templates import (
    cache_mount_snippet,
    docker_engine_snippet,
    registration_and_run_snippet,
    runner_download_snippet,
)
from drivers.orbstack_vm_driver import OrbStackVMDriver


class TestOrbStackTemplates(unittest.TestCase):
    def test_snippets_generate_valid_bash(self):
        engine = docker_engine_snippet()
        self.assertIn("docker-ce", engine)
        self.assertIn("systemctl enable docker", engine)

    def test_docker_engine_uses_cgroupfs_driver(self):
        # Regression test: Docker's default "systemd" cgroup driver asks the
        # guest's systemd to create a transient scope unit (via dbus) for
        # every container started. The golden VM is itself an OrbStack
        # "scon" (an LXC-style container inside one shared master VM, not
        # independent hardware virtualization), and in that nested setup
        # systemd's kernel-thread check for the new scope fails against the
        # guest's /proc with ENOTTY: "Failed to determine whether process N
        # is a kernel thread: Inappropriate ioctl for device" -- so every
        # `docker start` (including GitHub Actions service containers like
        # postgres) failed immediately. Reproduced live in the actual golden
        # base VM and confirmed the systemd driver fails while cgroupfs
        # (which manages the cgroup v2 hierarchy directly, without asking
        # systemd for a scope unit) starts the same container cleanly.
        engine = docker_engine_snippet()
        self.assertIn('"exec-opts": ["native.cgroupdriver=cgroupfs"]', engine)
        self.assertIn("/etc/docker/daemon.json", engine)

    def test_docker_engine_uses_registry_mirror(self):
        # Regression test: without a registry-mirrors entry, every `docker
        # pull`/`docker create` inside the VM (including GitHub Actions
        # service containers like postgres, pulled fresh on every ephemeral
        # VM) goes straight to Docker Hub, bypassing the stack's own
        # pull-through cache (docker-compose.yml's "docker-mirror" service)
        # entirely. Confirmed live (2026-08-26): docker-mirror-storage sat at
        # 0 bytes after dozens of pulls this session; after adding this
        # config, `docker info` reported the mirror active and a single pull
        # inside a real VM grew the mirror's storage volume from 0 to 3.4M.
        engine = docker_engine_snippet()
        self.assertIn('"registry-mirrors": ["http://host.orb.internal:49502"]', engine)
        # Required alongside it: dockerd refuses a plain-HTTP registry-mirrors
        # entry unless it's also listed in insecure-registries.
        self.assertIn('"insecure-registries": ["host.orb.internal:49502"]', engine)

    def test_other_snippets_generate_valid_bash(self):
        dl = runner_download_snippet("amd64", "2.336.0")
        self.assertIn("actions-runner-linux-${RUNNER_ARCH}-2.336.0.tar.gz", dl)

        reg = registration_and_run_snippet(
            "https://api.github.com/repos/owner/repo/actions/runners",
            "https://github.com/owner/repo",
            "pat-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1"
        )
        self.assertIn("registration-token", reg)
        self.assertIn("./config.sh", reg)
        self.assertIn("./run.sh", reg)
        # Default cache_mount_block is "" -- no bind-mount lines injected when the
        # caller (e.g. an existing test) doesn't pass one.
        self.assertNotIn("mount --bind", reg)

    def test_registration_and_run_snippet_includes_cache_mount_block(self):
        reg = registration_and_run_snippet(
            "https://api.github.com/repos/owner/repo/actions/runners",
            "https://github.com/owner/repo",
            "pat-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1",
            cache_mount_block="sudo mount --bind /mnt/mac/fake /home/runner/.npm"
        )
        # Cache mounts must land before the proxy env vars are exported and before
        # config.sh/run.sh execute, so the directories are ready before the job's own
        # tooling (and the proxy-aware env) starts using them.
        mount_idx = reg.index("mount --bind")
        proxy_idx = reg.index("export PROXY=1")
        config_idx = reg.index("./config.sh")
        self.assertLess(mount_idx, proxy_idx)
        self.assertLess(proxy_idx, config_idx)

    def test_cache_mount_snippet_empty_when_no_mounts(self):
        self.assertEqual(cache_mount_snippet(None), "")
        self.assertEqual(cache_mount_snippet({}), "")

    def test_cache_mount_snippet_generates_bind_mount_via_mac_share(self):
        snippet = cache_mount_snippet({
            "/Users/dev/.local-github-runner/cache/npm": "/home/runner/.npm",
            "/Users/dev/.local-github-runner/cache/pip": "/home/runner/.cache/pip",
        })
        # Every host path must be translated to OrbStack's automatic
        # /mnt/mac<absolute-macOS-path> share, and bind-mounted onto the exact
        # container-style destination path cache_manager.py expects.
        self.assertIn('sudo mkdir -p "/home/runner/.npm"', snippet)
        self.assertIn(
            'sudo mount --bind "/mnt/mac/Users/dev/.local-github-runner/cache/npm" "/home/runner/.npm"',
            snippet,
        )
        self.assertIn('sudo mkdir -p "/home/runner/.cache/pip"', snippet)
        self.assertIn(
            'sudo mount --bind "/mnt/mac/Users/dev/.local-github-runner/cache/pip" "/home/runner/.cache/pip"',
            snippet,
        )
        # Must guard against the mac share not (yet) exposing the path rather than
        # blowing up the whole provisioning script.
        self.assertIn("Warning: host cache dir", snippet)
        self.assertIn("Warning: cache bind mount failed", snippet)


class TestOrbStackVMDriver(unittest.TestCase):
    def setUp(self):
        self.driver = OrbStackVMDriver(distro="ubuntu:24.04")

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

    @patch("shutil.which", return_value="/usr/local/bin/orbctl")
    @patch("subprocess.run")
    def test_is_available_exception(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_list_runners_json_parser(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=json.dumps([
                {"name": "runzero-vm-arm64-el-j-run-zero-123", "state": "running"},
                {"name": "runzero-vm-amd64-my-org-456", "state": "stopped"},
                {"name": "unrelated-vm", "state": "running"}
            ]),
            returncode=0
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
    def test_list_runners_creating_and_provisioning_are_pending_not_exited(self, mock_run):
        # Regression test: these are transient startup states, not terminal ones.
        # Misclassifying them as "exited" undercounts genuinely in-flight VMs in
        # the autoscaler's active-runner tally, causing a duplicate spawn for the
        # same job before the first VM finishes booting -- confirmed live: 3
        # runners registered for one real queued job, the 2 losers left idle
        # forever since ephemeral runners only self-terminate after completing a
        # job, never just for being unclaimed.
        mock_run.return_value = MagicMock(
            stdout=json.dumps([
                {"name": "runzero-vm-arm64-el-j-run-zero-aaa111", "state": "creating"},
                {"name": "runzero-vm-arm64-el-j-run-zero-bbb222", "state": "provisioning"},
            ]),
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "pending")
        self.assertEqual(runners[1].state, "pending")

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
            stdout=json.dumps([
                {"name": "runzero-vm-amd64-el-j-run-zero-ccc333", "state": "starting"},
            ]),
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "pending")

    @patch("subprocess.run")
    def test_list_runners_exception(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl")
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

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
                    {"name": "runzero-vm-amd64-el-j-run-zero-abc123", "state": "running"},
                ]),
                returncode=0
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
        clone_call = mock_run.call_args_list[1]
        self.assertEqual(clone_call[0][0][:2], ["orbctl", "clone"])

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
        popen_args = mock_popen.call_args[0][0]
        self.assertEqual(popen_args[:5], ["orb", "-m", name, "-u", "runner"])
        setup_script = popen_args[-1]
        self.assertIn(
            'sudo mount --bind "/mnt/mac/Users/dev/.local-github-runner/cache/npm" "/home/runner/.npm"',
            setup_script,
        )

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
        self.assertIn('export PIP_INDEX_URL="http://host.orb.internal:49507/root/pypi/+simple/"', setup_script)
        self.assertIn('export UV_INDEX_URL="http://host.orb.internal:49507/root/pypi/+simple/"', setup_script)
        # pip refuses a plain-HTTP non-localhost index without this (verified live).
        self.assertIn('export PIP_TRUSTED_HOST="host.orb.internal"', setup_script)
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

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_skips_duplicate_build_while_already_building(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),  # list VMs
        ]
        self.driver._building_arches.add("amd64")
        with patch.object(self.driver, "_build_base_image_async") as mock_async_build:
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)
        mock_async_build.assert_not_called()

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

            for _ in range(100):
                with driver._building_lock:
                    if "amd64" not in driver._building_arches:
                        break
                time.sleep(0.02)

        self.assertEqual(calls, ["amd64"])
        self.assertNotIn("amd64", driver._building_arches)

    def _run_async_build_and_wait(self, driver: OrbStackVMDriver, orb_arch: str) -> None:
        """Kick off _build_base_image_async and block until its background
        thread has finished (removed orb_arch from _building_arches)."""
        driver._build_base_image_async(orb_arch)
        for _ in range(100):
            with driver._building_lock:
                if orb_arch not in driver._building_arches:
                    return
            time.sleep(0.02)
        self.fail("build_base_image_async did not finish in time")

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
            self.assertEqual(driver._build_failure_counts["amd64"], 1)
            self.assertGreater(driver._build_cooldown_remaining("amd64"), 0)

            # Immediate follow-up poll (what the real poll loop does every
            # ~15-20s) must be a no-op while the cooldown is in effect.
            driver._build_base_image_async("amd64")
            self.assertEqual(calls, ["amd64"])

    def test_build_base_image_async_cooldown_escalates_and_resets_on_success(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        outcomes = iter([False, False])

        with patch.object(driver, "build_base_image", side_effect=lambda arch: next(outcomes)):
            self._run_async_build_and_wait(driver, "amd64")
            first_cooldown = driver._build_cooldown_remaining("amd64")

            # Force the cooldown to have already elapsed so the second
            # attempt is actually allowed to run.
            driver._build_retry_after["amd64"] = time.monotonic()
            self._run_async_build_and_wait(driver, "amd64")
            second_cooldown = driver._build_cooldown_remaining("amd64")

        self.assertEqual(driver._build_failure_counts["amd64"], 2)
        self.assertGreater(second_cooldown, first_cooldown)

        # A subsequent success must clear both the failure count and cooldown
        # -- a build that starts working again shouldn't stay throttled.
        driver._build_retry_after["amd64"] = time.monotonic()
        with patch.object(driver, "build_base_image", return_value=True):
            self._run_async_build_and_wait(driver, "amd64")
        self.assertEqual(driver._build_failure_counts["amd64"], 0)
        self.assertEqual(driver._build_cooldown_remaining("amd64"), 0.0)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_does_not_reannounce_build_during_cooldown(self, mock_run, mock_popen):
        # spawn_runner()'s "Building it in the background" message implies an
        # attempt is actually starting -- must not print (or start one) while
        # a backoff cooldown from a prior failure is still in effect.
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([]), returncode=0),  # list VMs
        ]
        self.driver._build_retry_after["amd64"] = time.monotonic() + 60
        with patch.object(self.driver, "_build_base_image_async") as mock_async_build:
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)
        mock_async_build.assert_not_called()

    @patch("subprocess.run")
    def test_build_base_image_missing_script_fails_gracefully(self, mock_run):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        driver._provision_script_path = "/nonexistent/provision-toolchain.sh"
        result = driver.build_base_image("amd64")
        self.assertFalse(result)
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_build_base_image_skips_when_already_exists(self, mock_run):
        # Guards against ever deleting/rebuilding a golden image that's already
        # there, regardless of why build_base_image() got called.
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0
        )
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
        with patch.object(self.driver, "base_image_exists", return_value=False), \
             patch.object(self.driver, "_stop_vm", return_value=True):
            result = self.driver.build_base_image("amd64")
            self.assertTrue(result)
            rename_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "rename"]]
            self.assertEqual(len(rename_calls), 1)
            self.assertEqual(
                rename_calls[0][0][0], ["orbctl", "rename", "runzero-vm-base-amd64-building", "runzero-vm-base-amd64"]
            )

    @patch("subprocess.run")
    def test_build_base_image_rename_failure(self, mock_run):
        # When rename fails across all retries and clone fallback also fails,
        # build_base_image returns False.
        mock_run.return_value = MagicMock(returncode=1, stderr=b"persistent error", stdout=json.dumps([]))
        with patch.object(self.driver, "base_image_exists", return_value=False), \
             patch.object(self.driver, "_stop_vm", return_value=True):
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
        with patch.object(self.driver, "_stop_vm", return_value=True):
            res = self.driver._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
            self.assertTrue(res)

    @patch("subprocess.run")
    def test_base_image_exists_auto_promotes_completed_staging(self, mock_run):
        # If base image is missing but completed staging VM exists, base_image_exists auto-promotes it
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]),
            returncode=0
        )
        with patch.object(self.driver, "_is_staging_provisioned", return_value=True), \
             patch.object(self.driver, "_promote_staging_to_base", return_value=True) as mock_promote:
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
    def test_spawn_runner_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "orbctl", stderr=b"Out of memory")
        name = self.driver.spawn_runner(repo="el-j/run-zero")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_stops_idle_running_base(self, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([  # _list_vm_names() in ensure_base_images_stopped
                {"name": "runzero-vm-base-amd64", "state": "running"},
                {"name": "runzero-vm-amd64-el-j-run-zero-abc", "state": "running"},
            ]), returncode=0),
            MagicMock(returncode=0),  # orbctl stop
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
        ]
        self.driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(len(stop_calls), 1)
        self.assertEqual(stop_calls[0][0][0], ["orbctl", "stop", "runzero-vm-base-amd64"])

    @patch("subprocess.run")
    def test_ensure_base_images_stopped_leaves_stopped_base_alone(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0
        )
        self.driver.ensure_base_images_stopped()
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "stop"]]
        self.assertEqual(stop_calls, [])

    def test_ensure_base_images_stopped_skips_arch_currently_being_built(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        driver._building_arches.add("amd64")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "running"}]), returncode=0
            )
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
        driver._building_arches.add("amd64")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "running"}]), returncode=0
            )
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
        with patch("subprocess.run") as mock_run, \
             patch.object(driver, "_is_staging_provisioned") as mock_probe, \
             patch.object(driver, "_build_base_image_async") as mock_resume:
            mock_run.return_value = MagicMock(
                stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "stopped"}]),
                returncode=0
            )
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
        with patch("subprocess.run") as mock_run, \
             patch.object(driver, "_is_staging_provisioned", return_value=False) as mock_probe, \
             patch.object(driver, "_stop_vm", return_value=True) as mock_stop, \
             patch.object(driver, "_build_base_image_async") as mock_resume:
            mock_run.return_value = MagicMock(
                stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "running"}]),
                returncode=0
            )
            driver.ensure_base_images_stopped()
        mock_probe.assert_called_once_with("runzero-vm-base-arm64-building")
        mock_stop.assert_called_once_with("runzero-vm-base-arm64-building")
        mock_resume.assert_not_called()

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
    def test_is_staging_provisioned_tolerates_exception(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="orb", timeout=25)
        self.assertFalse(self.driver._is_staging_provisioned("runzero-vm-base-amd64-building"))

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
        with patch.object(self.driver, "_stop_vm", return_value=True), \
             patch.object(self.driver, "_list_vm_names", return_value=["runzero-vm-base-amd64"]):
            result = self.driver._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
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
        with patch.object(self.driver, "_stop_vm", return_value=True), \
             patch("time.sleep"):
            result = self.driver._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_create_raises_called_process_error(self, mock_run):
        # Regression-safe unit test isolating the "orbctl create" failure
        # branch: base_image_exists() and the staging-VM lookup are patched
        # directly so the only real subprocess.run call is the failing
        # "orbctl create" itself.
        with patch.object(self.driver, "base_image_exists", return_value=False), \
             patch.object(self.driver, "_list_vm_names", return_value=[]):
            mock_run.side_effect = [
                MagicMock(returncode=0),  # orbctl delete -f staging (no-op)
                subprocess.CalledProcessError(1, ["orbctl", "create"], stderr=b"Out of memory"),
            ]
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_provisioning_times_out(self, mock_run):
        with patch.object(self.driver, "base_image_exists", return_value=False), \
             patch.object(self.driver, "_list_vm_names", return_value=[]):
            mock_run.side_effect = [
                MagicMock(returncode=0),  # orbctl delete -f staging (no-op)
                MagicMock(returncode=0),  # orbctl create
                subprocess.TimeoutExpired(cmd="orb", timeout=1800),  # orb exec provisioning
            ]
            result = self.driver.build_base_image("amd64")
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_build_base_image_provisioning_succeeds_but_promote_fails(self, mock_run):
        with patch.object(self.driver, "base_image_exists", return_value=False), \
             patch.object(self.driver, "_list_vm_names", return_value=[]), \
             patch.object(self.driver, "_promote_staging_to_base", return_value=False) as mock_promote:
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
        with patch.object(self.driver, "base_image_exists", return_value=False), \
             patch.object(self.driver, "_list_vm_names", return_value=[]), \
             patch.object(self.driver, "_promote_staging_to_base", return_value=True) as mock_promote:
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
        result = self.driver._stop_vm("test-vm")
        self.assertTrue(result)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_gives_up_after_repeated_attempts(self, mock_run, mock_sleep):
        # VM never actually reports "stopped" -- _stop_vm must exhaust its
        # retries and return False rather than hang or raise.
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"name": "test-vm", "state": "running"}]), returncode=0
        )
        result = self.driver._stop_vm("test-vm")
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
        with patch("subprocess.run") as mock_run, \
             patch.object(driver, "_is_staging_provisioned", return_value=True) as mock_probe, \
             patch.object(driver, "_promote_staging_to_base", return_value=True) as mock_promote, \
             patch.object(driver, "_stop_vm") as mock_stop:
            mock_run.return_value = MagicMock(
                stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "running"}]),
                returncode=0
            )
            driver.ensure_base_images_stopped()
        mock_probe.assert_called_once_with("runzero-vm-base-arm64-building")
        mock_promote.assert_called_once_with("runzero-vm-base-arm64-building", "runzero-vm-base-arm64")
        mock_stop.assert_not_called()

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_spawn_runner_for_org_target(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),  # orbctl clone
        ]
        name = self.driver.spawn_runner(org="my-org", arch="amd64", access_token="token")
        self.assertIsNotNone(name)
        self.assertEqual(self.driver._runner_repos.get(name), "my-org")

    @patch("subprocess.run")
    def test_spawn_runner_clone_failure_with_existing_base_image(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, ["orbctl", "clone"], stderr=b"Disk full")
        with patch.object(self.driver, "base_image_exists", return_value=True):
            name = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token")
        self.assertIsNone(name)

    def test_destroy_runner_refuses_to_delete_base_image(self):
        self.assertFalse(self.driver.destroy_runner("runzero-vm-base-amd64"))

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
        mock_run.return_value = MagicMock(
            stdout=json.dumps([{"name": "runzero-vm-amd64-el-j-run-zero-abc123", "state": "stopped"}]),
            returncode=0
        )
        self.driver.cleanup_all()
        delete_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "delete"]]
        self.assertEqual(len(delete_calls), 1)
        self.assertEqual(delete_calls[0][0][0], ["orbctl", "delete", "-f", "runzero-vm-amd64-el-j-run-zero-abc123"])


if __name__ == "__main__":
    unittest.main()
