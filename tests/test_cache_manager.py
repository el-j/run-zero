"""
Unit tests for host cache directory manager.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from cache_manager import init_cache_dirs


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_cache_dirs_creates_structure(self):
        mounts = init_cache_dirs(self.temp_dir, "arm64", cache_enabled=True)
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "npm")))
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "hostedtoolcache", "arm64")))
        self.assertIn(os.path.join(self.temp_dir, "npm"), mounts)
        self.assertEqual(mounts[os.path.join(self.temp_dir, "npm")], "/home/runner/.npm")

    def test_init_cache_dirs_disabled(self):
        mounts = init_cache_dirs(self.temp_dir, "arm64", cache_enabled=False)
        self.assertEqual(mounts, {})

    @patch("os.chmod", side_effect=OSError("Operation not permitted"))
    def test_init_cache_dirs_tolerates_chmod_failure(self, mock_chmod):
        # Regression guard: a host filesystem that rejects chmod (e.g. a
        # mounted volume with restrictive permissions) must not blow up
        # directory initialization -- the directories still get created,
        # and the mount mapping is still returned.
        mounts = init_cache_dirs(self.temp_dir, "arm64", cache_enabled=True)
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "npm")))
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "hostedtoolcache", "arm64")))
        self.assertIn(os.path.join(self.temp_dir, "npm"), mounts)
        self.assertTrue(mock_chmod.called)


if __name__ == "__main__":
    unittest.main()
