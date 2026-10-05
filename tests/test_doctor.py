"""
Tests for doctor: host checks, the in-runner probe and the report, with mocked backends (#73).
"""

import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import doctor
from doctor import FAIL, OK, SKIP, WARN, Check
from drivers.sizing import HostCapacity, RunnerSizing

SIZING = RunnerSizing(3, 4096, "configured", HostCapacity(11, 16384), 3)

GOOD_PROBE = """
npm warn exec The following package was not found and will be installed: pnpm@11
RUNZERO=1
RUNNER_TOOL_CACHE=/opt/hostedtoolcache
TOOLCACHE_MOUNTED=1
PLAYWRIGHT_BROWSERS_PATH=/home/runner/.cache/ms-playwright
PLAYWRIGHT_MOUNTED=1
EXPECTED_REGISTRY=http://localhost:49501/
NPM_REGISTRY=http://localhost:49501/
YARN_REGISTRY=http://localhost:49501
PNPM10_REGISTRY=http://localhost:49501/
PNPM10_STORE=/home/runner/.local/share/pnpm/store
PNPM11_REGISTRY=http://localhost:49501/
PNPM11_STORE=/home/runner/.local/share/pnpm/store
REGISTRY_SECONDS=0.004
"""


def statuses(checks: list[Check]) -> dict[str, str]:
    return {c.name: c.status for c in checks}


class TestHostChecks(unittest.TestCase):
    def test_proxies(self):
        def get(url: str):
            if "49503" in url:
                return False, 0.0, b""
            return True, (2.0 if "49500" in url else 0.01), b""

        result = statuses(doctor.check_proxies(True, get=get))
        self.assertEqual(result["proxy apt-cacher-ng"], FAIL)
        self.assertEqual(result["proxy athens (Go)"], WARN)
        self.assertEqual(result["proxy verdaccio (npm/pnpm/yarn)"], OK)
        self.assertEqual(doctor.check_proxies(False), [Check("proxies", SKIP, "PROXIES_ENABLED=false")])

    def test_cache_dir(self):
        self.assertEqual(doctor.check_cache_dir("", False)[0].status, SKIP)
        self.assertEqual(doctor.check_cache_dir("/nonexistent/runzero", True)[0].status, FAIL)
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "npm"))
            with open(os.path.join(root, "npm", "pkg"), "wb") as fh:
                fh.write(b"x" * 4)
            os.symlink(os.path.join(root, "npm", "pkg"), os.path.join(root, "npm", "link"))
            checks = statuses(doctor.check_cache_dir(root, True))
            self.assertEqual(checks["host cache"], OK)
            self.assertEqual(checks["cache npm"], OK)
            self.assertEqual(checks["cache pnpm"], WARN)  # empty: never got a hit

    def test_dir_bytes_skips_vanished_files(self):
        with tempfile.TemporaryDirectory() as root:
            open(os.path.join(root, "a"), "wb").close()
            with patch("doctor.os.path.getsize", side_effect=OSError):
                self.assertEqual(doctor._dir_bytes(root), 0)

    def test_load(self):
        self.assertEqual(doctor.check_load(lambda: (12.0, 0, 0), cpus=10).status, WARN)
        self.assertEqual(doctor.check_load(lambda: (2.0, 0, 0), cpus=10).status, OK)
        self.assertEqual(doctor.check_load().name, "host load")

    def test_sizing(self):
        checks = doctor.check_sizing({"RUNNER_SIZING": "unlimited"}, "docker")
        self.assertEqual([c.status for c in checks], [OK, WARN])
        with patch("doctor.resolve_sizing") as resolve:
            doctor.check_sizing({}, "orbstack-vm")
        self.assertIs(resolve.call_args.args[1], doctor.orbstack_capacity)

    @patch("doctor.build_info", return_value={"version": "0.0.1", "git_sha": "abc123"})
    def test_versions(self, _info):
        bodies = {
            "http://b/health": (True, 0.0, json.dumps({"version": "0.0.1-beta.1", "git_sha": "fff000"}).encode()),
            "http://d/api/status": (True, 0.0, json.dumps({"version": "0.0.1", "git_sha": "abc123"}).encode()),
        }
        checks = doctor.check_versions("http://b", "http://d", get=lambda url: bodies[url])
        self.assertEqual([c.status for c in checks], [WARN, OK])
        self.assertIn("fff000", checks[0].detail)
        checks = doctor.check_versions("http://b", "http://d", get=lambda url: (url.endswith("status"), 0.0, b"not json"))
        self.assertEqual([c.status for c in checks], [WARN, WARN])
        self.assertIn("not reachable", checks[0].detail)
        self.assertIn("does not report", checks[1].detail)
        checks = doctor.check_versions("http://b", "http://d", get=lambda url: (True, 0.0, b"[1]"))
        self.assertIn("does not report", checks[0].detail)

    def test_http_get(self):
        ok, _, _ = doctor._http_get("http://127.0.0.1:9/")  # discard port: refused
        self.assertFalse(ok)
        err = MagicMock(fp=None)
        with patch("doctor.urllib.request.urlopen", side_effect=doctor.urllib.error.HTTPError("u", 404, "nf", {}, err.fp)):  # type: ignore[arg-type]
            self.assertEqual(doctor._http_get("http://127.0.0.1/")[::2], (True, b""))
        resp = MagicMock()
        resp.__enter__.return_value.read.return_value = b"pong"
        with patch("doctor.urllib.request.urlopen", return_value=resp):
            self.assertEqual(doctor._http_get("http://127.0.0.1/")[::2], (True, b"pong"))

    def test_http_get_reads_error_body(self):
        error = doctor.urllib.error.HTTPError("u", 500, "boom", {}, MagicMock(read=MagicMock(return_value=b"oops")))  # type: ignore[arg-type]
        with patch("doctor.urllib.request.urlopen", side_effect=error):
            self.assertEqual(doctor._http_get("http://127.0.0.1/")[2], b"oops")


