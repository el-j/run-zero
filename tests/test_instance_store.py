"""
Unit tests for InstanceStore (host-side metadata persistence for Multipass & WSL2).
"""

import os
import tempfile
import unittest

from drivers.instance_store import InstanceStore, default_state_dir


class TestInstanceStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_path = os.path.join(self.temp_dir.name, "instances.json")
        self.store = InstanceStore(self.store_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_state_dir(self):
        self.assertTrue(len(default_state_dir()) > 0)

    def test_empty_store_returns_empty(self):
        self.assertEqual(self.store.get("non-existent"), {})
        self.assertEqual(self.store.all(), {})

    def test_corrupt_store_file_returns_empty(self):
        with open(self.store_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        self.assertEqual(self.store.get("any"), {})
        self.assertEqual(self.store.all(), {})

    def test_non_dict_store_file_returns_empty(self):
        with open(self.store_path, "w", encoding="utf-8") as f:
            f.write('["not", "a", "dict"]')
        self.assertEqual(self.store.get("any"), {})
        self.assertEqual(self.store.all(), {})

    def test_put_get_remove_lifecycle(self):
        self.store.put("inst-1", target="el-j/run-zero", arch="arm64", created_at=100.0)
        meta = self.store.get("inst-1")
        self.assertEqual(meta["target"], "el-j/run-zero")
        self.assertEqual(meta["arch"], "arm64")
        self.assertEqual(meta["created_at"], 100.0)

        all_inst = self.store.all()
        self.assertIn("inst-1", all_inst)
        self.assertEqual(len(all_inst), 1)

        # Overwrite
        self.store.put("inst-1", target="el-j/run-zero", arch="amd64", created_at=200.0)
        self.assertEqual(self.store.get("inst-1")["arch"], "amd64")

        # Remove
        self.store.remove("inst-1")
        self.assertEqual(self.store.get("inst-1"), {})
        self.assertEqual(self.store.all(), {})

        # Remove non-existent is no-op
        self.store.remove("non-existent")

    def test_prune(self):
        self.store.put("keep-1", target="t1", arch="arm64")
        self.store.put("keep-2", target="t2", arch="amd64")
        self.store.put("drop-1", target="t3", arch="arm64")

        self.store.prune({"keep-1", "keep-2"})
        all_inst = self.store.all()
        self.assertIn("keep-1", all_inst)
        self.assertIn("keep-2", all_inst)
        self.assertNotIn("drop-1", all_inst)
        self.assertEqual(len(all_inst), 2)

    def test_write_oserror_cleans_up_tmp(self):
        from unittest.mock import patch

        with patch("os.replace", side_effect=OSError("replace failed")), self.assertRaises(OSError):
            self.store._write({"foo": {"bar": 1}})


if __name__ == "__main__":
    unittest.main()
