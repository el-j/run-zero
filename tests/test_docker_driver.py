"""
Unit tests for Docker container runner driver.
"""

import json
import os
import subprocess
import time
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from drivers.docker_driver import DockerDriver


class TestDockerDriver(unittest.TestCase):
    def setUp(self):
        # Spawning exchanges the PAT for a registration token via the GitHub API; stub it.
        _reg = patch("drivers.create_registration_token", return_value="reg-token")
        self.create_registration_token = _reg.start()
        self.addCleanup(_reg.stop)
        # A "missing image" answer from mocked subprocess.run would otherwise start a real
        # background `docker buildx build` thread that outlives this test's mocks.
        _build = patch.object(DockerDriver, "_build_runner_image_async")
        self.build_runner_image_async = _build.start()
        self.addCleanup(_build.stop)
        self.driver = DockerDriver()

    def test_name(self):
        self.assertEqual(self.driver.name(), "docker")

    def test_init_defaults(self):
        # Mutation-prone: every default value here (docker_sock path, network mode,
        # runner_image_prefix, registry-mirror-checked flag) was previously unasserted,
        # so a broken default (e.g. runner_image_prefix silently becoming None) would
        # have gone undetected until it broke image tagging in production.
        env = dict(os.environ)
        env.pop("DOCKER_SOCK", None)
        env.pop("DOCKER_NETWORK", None)
        with patch.dict(os.environ, env, clear=True):
            driver = DockerDriver()
        self.assertEqual(driver.docker_sock, "/var/run/docker.sock")
        self.assertEqual(driver.network, "host")
        self.assertEqual(driver.runner_image_prefix, "local-github-runner")
        self.assertIs(driver._registry_mirror_checked, False)
        self.assertEqual(driver._backoff.failure_counts, {})
        self.assertEqual(driver._backoff.retry_after, {})

    def test_init_env_vars_override_constructor_defaults(self):
        # DOCKER_SOCK/DOCKER_NETWORK env vars must win over the constructor's own
        # defaults -- this is how docker-compose.yml configures the autoscaler.
        with patch.dict(os.environ, {"DOCKER_SOCK": "/custom/docker.sock", "DOCKER_NETWORK": "bridge"}):
            driver = DockerDriver()
        self.assertEqual(driver.docker_sock, "/custom/docker.sock")
        self.assertEqual(driver.network, "bridge")

    def test_init_custom_runner_image_prefix_is_stored_verbatim(self):
        driver = DockerDriver(runner_image_prefix="custom-prefix")
        self.assertEqual(driver.runner_image_prefix, "custom-prefix")

    def test_normalize_arch_recognizes_all_amd64_synonyms(self):
        # Mutation-prone: this static method had zero direct tests. A case-sensitivity
        # or synonym-list regression here silently misroutes architecture-specific
        # image tags/builds for every caller in the codebase.
        for synonym in ("amd64", "x64", "x86_64"):
            self.assertEqual(DockerDriver._normalize_arch(synonym), "amd64")

    def test_normalize_arch_falls_back_to_arm64_for_anything_else(self):
        self.assertEqual(DockerDriver._normalize_arch("arm64"), "arm64")
        self.assertEqual(DockerDriver._normalize_arch("unknown-arch"), "arm64")

    def test_image_tag_for_arch(self):
        driver = DockerDriver(runner_image_prefix="my-prefix")
        self.assertEqual(driver._image_tag_for_arch("x64"), "my-prefix:amd64")
        self.assertEqual(driver._image_tag_for_arch("arm64"), "my-prefix:arm64")

    @patch("subprocess.run")
    def test_image_exists_true_on_returncode_zero(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver._image_exists("amd64"))
        mock_run.assert_called_once_with(["docker", "image", "inspect", "local-github-runner:amd64"], capture_output=True)

    @patch("subprocess.run")
    def test_image_exists_false_on_nonzero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(self.driver._image_exists("amd64"))

    @patch("subprocess.run", side_effect=OSError("docker not found"))
    def test_image_exists_false_on_exception(self, mock_run):
        self.assertFalse(self.driver._image_exists("amd64"))

    def test_build_cooldown_remaining_zero_when_never_failed(self):
        self.assertEqual(self.driver._backoff.remaining("amd64"), 0.0)

    @patch("shutil.which", return_value="/usr/local/bin/docker")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())
        mock_which.assert_called_once_with("docker")
        mock_run.assert_called_once_with(["docker", "info"], capture_output=True, timeout=5)

    @patch("shutil.which", return_value="/usr/local/bin/docker")
    @patch("subprocess.run")
    def test_is_available_false_on_nonzero_returncode(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value=None)
    def test_is_available_when_no_binary(self, mock_which):
        self.assertFalse(self.driver.is_available())

    @patch("shutil.which", return_value="/usr/local/bin/docker")
    @patch("subprocess.run")
    def test_is_available_when_error(self, mock_run, mock_which):
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
        self.assertFalse(self.driver.is_available())

    @patch("subprocess.run")
    def test_list_runners_parsing(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=(
                "runner1|Up 2 hours|local-runner-arm64-el-j-run-zero-123|running|el-j/run-zero|arm64|docker\n"
                "runner2|Exited (0)|local-runner-amd64-my-org-456|exited|my-org|amd64|docker\n"
            ),
            returncode=0,
        )
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)
        self.assertEqual(runners[0].name, "local-runner-arm64-el-j-run-zero-123")
        self.assertEqual(runners[0].target_arch, "arm64")
        self.assertEqual(runners[0].state, "running")
        self.assertEqual(runners[0].target_repo, "el-j/run-zero")

        self.assertEqual(runners[1].name, "local-runner-amd64-my-org-456")
        self.assertEqual(runners[1].target_arch, "amd64")
        self.assertEqual(runners[1].state, "exited")

    @patch("subprocess.run")
    def test_list_runners_parses_created_at(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="runner1|Up 2 hours|local-runner-arm64-1|running|el-j/run-zero|arm64|docker|2026-08-25 14:38:53 +0200 CEST\n", returncode=0
        )
        runners = self.driver.list_runners()
        self.assertIsNotNone(runners[0].created_at)

    def test_parse_created_at_invalid_returns_none(self):
        self.assertIsNone(self.driver._parse_created_at("not a timestamp"))

    @patch("subprocess.run")
    def test_list_runners_created_and_restarting_are_pending(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="r1|Created|c1|created|el-j/run-zero|arm64|docker\nr2|Restarting|c2|restarting|el-j/run-zero|arm64|docker\n", returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(runners[0].state, "pending")
        self.assertEqual(runners[1].state, "pending")

    @patch("subprocess.run")
    def test_list_runners_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker")
        runners = self.driver.list_runners()
        self.assertEqual(runners, [])

    @patch("subprocess.run")
    def test_spawn_runner_arm64_and_amd64(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        # Spawn for Repo
        name_arm = self.driver.spawn_runner(
            repo="el-j/run-zero", arch="arm64", access_token="secret-pat", cache_mounts={"/host/cache": "/home/runner/.cache"}, proxies_enabled=True
        )
        assert name_arm is not None
        self.assertIn("local-runner-arm64-el-j-run-zero-", name_arm)

        # Spawn for Org
        name_amd = self.driver.spawn_runner(org="my-org", arch="amd64", access_token="secret-pat", proxies_enabled=False)
        assert name_amd is not None
        self.assertIn("local-runner-amd64-my-org-", name_amd)

    @patch("subprocess.run")
    def test_spawn_runner_omits_resource_flags_when_unset(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="tok")
        cmd = mock_run.call_args[0][0]
        self.assertNotIn("--cpus", cmd)
        self.assertNotIn("--memory", cmd)

    @patch.dict(os.environ, {"RUNNER_CPUS": "2", "RUNNER_MEMORY": "4g"})
    @patch("subprocess.run")
    def test_spawn_runner_passes_configured_resource_limits(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        driver = DockerDriver()
        driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="tok")
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[cmd.index("--cpus") + 1], "2")
        self.assertEqual(cmd[cmd.index("--memory") + 1], "4g")

    @patch("subprocess.run")
    def test_spawn_runner_uses_configured_network_mode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        driver_host = DockerDriver(network="host")
        driver_host.spawn_runner(repo="el-j/herbful", arch="arm64", access_token="tok")
        cmd = mock_run.call_args[0][0]
        net_idx = cmd.index("--network")
        self.assertEqual(cmd[net_idx + 1], "host")

    @patch("subprocess.run")
    def test_spawn_runner_passes_cache_mount_dests_env(self, mock_run):
        # start.sh fixes ownership of the *container-side* mount destinations
        # (Docker/OrbStack create their ancestors as root) using this env var as
        # its source of truth. It must carry exactly the values of cache_mounts,
        # or the two can silently drift apart again — see the .nuget/packages /
        # go/pkg vs go/pkg/mod bug this fix addresses.
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(
            repo="el-j/run-zero",
            arch="arm64",
            access_token="secret-pat",
            cache_mounts={
                "/host/npm": "/home/runner/.npm",
                "/host/go-pkg": "/home/runner/go/pkg",
                "/host/dotnet": "/home/runner/.nuget/packages",
            },
        )
        cmd = mock_run.call_args[0][0]
        env_pairs = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        dest_entries = [p for p in env_pairs if p.startswith("CACHE_MOUNT_DESTS=")]
        self.assertEqual(len(dest_entries), 1)
        dests = dest_entries[0][len("CACHE_MOUNT_DESTS=") :].split(":")
        self.assertEqual(
            set(dests),
            {"/home/runner/.npm", "/home/runner/go/pkg", "/home/runner/.nuget/packages"},
        )

    @patch("subprocess.run")
    def test_spawn_runner_omits_cache_mount_dests_env_when_no_mounts(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="secret-pat")
        cmd = mock_run.call_args[0][0]
        env_pairs = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        self.assertFalse(any(p.startswith("CACHE_MOUNT_DESTS=") for p in env_pairs))

    @patch("subprocess.run")
    def test_spawn_runner_sets_pip_env_on_host_network(self, mock_run):
        # devpi's pull-through PyPI proxy: on --network host (this driver's default),
        # the published localhost port is reachable directly and pip implicitly trusts
        # localhost for plain HTTP, so no PIP_TRUSTED_HOST is needed.
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="tok", proxies_enabled=True)
        cmd = mock_run.call_args[0][0]
        env_values = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        pip_entries = [v for v in env_values if v.startswith("PIP_INDEX_URL=")]
        uv_entries = [v for v in env_values if v.startswith("UV_INDEX_URL=")]
        self.assertEqual(pip_entries, ["PIP_INDEX_URL=http://localhost:49507/root/pypi/+simple/"])
        self.assertEqual(uv_entries, ["UV_INDEX_URL=http://localhost:49507/root/pypi/+simple/"])
        self.assertFalse(any(v.startswith("PIP_TRUSTED_HOST=") for v in env_values))

    @patch("subprocess.run")
    def test_spawn_runner_sets_pip_trusted_host_on_non_host_network(self, mock_run):
        # Off --network host, PIP_INDEX_URL must point at the "devpi" Compose service
        # name (localhost wouldn't reach a sibling container) -- and pip refuses a
        # plain-HTTP index on any host other than localhost/127.0.0.1 unless it's
        # explicitly trusted (verified live: without this, pip silently installs
        # nothing and still exits 0).
        mock_run.return_value = MagicMock(returncode=0)
        driver = DockerDriver(network="runner-network")
        driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="tok", proxies_enabled=True)
        cmd = mock_run.call_args[0][0]
        env_values = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        self.assertIn("PIP_INDEX_URL=http://devpi:3141/root/pypi/+simple/", env_values)
        self.assertIn("UV_INDEX_URL=http://devpi:3141/root/pypi/+simple/", env_values)
        self.assertIn("PIP_TRUSTED_HOST=devpi", env_values)

    @patch("subprocess.run")
    def test_spawn_runner_omits_pip_env_when_proxies_disabled(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="tok", proxies_enabled=False)
        cmd = mock_run.call_args[0][0]
        env_values = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        self.assertFalse(any(v.startswith("PIP_INDEX_URL=") for v in env_values))
        self.assertFalse(any(v.startswith("UV_INDEX_URL=") for v in env_values))

    @patch("subprocess.run")
    def test_spawn_runner_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker", stderr=b"Docker daemon error")
        name = self.driver.spawn_runner(repo="el-j/run-zero")
        self.assertIsNone(name)

    @patch("subprocess.run")
    def test_prune_and_destroy(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="r1", name="runner-dead", status="exited", state="exited", target_repo="", target_arch="arm64", backend="docker"),
            RunnerInfo(id="r2", name="runner-live", status="running", state="running", target_repo="", target_arch="arm64", backend="docker"),
            RunnerInfo(id="r3", name="runner-vm", status="exited", state="exited", target_repo="", target_arch="arm64", backend="orbstack-vm"),
        ]
        self.driver.prune_exited(runners)
        self.driver.destroy_runner("runner-dead")
        self.driver.cleanup_all()

    @patch("subprocess.run")
    def test_prune_exited_only_removes_docker_backed_exited_or_dead_runners(self, mock_run):
        # Mutation-prone / correctness-critical: `backend == "docker" and state in
        # (exited, dead)` mutated to `or` (or negated) would make this method reach
        # across backend boundaries and force-remove OTHER drivers' runners (e.g. a
        # live OrbStack VM) just because ITS state happened to match, or skip real
        # exited Docker containers entirely. This was previously asserted on nothing.
        mock_run.return_value = MagicMock(returncode=0)
        runners = [
            RunnerInfo(id="r1", name="docker-exited", status="exited", state="exited", target_repo="", target_arch="arm64", backend="docker"),
            RunnerInfo(id="r2", name="docker-dead", status="dead", state="dead", target_repo="", target_arch="arm64", backend="docker"),
            RunnerInfo(id="r3", name="docker-running", status="running", state="running", target_repo="", target_arch="arm64", backend="docker"),
            RunnerInfo(id="r4", name="vm-exited", status="exited", state="exited", target_repo="", target_arch="arm64", backend="orbstack-vm"),
        ]
        self.driver.prune_exited(runners)
        rm_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["docker", "rm"]]
        removed_ids = {c[0][0][3] for c in rm_calls}
        self.assertEqual(removed_ids, {"r1", "r2"})

    @patch("subprocess.run")
    def test_cleanup_all_stops_and_removes_docker_backed_runners(self, mock_run):
        # Regression guard: cleanup_all() must only stop+remove runners whose
        # backend is actually "docker" -- list_runners() itself is real here
        # (only subprocess.run is mocked), so this exercises the real
        # filtering loop in cleanup_all() rather than relying on
        # list_runners() failing closed to an empty list.
        mock_run.return_value = MagicMock(stdout="c1|Up|local-runner-arm64-1|running|el-j/run-zero|arm64|docker\n", returncode=0)
        self.driver.cleanup_all()
        stop_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["docker", "stop"]]
        rm_calls = [c for c in mock_run.call_args_list if c[0][0][:2] == ["docker", "rm"]]
        self.assertEqual(len(stop_calls), 1)
        self.assertEqual(len(rm_calls), 1)
        self.assertEqual(stop_calls[0][0][0], ["docker", "stop", "c1"])

    @patch("subprocess.run")
    def test_spawn_runner_with_extra_env(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(
            repo="el-j/run-zero",
            arch="arm64",
            access_token="secret-pat",
            extra_env={"FOO": "bar", "BAZ": "qux"},
        )
        cmd = mock_run.call_args[0][0]
        env_pairs = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        self.assertIn("FOO=bar", env_pairs)
        self.assertIn("BAZ=qux", env_pairs)

    @patch("subprocess.run")
    def test_list_runners_skips_blank_lines(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="c1|Up|local-runner-arm64-1|running|el-j/run-zero|arm64|docker\n\nc2|Up|local-runner-arm64-2|running|el-j/run-zero|arm64|docker\n",
            returncode=0,
        )
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)

    @patch("subprocess.run")
    def test_spawn_runner_default_labels_amd64_includes_x64(self, mock_run):
        # Mutation-prone: spawn_runner should pick default labels that include
        # both amd64 AND x64 when arch=="amd64" (not just "amd64" alone),
        # because CI/CD systems may label with x64 or amd64 interchangeably.
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        cmd = mock_run.call_args[0][0]
        env_pairs = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        runner_label_env = [p for p in env_pairs if p.startswith("RUNNER_LABELS=")]
        self.assertEqual(len(runner_label_env), 1)
        labels = runner_label_env[0][len("RUNNER_LABELS=") :].split(",")
        self.assertIn("self-hosted", labels)
        self.assertIn("local", labels)
        self.assertIn("x64", labels)
        self.assertIn("amd64", labels)

    @patch("subprocess.run")
    def test_spawn_runner_job_labels_are_merged_with_defaults(self, mock_run):
        # #46: the job's runs-on labels are ADDED to the driver defaults (deduplicated,
        # case-insensitively); replacing them would drop the routing labels.
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="tok", labels="Self-Hosted,gpu,label-set")
        cmd = mock_run.call_args[0][0]
        env_pairs = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        runner_label_env = [p for p in env_pairs if p.startswith("RUNNER_LABELS=")]
        self.assertEqual(runner_label_env, ["RUNNER_LABELS=self-hosted,local,arm64,gpu,label-set"])

    @patch("subprocess.run")
    def test_spawn_runner_default_labels_arm64(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", access_token="tok")
        cmd = mock_run.call_args[0][0]
        env_pairs = [cmd[i + 1] for i, tok in enumerate(cmd) if tok == "-e"]
        runner_label_env = [p for p in env_pairs if p.startswith("RUNNER_LABELS=")]
        self.assertEqual(len(runner_label_env), 1)
        labels = runner_label_env[0][len("RUNNER_LABELS=") :].split(",")
        self.assertIn("arm64", labels)
        self.assertNotIn("x64", labels)

    @patch("subprocess.run")
    def test_list_runners_maps_every_field_to_the_correct_column(self, mock_run):
        # Mutation-prone: `.id`/`.status` were never asserted anywhere, so a column-index
        # swap (e.g. status=parts[2] instead of parts[1]) went completely undetected.
        mock_run.return_value = MagicMock(stdout="cid1|status-text|name1|running|repo1|arm64|docker\n", returncode=0)
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        r = runners[0]
        self.assertEqual(r.id, "cid1")
        self.assertEqual(r.status, "status-text")
        self.assertEqual(r.name, "name1")
        self.assertEqual(r.state, "running")
        self.assertEqual(r.target_repo, "repo1")
        self.assertEqual(r.target_arch, "arm64")
        self.assertEqual(r.backend, "docker")

    @patch("subprocess.run")
    def test_list_runners_minimal_six_field_line_is_still_parsed(self, mock_run):
        # Mutation-prone: `len(parts) >= 6` mutated to `>= 7` would silently drop every
        # line that has no backend/created_at columns (older `docker ps` format).
        mock_run.return_value = MagicMock(stdout="cid1|status-text|name1|running|repo1|arm64\n", returncode=0)
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].backend, "docker")
        self.assertIsNone(runners[0].created_at)

    @patch("subprocess.run")
    def test_list_runners_backend_defaults_to_docker_when_missing(self, mock_run):
        # When backend field (parts[6]) is empty or missing, it should
        # default to "docker" not silently become None/empty.
        mock_run.return_value = MagicMock(stdout="c1|Up|runner1|running|el-j/run-zero|arm64||\n", returncode=0)
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 1)
        self.assertEqual(runners[0].backend, "docker")

    @patch("subprocess.run")
    def test_spawn_runner_goproxy_url_changes_by_network(self, mock_run):
        # GOPROXY must use localhost:49500 on --network host, and athens:3000
        # on other networks (for Athens Compose service discovery).
        mock_run.return_value = MagicMock(returncode=0)

        # Host network
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=True, access_token="tok")
        cmd_host = mock_run.call_args[0][0]
        env_host = [cmd_host[i + 1] for i, tok in enumerate(cmd_host) if tok == "-e"]
        goproxy_host = [v for v in env_host if v.startswith("GOPROXY=")]
        self.assertTrue(any("localhost:49500" in v for v in goproxy_host))

        # Non-host network
        driver_bridge = DockerDriver(network="runner-network")
        driver_bridge.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=True, access_token="tok")
        cmd_bridge = mock_run.call_args[0][0]
        env_bridge = [cmd_bridge[i + 1] for i, tok in enumerate(cmd_bridge) if tok == "-e"]
        goproxy_bridge = [v for v in env_bridge if v.startswith("GOPROXY=")]
        self.assertTrue(any("athens:3000" in v for v in goproxy_bridge))

    @patch("subprocess.run")
    def test_spawn_runner_npm_registry_url_changes_by_network(self, mock_run):
        # NPM_CONFIG_REGISTRY must use localhost:49501 on --network host,
        # and verdaccio:4873 on other networks.
        mock_run.return_value = MagicMock(returncode=0)

        # Host network
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=True, access_token="tok")
        cmd_host = mock_run.call_args[0][0]
        env_host = [cmd_host[i + 1] for i, tok in enumerate(cmd_host) if tok == "-e"]
        npm_host = [v for v in env_host if v.startswith("NPM_CONFIG_REGISTRY=")]
        self.assertEqual(len(npm_host), 1)
        self.assertIn("localhost:49501", npm_host[0])

        # Non-host network
        driver_bridge = DockerDriver(network="runner-network")
        driver_bridge.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=True, access_token="tok")
        cmd_bridge = mock_run.call_args[0][0]
        env_bridge = [cmd_bridge[i + 1] for i, tok in enumerate(cmd_bridge) if tok == "-e"]
        npm_bridge = [v for v in env_bridge if v.startswith("NPM_CONFIG_REGISTRY=")]
        self.assertEqual(len(npm_bridge), 1)
        self.assertIn("verdaccio:4873", npm_bridge[0])

    @patch("subprocess.run")
    def test_spawn_runner_exports_pnpm_registry_and_cache_env(self, mock_run):
        # pnpm 11 reads only pnpm_config_* (#67); mounted caches add store/browser paths (#68).
        mock_run.return_value = MagicMock(returncode=0)
        mounts = {"/host/pnpm": "/home/runner/.local/share/pnpm/store"}
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=True, access_token="tok", cache_mounts=mounts)
        cmd = mock_run.call_args[0][0]
        env = dict(cmd[i + 1].split("=", 1) for i, tok in enumerate(cmd) if tok == "-e")
        self.assertEqual(env["pnpm_config_registry"], "http://localhost:49501/")
        self.assertEqual(env["YARN_NPM_REGISTRY_SERVER"], "http://localhost:49501/")
        self.assertEqual(env["RUNNER_TOOL_CACHE"], "/opt/hostedtoolcache")
        self.assertEqual(env["RUNZERO"], "1")
        self.assertEqual(env["pnpm_config_store_dir"], "/home/runner/.local/share/pnpm/store")
        self.assertEqual(env["PLAYWRIGHT_BROWSERS_PATH"], "/home/runner/.cache/ms-playwright")

    @patch("subprocess.run")
    def test_spawn_runner_without_cache_mounts_keeps_tool_defaults(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=False, access_token="tok")
        cmd = mock_run.call_args[0][0]
        env = dict(cmd[i + 1].split("=", 1) for i, tok in enumerate(cmd) if tok == "-e")
        self.assertEqual(env["RUNNER_TOOL_CACHE"], "/opt/hostedtoolcache")
        self.assertNotIn("PLAYWRIGHT_BROWSERS_PATH", env)
        self.assertNotIn("pnpm_config_registry", env)

    @patch("builtins.print")
    @patch("subprocess.run")
    def test_spawn_runner_warns_when_registry_mirror_missing(self, mock_run, mock_print):
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker image inspect
            MagicMock(returncode=0, stdout="[]\n"),  # docker info mirrors
            MagicMock(returncode=0),  # docker run
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=True, access_token="tok")
        warning_calls = [c for c in mock_print.call_args_list if c.args and "registry mirror" in str(c.args[0]).lower()]
        self.assertEqual(len(warning_calls), 1)

    @patch("builtins.print")
    @patch("subprocess.run")
    def test_spawn_runner_no_warning_when_registry_mirror_configured(self, mock_run, mock_print):
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker image inspect
            MagicMock(returncode=0, stdout='["http://localhost:49502"]\n'),  # docker info mirrors
            MagicMock(returncode=0),  # docker run
        ]
        self.driver.spawn_runner(repo="el-j/run-zero", arch="arm64", proxies_enabled=True, access_token="tok")
        warning_calls = [c for c in mock_print.call_args_list if c.args and "registry mirror" in str(c.args[0]).lower()]
        self.assertEqual(len(warning_calls), 0)

    def test_resolve_build_context_dir_uses_env_var_when_set(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            for name in ("Dockerfile", "provision-toolchain.sh", "start.sh"):
                open(os.path.join(tmp, name), "w").close()
            with patch.dict(os.environ, {"RUNNER_IMAGE_DOCKER_DIR": tmp}):
                self.assertEqual(self.driver._resolve_build_context_dir(), tmp)

    @patch("os.path.isfile", return_value=False)
    def test_resolve_build_context_dir_returns_none_when_nothing_found(self, mock_isfile):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RUNNER_IMAGE_DOCKER_DIR", None)
            self.assertIsNone(self.driver._resolve_build_context_dir())

    def test_resolve_build_context_dir_requires_all_three_files(self):
        # Mutation-prone / outage-relevant: this method's validation must be a full
        # AND across Dockerfile + provision-toolchain.sh + start.sh -- a directory
        # missing even one of the three must be rejected, not treated as a usable
        # build context (this is the exact class of bug behind the 2026-09-22
        # docker-compose.yml outage: a mount pointing at an incomplete directory).
        # `os.path.isfile` is scoped to `tmp` only so this repo's own real `docker/`
        # directory (a valid later fallback candidate) can't mask the assertion.
        import tempfile

        real_isfile = os.path.isfile

        with tempfile.TemporaryDirectory() as tmp:

            def scoped_isfile(path):
                if not str(path).startswith(tmp):
                    return False
                return real_isfile(path)

            with patch.dict(os.environ, {"RUNNER_IMAGE_DOCKER_DIR": tmp}), patch("os.path.isfile", side_effect=scoped_isfile):
                # Nothing present yet.
                self.assertIsNone(self.driver._resolve_build_context_dir())

                open(os.path.join(tmp, "Dockerfile"), "w").close()
                self.assertIsNone(self.driver._resolve_build_context_dir())

                open(os.path.join(tmp, "provision-toolchain.sh"), "w").close()
                self.assertIsNone(self.driver._resolve_build_context_dir())

                # Only once all three exist does it become a valid build context.
                open(os.path.join(tmp, "start.sh"), "w").close()
                self.assertEqual(self.driver._resolve_build_context_dir(), tmp)

    def test_warn_if_registry_mirror_missing_short_circuits_when_already_checked(self):
        self.driver._registry_mirror_checked = True
        with patch("subprocess.run") as mock_run:
            self.driver._warn_if_registry_mirror_missing()
            mock_run.assert_not_called()

    @patch("subprocess.run", side_effect=OSError("docker not found"))
    def test_warn_if_registry_mirror_missing_swallows_subprocess_exception(self, mock_run):
        self.driver._warn_if_registry_mirror_missing()  # must not raise
        self.assertTrue(self.driver._registry_mirror_checked)

    @patch("subprocess.run")
    def test_warn_if_registry_mirror_missing_returns_when_docker_info_fails(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        with patch("builtins.print") as mock_print:
            self.driver._warn_if_registry_mirror_missing()
        self.assertFalse(any("registry mirror" in str(c.args[0]).lower() for c in mock_print.call_args_list if c.args))

    @patch("subprocess.run")
    def test_warn_if_registry_mirror_missing_returns_on_invalid_json(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="not json")
        with patch("builtins.print") as mock_print:
            self.driver._warn_if_registry_mirror_missing()
        self.assertFalse(any("registry mirror" in str(c.args[0]).lower() for c in mock_print.call_args_list if c.args))

    @patch("subprocess.run")
    def test_warn_if_registry_mirror_missing_returns_when_mirrors_not_a_list(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"unexpected": "shape"}')
        with patch("builtins.print") as mock_print:
            self.driver._warn_if_registry_mirror_missing()
        self.assertFalse(any("registry mirror" in str(c.args[0]).lower() for c in mock_print.call_args_list if c.args))

    @patch("subprocess.run")
    def test_warn_if_registry_mirror_missing_silent_when_mirror_configured(self, mock_run):
        for mirror in ("http://localhost:49502/", "https://host.orb.internal:49502"):
            with self.subTest(mirror=mirror):
                self.driver._registry_mirror_checked = False
                mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps([mirror]))
                with patch("builtins.print") as mock_print:
                    self.driver._warn_if_registry_mirror_missing()
                mock_print.assert_not_called()


class TestDockerDriverSpawnErrorPaths(unittest.TestCase):
    def setUp(self):
        # Spawning exchanges the PAT for a registration token via the GitHub API; stub it.
        _reg = patch("drivers.create_registration_token", return_value="reg-token")
        self.create_registration_token = _reg.start()
        self.addCleanup(_reg.stop)
        self.driver = DockerDriver()

    @patch("subprocess.run")
    def test_spawn_runner_image_unavailable_triggers_rebuild_and_returns_none(self, mock_run):
        def _side_effect(cmd, **kwargs):
            if cmd[:2] == ["docker", "image"]:
                return MagicMock(returncode=0)  # ensure_runtime_assets: image "exists"
            if cmd[:2] == ["docker", "run"]:
                raise subprocess.CalledProcessError(1, cmd, stderr=b"Unable to find image 'x' locally")
            return MagicMock(returncode=0)

        mock_run.side_effect = _side_effect
        with patch("threading.Thread", _SyncThread), patch.object(DockerDriver, "_build_runner_image", return_value=True):
            result = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        self.assertIsNone(result)

    @patch("subprocess.run")
    def test_spawn_runner_other_launch_failure_returns_none(self, mock_run):
        def _side_effect(cmd, **kwargs):
            if cmd[:2] == ["docker", "image"]:
                return MagicMock(returncode=0)
            if cmd[:2] == ["docker", "run"]:
                raise subprocess.CalledProcessError(1, cmd, stderr=b"some other docker daemon error")
            return MagicMock(returncode=0)

        mock_run.side_effect = _side_effect
        result = self.driver.spawn_runner(repo="el-j/run-zero", arch="amd64", access_token="tok")
        self.assertIsNone(result)


class TestDockerDriverBasics(unittest.TestCase):
    def setUp(self):
        self.driver = DockerDriver()

    @patch("subprocess.run")
    def test_destroy_runner_returns_true_on_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = self.driver.destroy_runner("runner-id")
        self.assertTrue(result)

    @patch("subprocess.run")
    def test_destroy_runner_returns_false_on_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        result = self.driver.destroy_runner("runner-id")
        self.assertFalse(result)


class _SyncThread:
    """Drop-in threading.Thread stand-in that runs its target synchronously on start().

    Lets tests exercise _build_runner_image_async()'s background-thread body
    deterministically without a real thread/sleep-and-poll dance.
    """

    def __init__(self, target=None, name=None, daemon=None):
        self._target = target

    def start(self):
        self._target()


class TestDockerDriverImageBuildReporting(unittest.TestCase):
    """Covers the golden-image build lifecycle: _build_runner_image, its async wrapper,
    ensure_runtime_assets, and the structured on_image_event reporting hook -- none of
    this was previously under test, leaving the entire build path uncovered."""

    def setUp(self):
        self.events: list[dict[str, Any]] = []
        self.driver = DockerDriver(on_image_event=self.events.append)

    def test_report_image_event_calls_callback_with_expected_shape(self):
        self.driver._report_image_event("ready", "amd64", "all good", profile="cuda")
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertEqual(event["driver"], "docker")
        self.assertEqual(event["arch"], "amd64")
        self.assertEqual(event["profile"], "cuda")
        self.assertEqual(event["status"], "ready")
        self.assertEqual(event["detail"], "all good")
        self.assertIn("ts", event)

    def test_report_image_event_swallows_callback_exception(self):
        driver = DockerDriver(on_image_event=lambda event: (_ for _ in ()).throw(RuntimeError("boom")))
        driver._report_image_event("ready", "amd64", "detail")  # must not raise

    @patch("subprocess.run")
    def test_build_runner_image_already_exists_reports_ready(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = self.driver._build_runner_image("amd64")
        self.assertTrue(result)
        self.assertEqual(self.events[-1]["status"], "ready")

    @patch.object(DockerDriver, "_resolve_build_context_dir", return_value=None)
    @patch("subprocess.run")
    def test_build_runner_image_missing_context_reports_failed(self, mock_run, mock_resolve):
        mock_run.return_value = MagicMock(returncode=1)  # _image_exists() -> False
        result = self.driver._build_runner_image("amd64")
        self.assertFalse(result)
        self.assertEqual(self.events[-1]["status"], "failed")
        self.assertIn("build context not found", self.events[-1]["detail"])

    @patch.object(DockerDriver, "_resolve_build_context_dir", return_value="/tmp/docker-ctx")
    @patch("subprocess.run")
    def test_build_runner_image_no_buildx_reports_failed(self, mock_run, mock_resolve):
        mock_run.side_effect = [
            MagicMock(returncode=1),  # _image_exists() -> False
            MagicMock(returncode=1),  # docker buildx version -> unavailable
        ]
        result = self.driver._build_runner_image("amd64")
        self.assertFalse(result)
        self.assertEqual(self.events[-1]["status"], "failed")
        self.assertIn("buildx", self.events[-1]["detail"])

    @patch.object(DockerDriver, "_resolve_build_context_dir", return_value="/tmp/docker-ctx")
    @patch("subprocess.run")
    def test_build_runner_image_success_reports_building_then_ready(self, mock_run, mock_resolve):
        mock_run.side_effect = [
            MagicMock(returncode=1),  # _image_exists() -> False
            MagicMock(returncode=0),  # docker buildx version -> available
            MagicMock(returncode=0),  # docker buildx build -> success
        ]
        result = self.driver._build_runner_image("amd64")
        self.assertTrue(result)
        statuses = [e["status"] for e in self.events]
        self.assertEqual(statuses, ["building", "ready"])

    @patch.object(DockerDriver, "_resolve_build_context_dir", return_value="/tmp/docker-ctx")
    @patch("subprocess.run")
    def test_build_runner_image_build_failure_reports_failed(self, mock_run, mock_resolve):
        error = subprocess.CalledProcessError(1, ["docker"], output=b"", stderr=b"boom")

        def _side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[:2] == ["docker", "image"]:
                return MagicMock(returncode=1)
            if cmd[:2] == ["docker", "buildx"] and "build" not in cmd:
                return MagicMock(returncode=0)
            raise error

        mock_run.side_effect = _side_effect
        result = self.driver._build_runner_image("amd64")
        self.assertFalse(result)
        self.assertEqual(self.events[-1]["status"], "failed")
        self.assertIn("boom", self.events[-1]["detail"])

    @patch("threading.Thread", _SyncThread)
    def test_build_runner_image_async_dedupes_when_already_building(self):
        self.driver._backoff.in_progress.add("amd64")
        with patch("subprocess.run") as mock_run:
            self.driver._build_runner_image_async("amd64")
            mock_run.assert_not_called()

    @patch("threading.Thread", _SyncThread)
    def test_build_runner_image_async_skips_during_cooldown(self):
        self.driver._backoff.retry_after["amd64"] = time.monotonic() + 100
        with patch("subprocess.run") as mock_run:
            self.driver._build_runner_image_async("amd64")
            mock_run.assert_not_called()

    @patch("threading.Thread", _SyncThread)
    @patch.object(DockerDriver, "_build_runner_image", return_value=True)
    def test_build_runner_image_async_success_resets_failure_state(self, mock_build):
        self.driver._backoff.failure_counts["amd64"] = 2
        self.driver._backoff.retry_after["amd64"] = time.monotonic() - 1  # cooldown already expired
        self.driver._build_runner_image_async("amd64")
        self.assertNotIn("amd64", self.driver._backoff.in_progress)
        self.assertEqual(self.driver._backoff.failure_counts["amd64"], 0)
        self.assertNotIn("amd64", self.driver._backoff.retry_after)

    @patch("threading.Thread", _SyncThread)
    @patch.object(DockerDriver, "_build_runner_image", return_value=False)
    def test_build_runner_image_async_failure_sets_cooldown_and_reports(self, mock_build):
        before = time.monotonic()
        self.driver._build_runner_image_async("amd64")
        self.assertNotIn("amd64", self.driver._backoff.in_progress)
        self.assertEqual(self.driver._backoff.failure_counts["amd64"], 1)
        self.assertIn("amd64", self.driver._backoff.retry_after)
        self.assertEqual(self.events[-1]["status"], "cooldown")
        # Mutation-prone: the previous assertion only checked key *presence*, not the
        # actual value -- a `+` -> `-` typo in the retry_after assignment would set the
        # cooldown deadline in the PAST (i.e. no cooldown at all) and still pass. The
        # deadline must be strictly in the future, ~30s out for the first failure.
        remaining = self.driver._backoff.retry_after["amd64"] - before
        self.assertGreater(remaining, 25)
        self.assertLess(remaining, 35)

    @patch("threading.Thread", _SyncThread)
    @patch.object(DockerDriver, "_build_runner_image", return_value=False)
    def test_build_runner_image_async_cooldown_backs_off_exponentially_and_caps_at_900(self, mock_build):
        # Mutation-prone: the exponential-backoff formula `30 * (2 ** (failures - 1))`
        # capped at 900s was completely unverified numerically -- multiplication could
        # silently become division, the exponent base/offset could drift, or the cap
        # could shift by one second, and no test would notice. This is the exact
        # backoff that governed the real 2026-09-22 outage's "8 failed attempts,
        # backing off 900s each time" retry pattern.
        expected_by_failure_count = {1: 30, 2: 60, 3: 120, 4: 240, 5: 480, 6: 900, 7: 900}
        for failures, expected_cooldown in expected_by_failure_count.items():
            self.driver._backoff.failure_counts["amd64"] = failures - 1
            self.driver._backoff.retry_after.pop("amd64", None)
            before = time.monotonic()
            self.driver._build_runner_image_async("amd64")
            actual_cooldown = self.driver._backoff.retry_after["amd64"] - before
            self.assertAlmostEqual(actual_cooldown, expected_cooldown, delta=2)

    @patch("subprocess.run")
    def test_ensure_runtime_assets_returns_true_when_image_exists(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.ensure_runtime_assets("amd64"))

    @patch("subprocess.run")
    def test_ensure_runtime_assets_returns_false_when_already_building(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)  # _image_exists() -> False
        self.driver._backoff.in_progress.add("amd64")
        self.assertFalse(self.driver.ensure_runtime_assets("amd64"))

    @patch("subprocess.run")
    def test_ensure_runtime_assets_returns_false_during_cooldown(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)  # _image_exists() -> False
        self.driver._backoff.retry_after["amd64"] = time.monotonic() + 100
        self.assertFalse(self.driver.ensure_runtime_assets("amd64"))

    @patch("threading.Thread", _SyncThread)
    @patch.object(DockerDriver, "_build_runner_image", return_value=True)
    @patch("subprocess.run")
    def test_ensure_runtime_assets_triggers_background_build_when_missing(self, mock_run, mock_build):
        mock_run.return_value = MagicMock(returncode=1)  # _image_exists() -> False
        result = self.driver.ensure_runtime_assets("amd64")
        self.assertFalse(result)
        mock_build.assert_called_once_with("amd64")


if __name__ == "__main__":
    unittest.main()