class TestProbeEvaluation(unittest.TestCase):
    def test_parse_ignores_noise(self):
        values = doctor.parse_probe(GOOD_PROBE + "not a pair\nlower=ignored\n")
        self.assertEqual(values["PNPM11_STORE"], "/home/runner/.local/share/pnpm/store")
        self.assertNotIn("lower", values)

    def test_healthy_runner(self):
        checks = doctor.evaluate_probe("docker", doctor.parse_probe(GOOD_PROBE), caches_mounted=True, proxies_enabled=True)
        self.assertEqual({c.status for c in checks}, {OK}, doctor.render(checks))

    def test_env_not_applied(self):
        (check,) = doctor.evaluate_probe("docker", {}, True, True)
        self.assertEqual(check.status, FAIL)

    def test_pnpm11_ignoring_npm_config_is_caught(self):
        values = doctor.parse_probe(GOOD_PROBE)
        values.update(PNPM11_REGISTRY="https://registry.npmjs.org/", PNPM11_STORE="/home/runner/.local/share/pnpm/store/v10")
        result = statuses(doctor.evaluate_probe("orbstack-vm", values, True, True))
        self.assertEqual(result["orbstack-vm: pnpm 11 registry"], FAIL)
        self.assertEqual(result["orbstack-vm: pnpm 11 store"], FAIL)

    def test_missing_mounts_and_tools(self):
        values = doctor.parse_probe(GOOD_PROBE)
        values.update(TOOLCACHE_MOUNTED="0", PLAYWRIGHT_MOUNTED="0", YARN_REGISTRY="", PNPM10_STORE="", REGISTRY_SECONDS="")
        result = statuses(doctor.evaluate_probe("docker", values, True, True))
        self.assertEqual(result["docker: tool cache mounted"], FAIL)
        self.assertEqual(result["docker: Playwright browsers"], FAIL)
        self.assertEqual(result["docker: yarn registry"], WARN)
        self.assertEqual(result["docker: registry reachable"], FAIL)
        self.assertNotIn("docker: pnpm 10 store", result)

    def test_without_caches_or_proxies(self):
        values = {"RUNZERO": "1", "RUNNER_TOOL_CACHE": ""}
        result = statuses(doctor.evaluate_probe("docker", values, caches_mounted=False, proxies_enabled=False))
        self.assertEqual(result, {"docker: runner env": OK, "docker: RUNNER_TOOL_CACHE": FAIL, "docker: registry": SKIP})

    def test_cgroup_limits_match_the_sizing(self):
        values = {"RUNZERO": "1", "CPU_MAX": "300000 100000", "MEMORY_MAX": "4294967296"}
        result = statuses(doctor.evaluate_probe("orbstack-vm", values, False, False, SIZING))
        self.assertEqual((result["orbstack-vm: CPU limit"], result["orbstack-vm: memory limit"]), (OK, OK))

    def test_cgroup_limits_missing_or_wrong(self):
        values = {"RUNZERO": "1", "CPU_MAX": "max 100000", "MEMORY_MAX": "max"}
        checks = {c.name: c for c in doctor.evaluate_probe("docker", values, False, False, SIZING)}
        self.assertEqual(checks["docker: CPU limit"].status, FAIL)
        self.assertEqual(checks["docker: memory limit"].detail, "unlimited (expected 4096 MiB)")
        values.update(CPU_MAX="200000 100000", MEMORY_MAX="2147483648")
        checks = {c.name: c for c in doctor.evaluate_probe("docker", values, False, False, SIZING)}
        self.assertEqual(checks["docker: CPU limit"].detail, "2 CPUs (expected 3)")
        self.assertEqual(checks["docker: memory limit"].status, FAIL)

    def test_cgroup_limits_unreadable_or_not_configured(self):
        result = statuses(doctor.evaluate_probe("docker", {"RUNZERO": "1"}, False, False, SIZING))
        self.assertEqual(result["docker: resource limits"], WARN)
        unlimited = RunnerSizing(None, None, "unlimited", HostCapacity(11, 16384), 3)
        for sizing in (None, unlimited):
            result = statuses(doctor.evaluate_probe("docker", {"RUNZERO": "1"}, False, False, sizing))
            self.assertNotIn("docker: resource limits", result)
            self.assertNotIn("docker: CPU limit", result)

    def test_registry_not_exported(self):
        result = statuses(doctor.evaluate_probe("docker", {"RUNZERO": "1"}, False, True))
        self.assertEqual(result["docker: registry"], FAIL)


