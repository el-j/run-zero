"""
Tests for drivers.sizing: per-runner CPU/memory sizing and oversubscription warnings (#71).
"""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from drivers.sizing import (
    MIN_MEMORY_MIB,
    HostCapacity,
    RunnerSizing,
    derive_sizing,
    host_capacity,
    orbstack_capacity,
    oversubscription_warnings,
    parse_memory_mib,
    resolve_sizing,
)

MAC = HostCapacity(cpus=11, memory_mib=16384)


class TestParseMemory(unittest.TestCase):
    def test_units(self):
        cases = {"4G": 4096, "4g": 4096, "4GiB": 4096, "4096M": 4096, "512MiB": 512, "4096": 4096, "1.5G": 1536, "1T": 1048576, "2097152k": 2048}
        for raw, mib in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(parse_memory_mib(raw), mib)

    def test_bare_fraction_is_bytes(self):
        self.assertEqual(parse_memory_mib("1048576.0"), 1)

    def test_garbage(self):
        self.assertIsNone(parse_memory_mib("lots"))
        self.assertIsNone(parse_memory_mib(""))


class TestDerive(unittest.TestCase):
    def test_equal_share_after_reserve(self):
        self.assertEqual(derive_sizing(MAC, 3), (3, 4778))

    def test_single_core_host(self):
        self.assertEqual(derive_sizing(HostCapacity(1, 2048), 1), (1, MIN_MEMORY_MIB))

    def test_huge_max_runners_never_drops_below_minimums(self):
        self.assertEqual(derive_sizing(MAC, 1000), (1, MIN_MEMORY_MIB))

    def test_zero_max_runners_is_treated_as_one(self):
        self.assertEqual(derive_sizing(MAC, 0), (10, 14336))


class TestWarnings(unittest.TestCase):
    def test_fits(self):
        self.assertEqual(oversubscription_warnings(3, 4096, MAC, 3), ())

    def test_cpu_oversubscribed(self):
        (warning,) = oversubscription_warnings(4, 4096, MAC, 3)
        self.assertIn("3 x 4 = 12 exceeds the host's 11 CPUs", warning)

    def test_memory_oversubscribed(self):
        (warning,) = oversubscription_warnings(3, 8192, MAC, 3)
        self.assertIn("24576 MiB exceeds the host's 16384 MiB", warning)

    def test_unknown_host_memory_is_not_flagged(self):
        self.assertEqual(oversubscription_warnings(1, 8192, HostCapacity(4, 0), 2), ())

    def test_unlimited(self):
        (warning,) = oversubscription_warnings(None, None, MAC, 2)
        self.assertIn("unlimited", warning)


class TestResolve(unittest.TestCase):
    def test_derived_when_unset(self):
        sizing = resolve_sizing({"MAX_RUNNERS": "3"}, lambda: MAC)
        self.assertEqual((sizing.cpus, sizing.memory_mib, sizing.source), (3, 4778, "derived"))
        self.assertEqual((sizing.cpus_arg, sizing.memory_arg), ("3", "4778M"))
        self.assertEqual(sizing.warnings, ())

    def test_configured_values_win_and_partial_config_derives_the_rest(self):
        sizing = resolve_sizing({"MAX_RUNNERS": "3", "RUNNER_CPUS": "2.5"}, lambda: MAC)
        self.assertEqual((sizing.cpus, sizing.memory_mib, sizing.source), (3, 4778, "configured"))
        sizing = resolve_sizing({"MAX_RUNNERS": "3", "RUNNER_MEMORY": "4G"}, lambda: MAC)
        self.assertEqual((sizing.cpus, sizing.memory_mib), (3, 4096))

    def test_configured_oversubscription_is_warned(self):
        sizing = resolve_sizing({"MAX_RUNNERS": "4", "RUNNER_CPUS": "4"}, lambda: MAC)
        self.assertEqual(len(sizing.warnings), 1)

    def test_invalid_values_fall_back(self):
        sizing = resolve_sizing({"MAX_RUNNERS": "many", "RUNNER_CPUS": "-1", "RUNNER_MEMORY": "huge"}, lambda: MAC)
        self.assertEqual((sizing.max_runners, sizing.cpus, sizing.source), (4, 2, "derived"))
        self.assertEqual(resolve_sizing({"RUNNER_CPUS": "x"}, lambda: MAC).source, "derived")

    def test_unlimited_mode_never_measures_the_pool(self):
        capacity = MagicMock()
        sizing = resolve_sizing({"RUNNER_SIZING": "Unlimited", "MAX_RUNNERS": "2"}, capacity)
        capacity.assert_not_called()
        self.assertEqual((sizing.cpus_arg, sizing.memory_arg, sizing.source), (None, None, "unlimited"))
        self.assertEqual(len(sizing.warnings), 1)

    def test_describe_and_to_dict(self):
        sizing = RunnerSizing(3, 4096, "configured", MAC, 3)
        self.assertEqual(sizing.describe(), "3 CPU, 4096 MiB per runner x 3 (configured; host 11 CPU / 16384 MiB)")
        self.assertEqual(
            RunnerSizing(None, None, "unlimited", MAC, 2).describe(), "unlimited CPU, unlimited memory per runner x 2 (unlimited; host 11 CPU / 16384 MiB)"
        )
        self.assertEqual(
            sizing.to_dict(),
            {"cpus": 3, "memory_mib": 4096, "source": "configured", "max_runners": 3, "host_cpus": 11, "host_memory_mib": 16384, "warnings": []},
        )


class TestCapacity(unittest.TestCase):
    def test_host_capacity_reads_this_machine(self):
        host = host_capacity()
        self.assertGreaterEqual(host.cpus, 1)
        self.assertGreater(host.memory_mib, 0)

    @patch("drivers.sizing.os.sysconf", side_effect=ValueError)
    @patch("drivers.sizing.os.cpu_count", return_value=None)
    def test_host_capacity_degrades(self, _cpu, _sysconf):
        self.assertEqual(host_capacity(), HostCapacity(1, 0))

    @patch("drivers.sizing.host_capacity", return_value=HostCapacity(11, 36864))
    @patch("drivers.sizing.subprocess.run")
    def test_orbstack_pool_caps_the_host(self, run, _host):
        run.return_value = MagicMock(stdout="cpu: 8\nmemory_mib: 16384\nmachine.docker.cpu: 0\n")
        self.assertEqual(orbstack_capacity(), HostCapacity(8, 16384))
        run.return_value = MagicMock(stdout="cpu: 0\nmemory_mib: 0\n")  # 0 = OrbStack default
        self.assertEqual(orbstack_capacity(), HostCapacity(11, 36864))

    @patch("drivers.sizing.host_capacity", return_value=HostCapacity(4, 0))
    @patch("drivers.sizing.subprocess.run", return_value=MagicMock(stdout="memory_mib: 8192\n"))
    def test_orbstack_pool_when_host_memory_unknown(self, _run, _host):
        self.assertEqual(orbstack_capacity(), HostCapacity(4, 8192))

    @patch("drivers.sizing.host_capacity", return_value=MAC)
    @patch("drivers.sizing.subprocess.run", side_effect=subprocess.TimeoutExpired("orb", 5))
    def test_orbstack_unavailable_falls_back_to_host(self, _run, _host):
        self.assertEqual(orbstack_capacity(), MAC)


if __name__ == "__main__":
    unittest.main()
