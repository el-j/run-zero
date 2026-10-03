"""
Tests for drivers.runner_env: the cache/registry environment every runner exports (#66-#69).
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest

from cache_manager import init_cache_dirs
from drivers.runner_env import (
    MOUNTED_CACHES,
    PLAYWRIGHT_BROWSERS,
    PNPM_STORE,
    TOOL_CACHE,
    cache_env,
    docker_env_args,
    export_block,
    registry_env,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestCacheEnv(unittest.TestCase):
    def test_tool_cache_and_marker_always_set(self):
        self.assertEqual(
            cache_env(caches_mounted=False),
            {"RUNZERO": "1", "RUNNER_TOOL_CACHE": TOOL_CACHE, "AGENT_TOOLSDIRECTORY": TOOL_CACHE},
        )

    def test_mounted_caches_point_pnpm_and_playwright_at_mounts(self):
        env = cache_env(caches_mounted=True)
        self.assertEqual(env["pnpm_config_store_dir"], PNPM_STORE)
        self.assertEqual(env["npm_config_store_dir"], PNPM_STORE)
        self.assertEqual(env["PLAYWRIGHT_BROWSERS_PATH"], PLAYWRIGHT_BROWSERS)
        self.assertEqual(env["RUNZERO_CACHES"], ",".join(MOUNTED_CACHES))
        self.assertEqual(env["RUNNER_TOOL_CACHE"], TOOL_CACHE)

    def test_rehomes_runner_paths_for_other_guest_users(self):
        env = cache_env(caches_mounted=True, home="/home/ubuntu")
        self.assertEqual(env["pnpm_config_store_dir"], "/home/ubuntu/.local/share/pnpm/store")
        self.assertEqual(env["PLAYWRIGHT_BROWSERS_PATH"], "/home/ubuntu/.cache/ms-playwright")
        self.assertEqual(env["RUNNER_TOOL_CACHE"], TOOL_CACHE)

    def test_env_paths_match_cache_manager_mount_destinations(self):
        with tempfile.TemporaryDirectory() as tmp:
            dests = set(init_cache_dirs(tmp, "arm64").values())
            self.assertTrue(os.path.isdir(os.path.join(tmp, "ms-playwright", "arm64")))
        self.assertTrue({TOOL_CACHE, PNPM_STORE, PLAYWRIGHT_BROWSERS} <= dests)


class TestRegistryEnv(unittest.TestCase):
    def test_sets_every_package_manager_spelling(self):
        env = registry_env("http://reg/")
        self.assertEqual(
            set(env),
            {"npm_config_registry", "NPM_CONFIG_REGISTRY", "pnpm_config_registry", "YARN_REGISTRY", "YARN_NPM_REGISTRY_SERVER"},
        )
        self.assertEqual(set(env.values()), {"http://reg/"})

    def test_start_sh_exports_the_same_registry_variables(self):
        with open(os.path.join(REPO_ROOT, "docker", "start.sh"), encoding="utf-8") as fh:
            body = re.search(r"use_npm_registry\(\) \{(.*?)\n\}", fh.read(), re.DOTALL)
        assert body is not None
        exported = set(re.findall(r"\b([A-Za-z_]+)=\"\$1\"", body.group(1)))
        self.assertEqual(exported, set(registry_env("x")))


class TestRendering(unittest.TestCase):
    def test_export_block_quotes_values(self):
        self.assertEqual(export_block({"A": "x y", "B": "z"}), "export A='x y'\nexport B=z")
        self.assertEqual(export_block({}), "")

    def test_export_block_expand_keeps_shell_references(self):
        self.assertEqual(export_block({"R": "http://${HOST_IP}/"}, expand=True), 'export R="http://${HOST_IP}/"')

    def test_docker_env_args(self):
        self.assertEqual(docker_env_args({"A": "1", "B": "2"}), ["-e", "A=1", "-e", "B=2"])


def _pnpm_binaries() -> list[str]:
    """pnpm binaries to check: $RUNZERO_TEST_PNPM_BINS (os.pathsep-separated), else `pnpm` on PATH."""
    configured = [p for p in os.getenv("RUNZERO_TEST_PNPM_BINS", "").split(os.pathsep) if p]
    if configured:
        return configured
    found = shutil.which("pnpm")
    return [found] if found else []


@unittest.skipUnless(_pnpm_binaries(), "no pnpm binary (set RUNZERO_TEST_PNPM_BINS to check pnpm 10 and 11)")
class TestRealPnpmResolution(unittest.TestCase):
    """The env must actually steer real pnpm: 11 reads only pnpm_config_*, <=10 only npm_config_*."""

    def _config_get(self, pnpm: str, key: str, env: dict[str, str]) -> str:
        with tempfile.TemporaryDirectory() as home:
            clean = {k: v for k, v in os.environ.items() if not k.lower().startswith(("npm_config_", "pnpm_config_")) and k != "NODE_OPTIONS"}
            clean.update(env, HOME=home, XDG_CONFIG_HOME=home)
            res = subprocess.run([pnpm, "config", "get", key], cwd=home, env=clean, capture_output=True, text=True, timeout=60, check=True)
        return res.stdout.strip()

    def test_registry_and_store_dir_resolve(self):
        env = {**registry_env("http://verdaccio.invalid:49501/"), **cache_env(caches_mounted=True)}
        for pnpm in _pnpm_binaries():
            with self.subTest(pnpm=pnpm):
                self.assertEqual(self._config_get(pnpm, "registry", env), "http://verdaccio.invalid:49501/")
                self.assertEqual(self._config_get(pnpm, "store-dir", env), PNPM_STORE)


if __name__ == "__main__":
    unittest.main()