class TestProbes(unittest.TestCase):
    @patch("doctor.subprocess.run")
    @patch("drivers.docker_driver.DockerDriver.is_available", return_value=True)
    @patch("drivers.docker_driver.DockerDriver._image_exists", return_value=True)
    def test_docker_probe_mirrors_a_jobs_env_and_mounts(self, _exists, _avail, run):
        run.return_value = MagicMock(stdout=GOOD_PROBE)
        self.assertEqual(doctor.probe_docker("x86_64", {"/h/npm": "/home/runner/.npm"}, True), GOOD_PROBE)
        cmd = run.call_args.args[0]
        self.assertEqual(cmd[:5], ["docker", "run", "--rm", "--platform", "linux/amd64"])
        self.assertIn("RUNZERO=1", cmd)
        self.assertIn("/h/npm:/home/runner/.npm", cmd)
        self.assertTrue(any(a.startswith("pnpm_config_registry=") for a in cmd))
        self.assertEqual(cmd[-2:], ["-lc", doctor.PROBE_SCRIPT])

    @patch("doctor.subprocess.run")
    @patch("drivers.docker_driver.DockerDriver.is_available", return_value=True)
    @patch("drivers.docker_driver.DockerDriver._image_exists", return_value=True)
    def test_docker_probe_applies_the_runner_sizing(self, _exists, _avail, run):
        run.return_value = MagicMock(stdout=GOOD_PROBE)
        with patch.dict(os.environ, {"RUNNER_SIZING": "auto", "RUNNER_CPUS": "2", "RUNNER_MEMORY": "2G", "MAX_RUNNERS": "1"}):
            doctor.probe_docker("arm64", {}, False)
        cmd = run.call_args.args[0]
        self.assertEqual(cmd[cmd.index("--cpus") + 1], "2")
        self.assertEqual(cmd[cmd.index("--memory") + 1], "2048M")

    @patch("doctor.subprocess.run", side_effect=subprocess.TimeoutExpired("docker", 1))
    @patch("drivers.docker_driver.DockerDriver.is_available", return_value=True)
    @patch("drivers.docker_driver.DockerDriver._image_exists", return_value=True)
    def test_docker_probe_timeout(self, _exists, _avail, _run):
        self.assertIsNone(doctor.probe_docker("arm64", {}, False))

    @patch("drivers.docker_driver.DockerDriver.is_available", return_value=False)
    def test_docker_probe_unavailable(self, _avail):
        self.assertIsNone(doctor.probe_docker("arm64", {}, True))

    @patch("doctor.subprocess.run")
    @patch("drivers.orbstack_vm_driver.OrbStackVMDriver.is_available", return_value=True)
    @patch("drivers.orbstack_vm_driver.OrbStackVMDriver.base_image_exists", return_value=True)
    def test_orbstack_probe_clones_probes_and_always_deletes(self, _exists, _avail, run):
        run.side_effect = [MagicMock(), MagicMock(stdout=GOOD_PROBE), MagicMock()]
        self.assertEqual(doctor.probe_orbstack("arm64", {"/h/npm": "/home/runner/.npm"}, True), GOOD_PROBE)
        clone, probe, delete = (c.args[0] for c in run.call_args_list)
        self.assertEqual(clone[:3], ["orbctl", "clone", "runzero-vm-base-arm64"])
        self.assertEqual(probe[:5], ["orb", "-m", clone[3], "-u", "runner"])
        self.assertIn("host.orb.internal:49501", probe[-1])
        self.assertIn("mount --bind", probe[-1])
        self.assertIn("export RUNZERO=1", probe[-1])
        self.assertEqual(delete, ["orbctl", "delete", "-f", clone[3]])

    @patch("doctor.subprocess.run")
    @patch("drivers.orbstack_vm_driver.OrbStackVMDriver.is_available", return_value=True)
    @patch("drivers.orbstack_vm_driver.OrbStackVMDriver.base_image_exists", return_value=True)
    def test_orbstack_probe_clone_failure_still_cleans_up(self, _exists, _avail, run):
        run.side_effect = [subprocess.CalledProcessError(1, "orbctl"), MagicMock()]
        self.assertIsNone(doctor.probe_orbstack("arm64", {}, False))
        self.assertEqual(run.call_args.args[0][:3], ["orbctl", "delete", "-f"])

    @patch("drivers.orbstack_vm_driver.OrbStackVMDriver.is_available", return_value=False)
    def test_orbstack_probe_unavailable(self, _avail):
        self.assertIsNone(doctor.probe_orbstack("arm64", {}, True))

    def test_check_runner(self):
        self.assertEqual(doctor.check_runner("multipass", "arm64", "", False, True)[0].status, SKIP)
        with patch.dict(doctor.PROBES, {"docker": lambda arch, mounts, proxies: None}):
            self.assertEqual(doctor.check_runner("docker", "arm64", "", False, True)[0].status, SKIP)
        with tempfile.TemporaryDirectory() as cache, patch.dict(doctor.PROBES, {"docker": lambda arch, mounts, proxies: GOOD_PROBE}):
            checks = doctor.check_runner("docker", "arm64", cache, True, True)
        self.assertEqual({c.status for c in checks}, {OK})


