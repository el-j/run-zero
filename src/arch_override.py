"""
Opt-in native-arch override: serve amd64 jobs with a host-native runner, no workflow changes (#75).

A workflow that requests `[self-hosted, local, amd64]` must keep working unchanged on
GitHub-hosted `ubuntu-latest`. On Apple Silicon, though, every such job runs under Rosetta
emulation, several times slower for Node and browsers, although most jobs (Node, pnpm,
Playwright, Go) are architecture-neutral. With `NATIVE_ARCH_OVERRIDE` RunZero itself decides
to serve those jobs natively: the runner is spawned for the host's arch, still carries the
job's `amd64` label (job labels are always merged into the runner's), and `RUNNER_ARCH`
inside it is the native one, so `setup-node` and Playwright fetch native binaries.

Trade-off: a job that inspects `uname -m`, or builds amd64 artifacts without `--platform`,
gets arm64. Keep such repositories off the list. Jobs that ask for emulation explicitly
(a `rosetta`/`x86_64` label) are never overridden.
"""

import platform

OFF = "off"
ALL = "all"
# Labels that ask for real x86-64 rather than "whatever ubuntu-latest would be".
EMULATION_LABELS = frozenset({"rosetta", "x86_64"})


class NativeArchOverride:
    """Which repositories' amd64 jobs to serve natively: none ("off"), all, or a list."""

    def __init__(self, raw: str | None, host_arch: str | None = None):
        """Parse `raw` ("off", "all", or comma-separated owner/repo names; case-insensitive).

        `host_arch` defaults to this machine's (the autoscaler container runs natively on
        its host, so `platform.machine()` reports the host's arch).
        """
        value = (raw or OFF).strip().lower()
        self.mode = value if value in (OFF, ALL) else "list"
        self.repos = frozenset(r.strip() for r in value.split(",") if r.strip()) if self.mode == "list" else frozenset()
        self.host_arch = host_arch or normalize_host_arch(platform.machine())

    def __repr__(self) -> str:
        """Readable form for logs and test failures."""
        return f"NativeArchOverride(mode={self.mode!r}, repos={sorted(self.repos)}, host_arch={self.host_arch!r})"

    def describe(self) -> str:
        """One-line summary for the startup banner."""
        if self.mode == OFF:
            return "off"
        scope = "all repositories" if self.mode == ALL else ", ".join(sorted(self.repos))
        if self.host_arch != "arm64":
            return f"configured for {scope}, inactive on this {self.host_arch} host"
        return f"amd64 jobs run natively on arm64 for {scope}"

    def applies_to(self, repo: str) -> bool:
        """True if `repo` (owner/name) opted in."""
        return self.mode == ALL or (self.mode == "list" and repo.lower() in self.repos)

    def arch_for(self, job_arch: str, job_labels: list[str], repo: str) -> str:
        """The arch to spawn for a job resolved to `job_arch`.

        Only an amd64 job, on an arm64 host, of an opted-in repo, that doesn't explicitly ask
        for emulation, is moved to arm64. Everything else is returned unchanged.
        """
        if job_arch != "amd64" or self.host_arch != "arm64" or not self.applies_to(repo):
            return job_arch
        if EMULATION_LABELS & {label.lower() for label in job_labels}:
            return job_arch
        return "arm64"


def normalize_host_arch(machine: str) -> str:
    """Map `platform.machine()` spellings to "arm64"/"amd64" (anything else is returned lowercased)."""
    machine = machine.lower()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    if machine in ("x86_64", "amd64"):
        return "amd64"
    return machine


def validate(raw: str) -> str | None:
    """Error message for an invalid NATIVE_ARCH_OVERRIDE value, or None if it's valid."""
    value = raw.strip().lower()
    if value in (OFF, ALL):
        return None
    bad = [r for r in (p.strip() for p in value.split(",")) if r.count("/") != 1 or r.startswith("/") or r.endswith("/")]
    if bad or not value:
        return f"NATIVE_ARCH_OVERRIDE={raw!r} must be off, all, or comma-separated owner/repo names"
    return None
