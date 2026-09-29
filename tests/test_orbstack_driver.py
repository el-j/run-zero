"""
Unit tests for OrbStack Linux VM runner driver and templates.
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

from drivers import RunnerInfo
from drivers.orbstack_templates import (
    cache_mount_snippet,
    docker_engine_snippet,
    registration_and_run_snippet,
    runner_download_snippet,
)
from drivers.orbstack_vm_driver import (
    FAST_FAILURE_WINDOW_SECONDS,
    STARTUP_GRACE_PERIOD_SECONDS,
    OrbStackVMDriver,
)


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
            "https://github.com/owner/repo",
            "reg-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1",
        )
        # The VM registers with the host-issued registration token; it never calls the
        # registration-token API itself (that would require the PAT inside the VM).
        self.assertNotIn("registration-token", reg)
        self.assertNotIn("Authorization", reg)
        self.assertIn("--token reg-token", reg)
        self.assertIn("./config.sh", reg)
        self.assertIn("./run.sh", reg)
        # Default cache_mount_block is "" -- no bind-mount lines injected when the
        # caller (e.g. an existing test) doesn't pass one.
        self.assertNotIn("mount --bind", reg)

    def test_registration_and_run_snippet_includes_cache_mount_block(self):
        reg = registration_and_run_snippet(
            "https://github.com/owner/repo",
            "reg-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1",
            cache_mount_block="sudo mount --bind /mnt/mac/fake /home/runner/.npm",
        )
        # Cache mounts must land before the proxy env vars are exported and before
        # config.sh/run.sh execute, so the directories are ready before the job's own
        # tooling (and the proxy-aware env) starts using them.
        mount_idx = reg.index("mount --bind")
        proxy_idx = reg.index("export PROXY=1")
        config_idx = reg.index("./config.sh")
        self.assertLess(mount_idx, proxy_idx)
        self.assertLess(proxy_idx, config_idx)

    def test_registration_and_run_snippet_includes_network_self_healing(self):
        reg = registration_and_run_snippet(
            "https://github.com/owner/repo",
            "reg-token",
            "vm-test",
            "self-hosted,local",
            "export PROXY=1",
        )
        self.assertIn("DHCP unfulfilled on eth0", reg)
        self.assertIn("192.168.139.1", reg)
        self.assertIn("nameserver 0.250.250.200", reg)
        self.assertIn("nameserver 1.1.1.1", reg)
        self.assertIn("api.github.com reachable", reg)

    def test_cache_mount_snippet_empty_when_no_mounts(self):
        self.assertEqual(cache_mount_snippet(None), "")
        self.assertEqual(cache_mount_snippet({}), "")

    def test_cache_mount_snippet_generates_bind_mount_via_mac_share(self):
        snippet = cache_mount_snippet(
            {
                "/Users/dev/.local-github-runner/cache/npm": "/home/runner/.npm",
                "/Users/dev/.local-github-runner/cache/pip": "/home/runner/.cache/pip",
            }
        )
        # Every host path must be translated to OrbStack's automatic
        # /mnt/mac<absolute-macOS-path> share, and bind-mounted onto the exact
        # container-style destination path cache_manager.py expects.
        self.assertIn("sudo mkdir -p /home/runner/.npm", snippet)
        self.assertIn(
            "sudo mount --bind /mnt/mac/Users/dev/.local-github-runner/cache/npm /home/runner/.npm",
            snippet,
        )
        self.assertIn("sudo mkdir -p /home/runner/.cache/pip", snippet)
        self.assertIn(
            "sudo mount --bind /mnt/mac/Users/dev/.local-github-runner/cache/pip /home/runner/.cache/pip",
            snippet,
        )
        # Must guard against the mac share not (yet) exposing the path rather than
        # blowing up the whole provisioning script.
        self.assertIn("Warning: host cache dir", snippet)
        self.assertIn("Warning: cache bind mount failed", snippet)

    def test_cache_mount_snippet_chowns_runner_ancestor_directories(self):
        snippet = cache_mount_snippet({"/Users/dev/.local-github-runner/cache/rust": "/home/runner/.cargo/registry"})
        self.assertIn("sudo mkdir -p /home/runner/.cargo/registry", snippet)
        self.assertIn('sudo chown runner:runner "$_p"', snippet)
        self.assertIn("sudo chown runner:runner /home/runner/.cargo/registry", snippet)

    def test_cache_mount_snippet_quotes_hostile_paths(self):
        # cache_mounts can arrive over the bridge; a path must never break out of its word.
        snippet = cache_mount_snippet({'/Users/x"; touch /tmp/pwned; "': "/home/runner/$(id)"})
        self.assertNotIn("$(id)\n", snippet.replace("'/home/runner/$(id)'", ""))
        self.assertIn("'/home/runner/$(id)'", snippet)
        self.assertIn("'/mnt/mac/Users/x\"; touch /tmp/pwned; \"'", snippet)


class TestOrbStackVMDriver(unittest.TestCase):
    # Regression guard for issue #20: OrbStackVMDriver._build_base_image_async
    # starts a real background daemon thread. Under plain `unittest discover`
    # (as opposed to the containerized `make test-suite` run), a thread left
    # running past its own test's mock.patch context is invisible to that
    # test but still alive when a LATER test starts -- and since
    # unittest.mock.patch("subprocess.run") patches the module-global
    # function, the leftover thread's real subprocess.run calls get routed
    # through whatever later test currently has it patched, corrupting that
    # test's mock call/side_effect bookkeeping non-deterministically. This
    # was confirmed to be the actual root cause of order-dependent flakiness
    # in test_spawn_runner_omits_cache_mount_lines_when_no_mounts, sourced
    # from test_spawn_runner_failure (which used to leave exactly this kind
    # of thread running -- see that test's fix below).
    #
    # tearDown joins every background thread this class's `self.driver`
    # started, so no test in this class can leak a live thread into the next
    # one. Any NEW test added here that triggers a real background thread
    # (by not mocking `_build_base_image_async`/`build_base_image`) will now
    # fail loudly, right here, instead of silently destabilizing an unrelated
    # test later.
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
        self.assertIn('export NPM_CONFIG_REGISTRY="http://host.orb.internal:49501/"', setup_script)
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

            # Join (not just poll shared state) so the background thread is
            # provably finished -- and thus can never leak into a later test
            # -- before this mock.patch context exits. See issue #20.
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

        self.assertEqual(calls, ["amd64"])
        self.assertNotIn("amd64", driver._building_arches)

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

    def _run_async_build_and_wait(self, driver: OrbStackVMDriver, orb_arch: str) -> None:
        """Kick off _build_base_image_async and block until its background
        thread has actually finished (joined, not just polled via shared
        state) -- see issue #20 on why a real join matters here."""
        driver._build_base_image_async(orb_arch)
        if not driver.join_background_build_threads(timeout=5.0):
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
        with patch.object(self.driver, "base_image_exists", return_value=False), patch.object(self.driver, "_stop_vm", return_value=True):
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
        with patch.object(self.driver, "base_image_exists", return_value=False), patch.object(self.driver, "_stop_vm", return_value=True):
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
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
        with (
            patch.object(self.driver, "_is_staging_provisioned", return_value=True),
            patch.object(self.driver, "_promote_staging_to_base", return_value=True) as mock_promote,
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
        driver._building_arches.add("amd64")
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
        driver._building_arches.add("amd64")
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
            patch.object(driver, "_is_staging_provisioned") as mock_probe,
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
            patch.object(driver, "_is_staging_provisioned", return_value=False) as mock_probe,
            patch.object(driver, "_stop_vm", return_value=True) as mock_stop,
            patch.object(driver, "_build_base_image_async") as mock_resume,
        ):
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "running"}]), returncode=0)
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

    @patch("subprocess.run")
    def test_is_staging_provisioned_tolerates_exception(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="orb", timeout=25)
        self.assertFalse(self.driver._is_staging_provisioned("runzero-vm-base-amd64-building"))

    @patch("subprocess.run")
    def test_is_staging_provisioned_true_and_expected_orb_exec_args(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        self.assertTrue(self.driver._is_staging_provisioned("runzero-vm-base-amd64-building"))
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
        with patch.object(self.driver, "_stop_vm", return_value=True), patch.object(self.driver, "_list_vm_names", return_value=["runzero-vm-base-amd64"]):
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
        with patch.object(self.driver, "_stop_vm", return_value=True), patch("time.sleep"):
            result = self.driver._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
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
            patch.object(self.driver, "_promote_staging_to_base", return_value=False) as mock_promote,
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
            patch.object(self.driver, "_promote_staging_to_base", return_value=True) as mock_promote,
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
        result = self.driver._stop_vm("test-vm")
        self.assertTrue(result)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_gives_up_after_repeated_attempts(self, mock_run, mock_sleep):
        # VM never actually reports "stopped" -- _stop_vm must exhaust its
        # retries and return False rather than hang or raise.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "running"}]), returncode=0)
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
        with (
            patch("subprocess.run") as mock_run,
            patch.object(driver, "_is_staging_provisioned", return_value=True) as mock_probe,
            patch.object(driver, "_promote_staging_to_base", return_value=True) as mock_promote,
            patch.object(driver, "_stop_vm") as mock_stop,
        ):
            mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-arm64-building", "state": "running"}]), returncode=0)
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
        assert name is not None
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
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-amd64-el-j-run-zero-abc123", "state": "stopped"}]), returncode=0)
        self.driver.cleanup_all()
        delete_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["orbctl", "delete"]]
        self.assertEqual(len(delete_calls), 1)
        self.assertEqual(delete_calls[0][0][0], ["orbctl", "delete", "-f", "runzero-vm-amd64-el-j-run-zero-abc123"])

    def test_report_image_event_swallows_callback_exception(self):
        driver = OrbStackVMDriver(on_image_event=lambda event: (_ for _ in ()).throw(RuntimeError("boom")))
        driver._report_image_event("ready", "arm64", "detail")  # must not raise

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

    # -- Mutation-triage additions (issue #30) -----------------------------------

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
        self.assertTrue(os.path.isabs(driver._provision_script_path))
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        expected_path = os.path.join(repo_root, "docker", "provision-toolchain.sh")
        self.assertEqual(driver._provision_script_path, expected_path)

    def test_init_default_distro_is_ubuntu_2404(self):
        driver = OrbStackVMDriver()
        self.assertEqual(driver.distro, "ubuntu:24.04")

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

        self.assertEqual(driver._build_failure_counts.get("amd64", 0), 1)
        self.assertGreater(driver._build_cooldown_remaining("amd64"), 0)

    def test_build_base_image_async_success_from_clean_state_does_not_raise_in_thread(self):
        # Regression guard: on the success path, `self._build_retry_after.pop(orb_arch,
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
        driver._build_retry_after["amd64"] = time.monotonic() + 0.5
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
                driver._build_retry_after["amd64"] = time.monotonic()  # bypass prior cooldown gate
                driver._build_base_image_async("amd64")
                self.assertTrue(driver.join_background_build_threads(timeout=5.0))
                self.assertEqual(driver._build_failure_counts["amd64"], n)
                remaining = driver._build_cooldown_remaining("amd64")
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
                driver._build_retry_after["amd64"] = time.monotonic()
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
            thread = driver._build_threads["amd64"]
            self.assertEqual(thread.name, "runzero-build-base-amd64")
            self.assertTrue(thread.daemon, "background build thread must be a daemon thread")
            self.assertTrue(driver.join_background_build_threads(timeout=5.0))

    def test_build_cooldown_remaining_is_exactly_zero_with_no_prior_failure(self):
        # Regression guard: `.get(orb_arch, 0.0)` -- a mutant defaulting to 1.0
        # would report a phantom 1-second cooldown for an arch that never failed.
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        self.assertEqual(driver._build_cooldown_remaining("amd64"), 0.0)

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

    def test_promote_staging_to_base_stops_the_staging_vm_by_name(self):
        # Regression guard: existing promote tests all patch _stop_vm with
        # return_value=True, never asserting WHAT it was called with -- a mutant
        # that passed None (or base_name) instead of staging_name went
        # undetected despite _stop_vm shelling out to real `orbctl stop
        # <arg>` in production.
        with patch("subprocess.run") as mock_run, patch.object(self.driver, "_stop_vm", return_value=True) as mock_stop:
            mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([]))
            self.driver._promote_staging_to_base("runzero-vm-base-amd64-building", "runzero-vm-base-amd64")
        mock_stop.assert_called_once_with("runzero-vm-base-amd64-building")

    def test_promote_staging_to_base_subprocess_calls_have_expected_args(self):
        # Regression guard: every subprocess.run call site in this function
        # (pre-existing-destination delete, rename attempt, clone fallback,
        # post-clone staging delete) had zero exact-arg assertions -- kwarg
        # omission/None/False mutants on capture_output/text, and CLI flag
        # typos ("-f" -> "-F"), all survived silently.
        with patch("subprocess.run") as mock_run, patch.object(self.driver, "_stop_vm", return_value=True):
            mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([]))
            self.driver._promote_staging_to_base("staging-vm", "base-vm")
        mock_run.assert_any_call(
            ["orbctl", "rename", "staging-vm", "base-vm"],
            capture_output=True,
            text=True,
        )

    def test_promote_staging_to_base_deletes_existing_destination_with_expected_args(self):
        with (
            patch("subprocess.run") as mock_run,
            patch.object(self.driver, "_stop_vm", return_value=True),
            patch.object(self.driver, "_list_vm_names", return_value=["base-vm"]),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            self.driver._promote_staging_to_base("staging-vm", "base-vm")
        mock_run.assert_any_call(["orbctl", "delete", "-f", "base-vm"], capture_output=True)

    def test_promote_staging_to_base_clone_and_cleanup_calls_have_expected_args(self):
        def fake_run(cmd, *args, **kwargs):
            if cmd[:2] == ["orbctl", "rename"]:
                return MagicMock(returncode=1, stderr="locked")
            return MagicMock(returncode=0, stdout=json.dumps([]))

        with patch("subprocess.run") as mock_run, patch.object(self.driver, "_stop_vm", return_value=True), patch("time.sleep"):
            mock_run.side_effect = fake_run
            result = self.driver._promote_staging_to_base("staging-vm", "base-vm")
        self.assertTrue(result)
        mock_run.assert_any_call(["orbctl", "clone", "staging-vm", "base-vm"], capture_output=True, text=True)
        mock_run.assert_any_call(["orbctl", "delete", "-f", "staging-vm"], capture_output=True)

    def test_promote_staging_to_base_retries_rename_exactly_5_times(self):
        with patch("subprocess.run") as mock_run, patch.object(self.driver, "_stop_vm", return_value=True), patch("time.sleep"):

            def fake_run(cmd, *args, **kwargs):
                if cmd[:2] == ["orbctl", "rename"]:
                    return MagicMock(returncode=1, stderr="locked")
                return MagicMock(returncode=1, stdout=json.dumps([]))

            mock_run.side_effect = fake_run
            self.driver._promote_staging_to_base("staging-vm", "base-vm")
        rename_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "rename"]]
        self.assertEqual(len(rename_calls), 5)

    def test_promote_staging_to_base_rename_backoff_sleep_formula(self):
        # Regression guard: `time.sleep(1.0 + attempt * 0.5)` had no value
        # assertions -- wrong base, wrong operator (* -> /), or wrong
        # multiplier all survived.
        with patch("subprocess.run") as mock_run, patch.object(self.driver, "_stop_vm", return_value=True), patch("time.sleep") as mock_sleep:

            def fake_run(cmd, *args, **kwargs):
                if cmd[:2] == ["orbctl", "rename"]:
                    return MagicMock(returncode=1, stderr="locked")
                return MagicMock(returncode=1, stdout=json.dumps([]))

            mock_run.side_effect = fake_run
            self.driver._promote_staging_to_base("staging-vm", "base-vm")
        expected = [call(1.0 + attempt * 0.5) for attempt in range(5)]
        mock_sleep.assert_has_calls(expected)

    def test_read_provision_script_missing_file_error_message(self):
        with patch("os.path.isfile", return_value=False), patch("builtins.print") as mock_print:
            result = self.driver._read_provision_script()
        self.assertIsNone(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("shared provisioning script not found at", printed)
        self.assertIn(self.driver._provision_script_path, printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    def test_read_provision_script_opens_exact_path_and_returns_contents(self):
        with patch("os.path.isfile", return_value=True), patch("builtins.open", mock_open(read_data="script contents")) as mock_file:
            result = self.driver._read_provision_script()
        self.assertEqual(result, "script contents")
        mock_file.assert_called_once_with(self.driver._provision_script_path)

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

    def test_spawn_cooldown_remaining_is_exactly_zero_with_no_prior_failure(self):
        self.assertEqual(self.driver._spawn_cooldown_remaining("amd64"), 0.0)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_returns_true_immediately_when_vm_missing_from_list(self, mock_run, mock_sleep):
        # Regression guard: `.get(vm_name, "stopped")` -- a VM that's already
        # gone from `orbctl list`'s output (deleted/renamed between polls)
        # must be treated as "stopped" (the safe default), not queried again
        # for the full 3x10 retry budget. A mutant defaulting to None instead
        # would force every one of those 30 iterations before giving up.
        mock_run.return_value = MagicMock(stdout=json.dumps([]), returncode=0)
        result = self.driver._stop_vm("already-gone-vm")
        self.assertTrue(result)
        list_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "list"]]
        self.assertEqual(len(list_calls), 1)

    @patch("subprocess.run")
    def test_stop_vm_subprocess_calls_have_expected_args(self, mock_run):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "stopped"}]), returncode=0)
        self.driver._stop_vm("test-vm")
        mock_run.assert_any_call(["orbctl", "stop", "test-vm"], capture_output=True)
        mock_run.assert_any_call(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_polls_exactly_10_times_per_attempt_with_1s_sleep(self, mock_run, mock_sleep):
        # Regression guard: the inner `for _ in range(10)` poll loop and the
        # `time.sleep(1)` between polls both had zero value assertions.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "running"}]), returncode=0)
        self.driver._stop_vm("test-vm")
        list_calls = [c for c in mock_run.call_args_list if c.args[0][:2] == ["orbctl", "list"]]
        self.assertEqual(len(list_calls), 30)  # 3 outer attempts x 10 inner polls
        mock_sleep.assert_called_with(1)
        self.assertEqual(mock_sleep.call_count, 30)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_stop_vm_gives_up_message_content(self, mock_run, mock_sleep):
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "test-vm", "state": "running"}]), returncode=0)
        with patch("builtins.print") as mock_print:
            result = self.driver._stop_vm("test-vm")
        self.assertFalse(result)
        printed = " ".join(str(a) for a in mock_print.call_args.args)
        self.assertIn("test-vm", printed)
        self.assertIn("did not confirm stopped", printed)
        self.assertEqual(mock_print.call_args.kwargs.get("file"), sys.stderr)

    @patch("subprocess.run")
    def test_base_image_exists_skips_promotion_while_actively_building(self, mock_run):
        # Regression guard: `being_built = orb_arch in self._building_arches`
        # gates whether a fully-provisioned staging VM gets auto-promoted.
        # No existing test exercised the branch where a build IS actively
        # in progress for this arch -- an `and`->`or` mutant, or the guard
        # being replaced outright, would let this auto-promote a staging VM
        # out from under a build that's still running against it.
        mock_run.return_value = MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64-building", "state": "stopped"}]), returncode=0)
        self.driver._building_arches.add("amd64")
        with (
            patch.object(self.driver, "_is_staging_provisioned", return_value=True) as mock_provisioned,
            patch.object(self.driver, "_promote_staging_to_base") as mock_promote,
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
            patch.object(self.driver, "_is_staging_provisioned", return_value=True) as mock_provisioned,
            patch.object(self.driver, "_promote_staging_to_base", return_value=True) as mock_promote,
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
        with patch.object(self.driver, "_is_staging_provisioned", return_value=False), patch.object(self.driver, "_promote_staging_to_base") as mock_promote:
            result = self.driver.base_image_exists("amd64")
        self.assertFalse(result)
        mock_promote.assert_not_called()

    # -- build_base_image mutation-triage additions (issue #30, continued) ------
    # Regression guards for build_base_image()'s many _report_image_event()/print()
    # call sites: none had exact-argument assertions, so a mutant swapping any
    # status/arch/detail value for None or a mangled string survived. Each test
    # below captures real events via `_on_image_event` and drives one branch.

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
            patch.object(self.driver, "base_image_exists", return_value=False),
            patch.object(self.driver, "_list_vm_names", return_value=["runzero-vm-base-amd64-building"]),
            patch.object(self.driver, "_is_staging_provisioned", return_value=True) as mock_provisioned,
            patch.object(self.driver, "_promote_staging_to_base", return_value=True) as mock_promote,
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

    @patch.dict(os.environ, {"RUNNER_CPUS": "2", "RUNNER_MEMORY": "4g"})
    @patch("subprocess.run")
    def test_build_base_image_passes_configured_resource_limits_to_create(self, mock_run):
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
                "4g",
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
            patch.object(self.driver, "_read_provision_script", return_value="echo hello-provision-marker"),
            patch.object(self.driver, "_promote_staging_to_base", return_value=True),
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
        with patch.object(self.driver, "_promote_staging_to_base", return_value=False):
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
        with patch.object(self.driver, "_promote_staging_to_base", return_value=True), patch("builtins.print") as mock_print:
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
        self.driver._building_arches.add("amd64")
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
            patch.object(self.driver, "_stop_vm") as mock_stop,
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
            patch.object(self.driver, "_is_staging_provisioned", return_value=True),
            patch.object(self.driver, "_promote_staging_to_base") as mock_promote,
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
        self.driver._building_arches.add("arm64")
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
        self.driver._build_retry_after["arm64"] = time.monotonic() + 42
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

    def test_join_background_build_threads_default_timeout_is_10_seconds(self):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        release = threading.Event()

        def blocked(arch):
            release.wait(timeout=5)
            return True

        with patch.object(driver, "build_base_image", side_effect=blocked):
            driver._build_base_image_async("amd64")
            thread = driver._build_threads["amd64"]
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

    # -- spawn_runner mutation-triage additions (issue #30, continued) ----------

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
    def test_spawn_runner_custom_labels_override_default(self, mock_run, mock_popen):
        mock_run.side_effect = [
            MagicMock(stdout=json.dumps([{"name": "runzero-vm-base-amd64", "state": "stopped"}]), returncode=0),
            MagicMock(returncode=0),
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="token", labels="my,custom,labels")
        setup_script = mock_popen.call_args[0][0][-1]
        self.assertIn("my,custom,labels", setup_script)
        self.assertNotIn("self-hosted,local,vm,amd64", setup_script)

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
