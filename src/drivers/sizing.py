"""
Per-runner CPU/memory sizing: explicit RUNNER_CPUS/RUNNER_MEMORY, or derived from host capacity (#71).

Without limits every runner VM/container may claim every host core, so MAX_RUNNERS concurrent
jobs oversubscribe the host (measured: load ~23 on 10 cores, vitest workers timing out). When
the variables are unset, each runner gets an equal share of the host after a reserve for the
proxies, the bridge and the OS. Configured values are kept as-is, but a configuration whose
MAX_RUNNERS x size exceeds the host is reported as a warning.
"""

import os
import re
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

# Kept free for the caching proxies, the bridge/autoscaler and the host OS.
RESERVE_CPUS = 1
RESERVE_MEMORY_MIB = 2048
# Never derive a runner smaller than this; below it a job VM barely boots.
MIN_MEMORY_MIB = 1024

_MEMORY_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([kmgt]?)i?b?\s*$", re.IGNORECASE)
_MIB_PER_UNIT = {"": 1 / (1024 * 1024), "k": 1 / 1024, "m": 1, "g": 1024, "t": 1024 * 1024}


@dataclass(frozen=True)
class HostCapacity:
    """CPUs and memory available to runners on this host (or in the VM pool that runs them)."""

    cpus: int
    memory_mib: int


@dataclass(frozen=True)
class RunnerSizing:
    """The CPU/memory limit each runner gets, and any oversubscription warnings."""

    cpus: int | None
    memory_mib: int | None
    source: str  # "configured", "derived" or "unlimited"
    host: HostCapacity
    max_runners: int
    warnings: tuple[str, ...] = field(default=())

    @property
    def cpus_arg(self) -> str | None:
        """`--cpus` value for docker/orbctl/multipass, or None for unlimited."""
        return str(self.cpus) if self.cpus else None

    @property
    def memory_arg(self) -> str | None:
        """`--memory` value (MiB with an `M` suffix, accepted by docker/orbctl/multipass), or None."""
        return f"{self.memory_mib}M" if self.memory_mib else None

    def describe(self) -> str:
        """One-line human summary for logs."""
        cpus = f"{self.cpus} CPU" if self.cpus else "unlimited CPU"
        mem = f"{self.memory_mib} MiB" if self.memory_mib else "unlimited memory"
        host = f"host {self.host.cpus} CPU / {self.host.memory_mib} MiB"
        return f"{cpus}, {mem} per runner x {self.max_runners} ({self.source}; {host})"

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable form for /health and the dashboard."""
        return {
            "cpus": self.cpus,
            "memory_mib": self.memory_mib,
            "source": self.source,
            "max_runners": self.max_runners,
            "host_cpus": self.host.cpus,
            "host_memory_mib": self.host.memory_mib,
            "warnings": list(self.warnings),
        }


def parse_memory_mib(value: str) -> int | None:
    """Parse `4G`, `4096M`, `512MiB`, `4096` (MiB) into MiB; None if unparseable."""
    match = _MEMORY_RE.match(value)
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2).lower()
    if unit == "" and "." not in match.group(1):
        return int(number)  # a bare integer means MiB, as orbctl reads it
    return int(number * _MIB_PER_UNIT[unit])


def _parse_cpus(value: str) -> int | None:
    """Parse a CPU count (fractions round up, as a partial core still needs a core); None if invalid."""
    try:
        cpus = float(value)
    except ValueError:
        return None
    return max(1, int(-(-cpus // 1))) if cpus > 0 else None


def host_capacity() -> HostCapacity:
    """CPU count and physical memory of the machine this process runs on."""
    cpus = os.cpu_count() or 1
    try:
        memory_mib = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") // (1024 * 1024)
    except (ValueError, OSError, AttributeError):
        memory_mib = 0
    return HostCapacity(cpus=cpus, memory_mib=int(memory_mib))


def orbstack_capacity() -> HostCapacity:
    """OrbStack's VM pool (`orb config show` cpu / memory_mib), falling back to the host."""
    host = host_capacity()
    try:
        out = subprocess.run(["orb", "config", "show"], capture_output=True, text=True, timeout=5, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return host
    values = dict(line.split(": ", 1) for line in out.splitlines() if ": " in line)
    cpus = _parse_cpus(values.get("cpu", "")) or host.cpus
    memory_mib = parse_memory_mib(values.get("memory_mib", "")) or host.memory_mib
    return HostCapacity(cpus=min(cpus, host.cpus), memory_mib=min(memory_mib, host.memory_mib) if host.memory_mib else memory_mib)


def derive_sizing(host: HostCapacity, max_runners: int) -> tuple[int, int]:
    """Equal share of the host per runner after the reserve: (cpus, memory_mib)."""
    runners = max(1, max_runners)
    cpus = max(1, (host.cpus - RESERVE_CPUS) // runners)
    memory_mib = max(MIN_MEMORY_MIB, (host.memory_mib - RESERVE_MEMORY_MIB) // runners)
    return cpus, memory_mib


def oversubscription_warnings(cpus: int | None, memory_mib: int | None, host: HostCapacity, max_runners: int) -> tuple[str, ...]:
    """Warnings for a sizing whose MAX_RUNNERS x per-runner limit exceeds the host."""
    warnings = []
    if cpus is None:
        warnings.append(f"RUNNER_CPUS is unlimited: {max_runners} concurrent runners can each claim all {host.cpus} host CPUs")
    elif cpus * max_runners > host.cpus:
        warnings.append(f"MAX_RUNNERS x RUNNER_CPUS = {max_runners} x {cpus} = {cpus * max_runners} exceeds the host's {host.cpus} CPUs")
    if memory_mib is not None and host.memory_mib and memory_mib * max_runners > host.memory_mib:
        warnings.append(
            f"MAX_RUNNERS x RUNNER_MEMORY = {max_runners} x {memory_mib} MiB = {memory_mib * max_runners} MiB exceeds the host's {host.memory_mib} MiB"
        )
    return tuple(warnings)


def resolve_sizing(env: Mapping[str, str], capacity: Callable[[], HostCapacity] | None = None) -> RunnerSizing:
    """Sizing from RUNNER_CPUS/RUNNER_MEMORY/MAX_RUNNERS in `env`, deriving whatever is unset.

    `capacity` measures the pool runners share (default: this host; OrbStack passes its VM
    pool). It is not called with `RUNNER_SIZING=unlimited`, which keeps the old no-limits behavior.
    """
    try:
        max_runners = max(1, int(env.get("MAX_RUNNERS") or 4))
    except ValueError:
        max_runners = 4
    if (env.get("RUNNER_SIZING") or "").strip().lower() == "unlimited":
        host = host_capacity()
        return RunnerSizing(None, None, "unlimited", host, max_runners, oversubscription_warnings(None, None, host, max_runners))

    host = (capacity or host_capacity)()
    derived_cpus, derived_mem = derive_sizing(host, max_runners)
    cpus = _parse_cpus(env.get("RUNNER_CPUS") or "")
    memory_mib = parse_memory_mib(env.get("RUNNER_MEMORY") or "")
    source = "configured" if cpus or memory_mib else "derived"
    cpus = cpus or derived_cpus
    memory_mib = memory_mib or derived_mem
    return RunnerSizing(cpus, memory_mib, source, host, max_runners, oversubscription_warnings(cpus, memory_mib, host, max_runners))
