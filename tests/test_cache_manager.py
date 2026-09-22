"""
Unit tests for host cache directory manager.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from cache_manager import clean_build_cache, init_cache_dirs


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
        self.assertEqual(mounts[os.path.join(self.temp_dir, "go-build")], "/home/runner/.cache/go-build")

    def test_init_cache_dirs_with_scope_isolates_go_build(self):
        mounts_1 = init_cache_dirs(self.temp_dir, "arm64", cache_enabled=True, scope="el-j/herbful_1001_jobA")
        mounts_2 = init_cache_dirs(self.temp_dir, "arm64", cache_enabled=True, scope="el-j/herbful_1002_jobB")

        # Package download caches remain shared
        self.assertIn(os.path.join(self.temp_dir, "npm"), mounts_1)
        self.assertIn(os.path.join(self.temp_dir, "npm"), mounts_2)

        # Build caches are completely isolated under build-cache/<scope>/go-build
        go_build_1 = [k for k, v in mounts_1.items() if v == "/home/runner/.cache/go-build"][0]
        go_build_2 = [k for k, v in mounts_2.items() if v == "/home/runner/.cache/go-build"][0]
        self.assertNotEqual(go_build_1, go_build_2)
        self.assertIn("el-j_herbful_1001_jobA", go_build_1)
        self.assertIn("el-j_herbful_1002_jobB", go_build_2)
        self.assertTrue(os.path.isdir(go_build_1))
        self.assertTrue(os.path.isdir(go_build_2))

    def test_clean_build_cache(self):
        mounts = init_cache_dirs(self.temp_dir, "arm64", cache_enabled=True, scope="test-scope")
        go_build_dir = [k for k, v in mounts.items() if v == "/home/runner/.cache/go-build"][0]

        # Write dummy files and directories inside go-build
        sub_dir = os.path.join(go_build_dir, "0a")
        os.makedirs(sub_dir, exist_ok=True)
        dummy_file = os.path.join(sub_dir, "dummy.txt")
        with open(dummy_file, "w") as f:
            f.write("hello")

        self.assertTrue(os.path.exists(dummy_file))

        # Clean build cache
        clean_build_cache(self.temp_dir, scope="test-scope")
        self.assertTrue(os.path.isdir(go_build_dir))
        self.assertEqual(os.listdir(go_build_dir), [])

    def test_clean_build_cache_noop_when_no_host_cache_dir(self):
        # Must not raise -- and must not try to derive a path from an empty string.
        clean_build_cache("")

    def test_clean_build_cache_uses_flat_dir_when_no_scope(self):
        clean_build_cache(self.temp_dir)
        self.assertTrue(os.path.isdir(os.path.join(self.temp_dir, "go-build")))

    def test_clean_build_cache_removes_files_and_subdirs(self):
        target_dir = os.path.join(self.temp_dir, "build-cache", "test-scope", "go-build")
        os.makedirs(os.path.join(target_dir, "0a"), exist_ok=True)
        with open(os.path.join(target_dir, "0a", "entry.o"), "w") as f:
            f.write("data")
        with open(os.path.join(target_dir, "loose-file.txt"), "w") as f:
            f.write("data")

        clean_build_cache(self.temp_dir, scope="test-scope")

        self.assertTrue(os.path.isdir(target_dir))
        self.assertEqual(os.listdir(target_dir), [])

    def test_clean_build_cache_tolerates_remove_failure(self):
        target_dir = os.path.join(self.temp_dir, "build-cache", "test-scope", "go-build")
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, "locked.txt"), "w") as f:
            f.write("data")

        with patch("os.remove", side_effect=OSError("busy")):
            clean_build_cache(self.temp_dir, scope="test-scope")  # must not raise

        self.assertTrue(os.path.isdir(target_dir))

    def test_clean_build_cache_tolerates_listdir_failure(self):
        target_dir = os.path.join(self.temp_dir, "build-cache", "test-scope", "go-build")
        os.makedirs(target_dir, exist_ok=True)

        with patch("os.listdir", side_effect=OSError("permission denied")):
            clean_build_cache(self.temp_dir, scope="test-scope")  # must not raise

        self.assertTrue(os.path.isdir(target_dir))

    def test_clean_build_cache_tolerates_chmod_failure(self):
        with patch("os.chmod", side_effect=OSError("not permitted")):
            clean_build_cache(self.temp_dir, scope="test-scope")  # must not raise

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
