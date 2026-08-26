"""
Unit tests for Docker container runner driver.
"""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from drivers import RunnerInfo
from drivers.docker_driver import DockerDriver


class TestDockerDriver(unittest.TestCase):
    def setUp(self):
        self.driver = DockerDriver()

    def test_name(self):
        self.assertEqual(self.driver.name(), "docker")

    @patch("shutil.which", return_value="/usr/local/bin/docker")
    @patch("subprocess.run")
    def test_is_available(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.driver.is_available())

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
            stdout="runner1|Up 2 hours|local-runner-arm64-el-j-run-zero-123|running|el-j/run-zero|arm64|docker\nrunner2|Exited (0)|local-runner-amd64-my-org-456|exited|my-org|amd64|docker\n",
            returncode=0
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
            stdout="runner1|Up 2 hours|local-runner-arm64-1|running|el-j/run-zero|arm64|docker|2026-08-25 14:38:53 +0200 CEST\n",
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertIsNotNone(runners[0].created_at)

    def test_parse_created_at_invalid_returns_none(self):
        self.assertIsNone(self.driver._parse_created_at("not a timestamp"))

    @patch("subprocess.run")
    def test_list_runners_created_and_restarting_are_pending(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="r1|Created|c1|created|el-j/run-zero|arm64|docker\nr2|Restarting|c2|restarting|el-j/run-zero|arm64|docker\n",
            returncode=0
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
            repo="el-j/run-zero",
            arch="arm64",
            access_token="secret-pat",
            cache_mounts={"/host/cache": "/home/runner/.cache"},
            proxies_enabled=True
        )
        self.assertIn("local-runner-arm64-el-j-run-zero-", name_arm)

        # Spawn for Org
        name_amd = self.driver.spawn_runner(
            org="my-org",
            arch="amd64",
            access_token="secret-pat",
            proxies_enabled=False
        )
        self.assertIn("local-runner-amd64-my-org-", name_amd)

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
        dests = dest_entries[0][len("CACHE_MOUNT_DESTS="):].split(":")
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
    def test_cleanup_all_stops_and_removes_docker_backed_runners(self, mock_run):
        # Regression guard: cleanup_all() must only stop+remove runners whose
        # backend is actually "docker" -- list_runners() itself is real here
        # (only subprocess.run is mocked), so this exercises the real
        # filtering loop in cleanup_all() rather than relying on
        # list_runners() failing closed to an empty list.
        mock_run.return_value = MagicMock(
            stdout="c1|Up|local-runner-arm64-1|running|el-j/run-zero|arm64|docker\n",
            returncode=0
        )
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
            returncode=0
        )
        runners = self.driver.list_runners()
        self.assertEqual(len(runners), 2)


if __name__ == "__main__":
    unittest.main()
