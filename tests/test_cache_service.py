"""Unit tests for dashboard cache_service module."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from dashboard.cache_service import (
    _format_size,
    _get_path_size,
    get_cache_stats,
    purge_cache,
)


class TestCacheService(unittest.TestCase):
    """Test suite for cache inspection and purging functions."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_format_size_units(self):
        self.assertEqual(_format_size(0), "0 B")
        self.assertEqual(_format_size(100), "100 B")
        self.assertEqual(_format_size(1024), "1.0 KB")
        self.assertEqual(_format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(_format_size(1024 * 1024 * 1024), "1.0 GB")
        self.assertEqual(_format_size(1024 * 1024 * 1024 * 1024), "1.0 TB")
        self.assertEqual(_format_size(1024 * 1024 * 1024 * 1024 * 1024), "1024.0 TB")

    def test_get_path_size(self):
        self.assertEqual(_get_path_size(os.path.join(self.temp_dir, "nonexistent")), 0)

        file_path = os.path.join(self.temp_dir, "test.txt")
        with open(file_path, "wb") as f:
            f.write(b"12345")
        self.assertEqual(_get_path_size(file_path), 5)

        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        with open(os.path.join(sub_dir, "nested.txt"), "wb") as f:
            f.write(b"1234567")
        self.assertEqual(_get_path_size(self.temp_dir), 12)

    def test_get_cache_stats_empty_or_nonexistent(self):
        stats_nonexistent = get_cache_stats(os.path.join(self.temp_dir, "does_not_exist"))
        self.assertEqual(stats_nonexistent["total_bytes"], 0)
        self.assertEqual(stats_nonexistent["total_human"], "0 B")
        self.assertGreater(len(stats_nonexistent["categories"]), 0)

        stats_empty = get_cache_stats(self.temp_dir)
        self.assertEqual(stats_empty["total_bytes"], 0)

    def test_get_cache_stats_populated(self):
        pnpm_dir = os.path.join(self.temp_dir, "pnpm")
        os.makedirs(pnpm_dir)
        with open(os.path.join(pnpm_dir, "pkg.tar"), "wb") as f:
            f.write(b"x" * 2048)

        stats = get_cache_stats(self.temp_dir)
        self.assertGreaterEqual(stats["total_bytes"], 2048)
        pnpm_cat = next(c for c in stats["categories"] if c["category"] == "pnpm")
        self.assertEqual(pnpm_cat["bytes"], 2048)
        self.assertEqual(pnpm_cat["human_readable"], "2.0 KB")

    def test_purge_cache_category(self):
        pnpm_dir = os.path.join(self.temp_dir, "pnpm")
        os.makedirs(pnpm_dir)
        with open(os.path.join(pnpm_dir, "pkg.tar"), "wb") as f:
            f.write(b"content")

        res = purge_cache(self.temp_dir, category="pnpm")
        self.assertIn("pnpm", res["cleared"])
        self.assertFalse(os.path.exists(os.path.join(pnpm_dir, "pkg.tar")))

    def test_purge_cache_all(self):
        pnpm_dir = os.path.join(self.temp_dir, "pnpm")
        npm_dir = os.path.join(self.temp_dir, "npm")
        os.makedirs(pnpm_dir)
        os.makedirs(npm_dir)

        res = purge_cache(self.temp_dir, all_caches=True)
        self.assertIn("pnpm", res["cleared"])
        self.assertIn("npm", res["cleared"])

    def test_purge_cache_invalid_root_or_nonexistent_category(self):
        res = purge_cache(os.path.join(self.temp_dir, "nonexistent"))
        self.assertEqual(res["cleared"], [])

    def test_get_path_size_oserror(self):
        with patch("os.scandir", side_effect=OSError("permission denied")):
            self.assertEqual(_get_path_size(self.temp_dir), 0)

        entry_mock = MagicMock()
        entry_mock.is_file.side_effect = OSError("stat error")
        with patch("os.scandir", return_value=[entry_mock]):
            self.assertEqual(_get_path_size(self.temp_dir), 0)


if __name__ == "__main__":
    unittest.main()
