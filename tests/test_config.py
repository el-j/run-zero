"""
Tests for validated configuration loading (#50).
"""

import os
import re
import subprocess
import sys
import unittest

from config import BACKENDS, Config, ConfigError, load_config

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestLoadConfig(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(load_config({}), Config())

    def test_parses_every_type(self):
        cfg = load_config(
            {
                "GITHUB_TOKEN": "gh",
                "OWNER": " el-j ",
                "REPO": "el-j/run-zero",
                "AUTO_DISCOVER_REPOS": "no",
                "RUNNER_BACKEND": "OrbStack-VM",
                "RUNNER_ARCH": "arm64",
                "MIN_RUNNERS": "1",
                "MAX_RUNNERS": "8",
                "POLL_INTERVAL": "5",
                "DASHBOARD_ENABLED": "off",
                "RUNNER_BUSY_TIMEOUT_SECONDS": "3600",
            }
        )
        self.assertEqual(cfg.access_token, "gh")
        self.assertEqual(cfg.owner, "el-j")
        self.assertEqual(cfg.repos_config, "el-j/run-zero")
        self.assertFalse(cfg.auto_discover)
        self.assertEqual(cfg.runner_backend, "orbstack-vm")
        self.assertEqual((cfg.min_runners, cfg.max_runners, cfg.poll_interval), (1, 8, 5))
        self.assertFalse(cfg.dashboard_enabled)
        self.assertEqual(cfg.busy_timeout_seconds, 3600)

    def test_access_token_prefers_access_token_and_blank_means_unset(self):
        self.assertEqual(load_config({"ACCESS_TOKEN": "a", "GITHUB_TOKEN": "g"}).access_token, "a")
        self.assertEqual(load_config({"ACCESS_TOKEN": "  ", "GITHUB_TOKEN": "g"}).access_token, "g")
        self.assertEqual(load_config({"MAX_RUNNERS": ""}).max_runners, 4)

    def test_errors_name_the_variable(self):
        cases = {
            "MAX_RUNNERS": ("four", "MAX_RUNNERS='four' is not an integer"),
            "POLL_INTERVAL": ("0", "POLL_INTERVAL=0 must be between 1 and 3600"),
            "MIN_RUNNERS": ("-1", "MIN_RUNNERS=-1 must be >= 0"),
            "DASHBOARD_PORT": ("70000", "DASHBOARD_PORT=70000 must be between 1 and 65535"),
            "CACHE_ENABLED": ("maybe", "CACHE_ENABLED='maybe' is not a boolean"),
            "RUNNER_ARCH": ("x86", "RUNNER_ARCH='x86' must be one of"),
            "RUNNER_BACKEND": ("kubernetes", "RUNNER_BACKEND='kubernetes' must be one of"),
        }
        for name, (value, message) in cases.items():
            with self.subTest(name=name), self.assertRaises(ConfigError) as cm:
                load_config({name: value})
            self.assertIn(message, str(cm.exception))

    def test_boolean_spellings(self):
        for raw in ("true", "1", "YES", "on"):
            self.assertTrue(load_config({"CACHE_ENABLED": raw}).cache_enabled, raw)
        for raw in ("false", "0", "No", "off"):
            self.assertFalse(load_config({"CACHE_ENABLED": raw}).cache_enabled, raw)

    def test_min_cannot_exceed_max(self):
        with self.assertRaisesRegex(ConfigError, "MIN_RUNNERS=5 cannot exceed MAX_RUNNERS=4"):
            load_config({"MIN_RUNNERS": "5"})

    def test_every_documented_backend_is_accepted_by_get_driver(self):
        with open(os.path.join(REPO_ROOT, "src", "drivers", "__init__.py"), encoding="utf-8") as fh:
            source = fh.read()
        for backend in BACKENDS:
            self.assertIn(f'"{backend}"', source, backend)


class TestConsistentDefaults(unittest.TestCase):
    """Defaults in .env.example and docker-compose.yml must match config.Config."""

    def _read(self, name: str) -> str:
        with open(os.path.join(REPO_ROOT, name), encoding="utf-8") as fh:
            return fh.read()

    def test_env_example_and_compose_match(self):
        env_example = self._read(".env.example")
        compose = self._read("docker-compose.yml")
        defaults = Config()
        for var, expected in (("POLL_INTERVAL", defaults.poll_interval), ("MAX_RUNNERS", defaults.max_runners), ("MIN_RUNNERS", defaults.min_runners)):
            with self.subTest(var=var):
                example = re.search(rf"^{var}=(\d+)", env_example, re.M)
                assert example is not None
                self.assertEqual(int(example.group(1)), expected)
                composed = re.search(rf"{var}=\$\{{{var}:-(\d+)\}}", compose)
                assert composed is not None
                self.assertEqual(int(composed.group(1)), expected)


class TestAutoscalerStartupOnBadConfig(unittest.TestCase):
    def test_bad_value_exits_with_named_variable(self):
        env = {**os.environ, "PYTHONPATH": os.path.join(REPO_ROOT, "src"), "MAX_RUNNERS": "four"}
        res = subprocess.run([sys.executable, "-c", "import autoscaler"], env=env, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Configuration error: MAX_RUNNERS='four' is not an integer", res.stderr)


class TestSingleVersionSource(unittest.TestCase):
    def test_no_hardcoded_version_literals(self):
        pattern = re.compile(r"\b0\.1\.0\b")
        offenders = []
        for root, _dirs, files in os.walk(os.path.join(REPO_ROOT, "src")):
            for name in files:
                if name.endswith((".py", ".js", ".html")):
                    path = os.path.join(root, name)
                    with open(path, encoding="utf-8") as fh:
                        if pattern.search(fh.read()):
                            offenders.append(os.path.relpath(path, REPO_ROOT))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
