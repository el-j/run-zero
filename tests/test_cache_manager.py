"""
Unit tests for host cache directory manager.
"""

import os
import shutil
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