class TestReportAndMain(unittest.TestCase):
    def test_render(self):
        self.assertEqual(doctor.render([Check("a", OK, "fine"), Check("b", FAIL)]), "✅ a: fine\n❌ b")

    def test_truthy(self):
        self.assertTrue(doctor._truthy(None, True))
        self.assertTrue(doctor._truthy(" ", True))
        self.assertFalse(doctor._truthy("off", True))
        self.assertTrue(doctor._truthy("YES", False))

    def test_parse_args_defaults(self):
        args = doctor.parse_args([])
        self.assertEqual(args.backend, ["docker", "orbstack-vm"])
        self.assertFalse(args.no_spawn)
        self.assertEqual(doctor.parse_args(["--backend", "docker", "--arch", "amd64"]).backend, ["docker"])

    def _main(self, argv: list[str], env: dict[str, str], probe_output: str | None = GOOD_PROBE) -> tuple[int, str]:
        healthy = (True, 0.001, json.dumps({"version": "x"}).encode())
        with (
            patch("doctor._http_get", return_value=healthy),
            patch.dict(doctor.PROBES, {"docker": lambda a, m, p: probe_output, "orbstack-vm": lambda a, m, p: probe_output}),
            patch("doctor.check_load", return_value=Check("host load", OK)),
            patch("builtins.print") as out,
        ):
            code = doctor.main(argv, env=env)
        return code, "\n".join(str(c.args[0]) for c in out.call_args_list)

    def test_main_passes_on_healthy_setup(self):
        with tempfile.TemporaryDirectory() as cache:
            code, report = self._main(["--backend", "docker"], {"HOST_CACHE_DIR": cache, "RUNNER_CPUS": "1", "MAX_RUNNERS": "1"})
        self.assertEqual(code, 0, report)
        self.assertIn("0 failed", report)

    def test_main_fails_on_broken_runner(self):
        with tempfile.TemporaryDirectory() as cache:
            code, report = self._main([], {"HOST_CACHE_DIR": cache, "RUNNER_SIZING": "unlimited"}, probe_output="RUNZERO=\n")
        self.assertEqual(code, 1)
        self.assertIn("orbstack-vm: runner env", report)

    def test_main_no_spawn_skips_runner_probes(self):
        code, report = self._main(["--no-spawn"], {"CACHE_ENABLED": "false", "PROXIES_ENABLED": "false", "RUNNER_SIZING": "unlimited"}, probe_output=None)
        self.assertEqual(code, 0, report)
        self.assertNotIn("runner probe", report)

    def test_main_reads_os_environ_by_default(self):
        with patch.dict(os.environ, {"CACHE_ENABLED": "false", "PROXIES_ENABLED": "false"}):
            code, _ = self._main(["--no-spawn"], env=None)  # type: ignore[arg-type]
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
