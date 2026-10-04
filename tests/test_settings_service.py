"""Unit tests for dashboard settings_service module."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

from config import Config, ConfigError
from dashboard.settings_service import (
    _update_env_file,
    get_live_settings,
    update_live_settings,
)


class TestSettingsService(unittest.TestCase):
    """Test suite for settings inspection, validation, and hot-reloading."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = os.path.join(self.temp_dir, ".env")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_get_live_settings(self):
        cfg = Config(access_token="fake-token", max_runners=5, poll_interval=15)
        settings = get_live_settings(cfg)
        self.assertTrue(settings["access_token_configured"])
        self.assertEqual(settings["max_runners"], 5)
        self.assertEqual(settings["poll_interval"], 15)

    def test_update_live_settings_success(self):
        cfg = Config(access_token=None, max_runners=2, min_runners=0)
        body = {
            "max_runners": 6,
            "min_runners": 1,
            "poll_interval": 20,
            "discovery_interval": 300,
            "runner_backend": "docker",
            "runner_arch": "arm64",
            "native_arch_override": "off",
            "access_token": "new-token",
            "auto_route_vm": True,
            "cache_enabled": False,
            "proxies_enabled": False,
            "host_cache_dir": "/tmp/cache",
        }
        updated, live = update_live_settings(body, cfg, env_path=self.env_file)
        self.assertEqual(updated.max_runners, 6)
        self.assertEqual(updated.min_runners, 1)
        self.assertEqual(updated.poll_interval, 20)
        self.assertEqual(updated.discovery_interval, 300)
        self.assertEqual(updated.runner_backend, "docker")
        self.assertEqual(updated.runner_arch, "arm64")
        self.assertEqual(updated.access_token, "new-token")
        self.assertTrue(live["access_token_configured"])

        self.assertTrue(os.path.exists(self.env_file))
        with open(self.env_file) as f:
            content = f.read()
        self.assertIn("MAX_RUNNERS=6", content)
        self.assertIn("ACCESS_TOKEN=new-token", content)

    def test_update_live_settings_validations(self):
        cfg = Config(max_runners=4, min_runners=1)

        with self.assertRaises(ConfigError):
            update_live_settings({"max_runners": 0}, cfg)

        with self.assertRaises(ConfigError):
            update_live_settings({"min_runners": -1}, cfg)

        with self.assertRaises(ConfigError):
            update_live_settings({"min_runners": 5, "max_runners": 3}, cfg)

        with self.assertRaises(ConfigError):
            update_live_settings({"poll_interval": 0}, cfg)

        with self.assertRaises(ConfigError):
            update_live_settings({"discovery_interval": 10}, cfg)

        with self.assertRaises(ConfigError):
            update_live_settings({"runner_backend": "invalid-backend"}, cfg)

        with self.assertRaises(ConfigError):
            update_live_settings({"runner_arch": "invalid-arch"}, cfg)

        with self.assertRaises(ConfigError):
            update_live_settings({"native_arch_override": "invalid/syntax///"}, cfg)

    def test_update_env_file_replaces_existing_keys(self):
        with open(self.env_file, "w") as f:
            f.write("# existing env\nMAX_RUNNERS=2\nOTHER=test\n")

        _update_env_file(self.env_file, {"MAX_RUNNERS": "8", "NEW_VAR": "val"})

        with open(self.env_file) as f:
            content = f.read()
        self.assertIn("MAX_RUNNERS=8\n", content)
        self.assertIn("OTHER=test\n", content)
        self.assertIn("NEW_VAR=val\n", content)


if __name__ == "__main__":
    unittest.main()
