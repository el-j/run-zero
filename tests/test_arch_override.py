"""
Tests for arch_override: serving amd64 jobs natively on arm64 hosts, opt-in per repo (#75).
"""

import unittest
from unittest.mock import patch

from arch_override import NativeArchOverride, normalize_host_arch, validate

AMD_JOB = ["self-hosted", "local", "amd64"]


class TestDecision(unittest.TestCase):
    def test_off_never_overrides(self):
        self.assertEqual(NativeArchOverride("off", host_arch="arm64").arch_for("amd64", AMD_JOB, "el-j/herbful"), "amd64")
        self.assertEqual(NativeArchOverride(None, host_arch="arm64").arch_for("amd64", AMD_JOB, "el-j/herbful"), "amd64")

    def test_all_overrides_every_repo(self):
        self.assertEqual(NativeArchOverride("ALL", host_arch="arm64").arch_for("amd64", AMD_JOB, "any/repo"), "arm64")

    def test_list_overrides_only_listed_repos_case_insensitively(self):
        override = NativeArchOverride(" el-j/Herbful , el-j/other ", host_arch="arm64")
        self.assertEqual(override.arch_for("amd64", AMD_JOB, "el-j/herbful"), "arm64")
        self.assertEqual(override.arch_for("amd64", AMD_JOB, "EL-J/OTHER"), "arm64")
        self.assertEqual(override.arch_for("amd64", AMD_JOB, "el-j/run-zero"), "amd64")

    def test_noop_on_amd64_host(self):
        override = NativeArchOverride("all", host_arch="amd64")
        self.assertEqual(override.arch_for("amd64", AMD_JOB, "el-j/herbful"), "amd64")
        self.assertEqual(override.arch_for("arm64", ["arm64"], "el-j/herbful"), "arm64")

    def test_arm64_jobs_are_untouched(self):
        self.assertEqual(NativeArchOverride("all", host_arch="arm64").arch_for("arm64", ["arm64"], "o/r"), "arm64")

    def test_explicit_emulation_labels_are_respected(self):
        override = NativeArchOverride("all", host_arch="arm64")
        for label in ("rosetta", "X86_64"):
            with self.subTest(label=label):
                self.assertEqual(override.arch_for("amd64", [*AMD_JOB, label], "o/r"), "amd64")

    @patch("arch_override.platform.machine", return_value="aarch64")
    def test_host_arch_defaults_to_this_machine(self, _machine):
        self.assertEqual(NativeArchOverride("all").host_arch, "arm64")

    def test_describe(self):
        self.assertEqual(NativeArchOverride("off", host_arch="arm64").describe(), "off")
        self.assertEqual(NativeArchOverride("all", host_arch="arm64").describe(), "amd64 jobs run natively on arm64 for all repositories")
        self.assertEqual(NativeArchOverride("b/b,a/a", host_arch="arm64").describe(), "amd64 jobs run natively on arm64 for a/a, b/b")
        self.assertEqual(NativeArchOverride("all", host_arch="amd64").describe(), "configured for all repositories, inactive on this amd64 host")
        self.assertIn("mode='list'", repr(NativeArchOverride("a/b", host_arch="arm64")))


class TestHelpers(unittest.TestCase):
    def test_normalize_host_arch(self):
        self.assertEqual([normalize_host_arch(m) for m in ("arm64", "AARCH64", "x86_64", "AMD64", "riscv64")], ["arm64", "arm64", "amd64", "amd64", "riscv64"])

    def test_validate(self):
        for ok in ("off", "ALL", "o/r", "o/r, o/s"):
            with self.subTest(value=ok):
                self.assertIsNone(validate(ok))
        for bad in ("yes", "o/r,", "/r", "o/", "a/b/c", " "):
            with self.subTest(value=bad):
                self.assertIn("must be off, all", validate(bad) or "")


if __name__ == "__main__":
    unittest.main()
