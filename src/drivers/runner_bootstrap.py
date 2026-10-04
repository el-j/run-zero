"""
Guest-side GitHub Actions runner bootstrap shared by every VM driver (OrbStack, Multipass, WSL2).

Two shell snippets, both used inside the guest:
- `runner_download_snippet()` installs the runner release for the guest's architecture.
- `register_and_run_snippet()` registers an ephemeral runner with the host-issued registration
  token (the admin PAT never enters the guest), runs exactly one job, then runs `finish`
  (e.g. power the VM off so the driver's prune step reaps it).

Every caller-supplied value is shell-quoted.
"""

import platform
import re
import shlex
import uuid

from .runner_env import export_block

RUNNER_VERSION = "2.337.0"

POWEROFF = 'echo "Ephemeral run finished -- powering off so the autoscaler prunes this VM."\n' + (
    "sudo systemctl poweroff 2>/dev/null || sudo poweroff 2>/dev/null || sudo shutdown -h now 2>/dev/null || true"
)


def normalize_arch(arch: str) -> str:
    """Fold arch aliases to RunZero's two arches: "amd64" ("x64"/"x86_64" too) or "arm64"."""
    return "amd64" if arch in ("amd64", "x64", "x86_64") else "arm64"


def host_arch() -> str:
    """The host CPU as a RunZero arch. Multipass and WSL2 can only run guests of this arch."""
    return "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "amd64"


def instance_name(prefix: str, arch: str, target: str) -> str:
    """A unique instance name valid for Multipass and WSL2 ([a-z0-9-]): prefix, arch, target slug, id."""
    slug = re.sub(r"[^a-z0-9]+", "-", target.lower()).strip("-")[:30].strip("-")
    suffix = uuid.uuid4().hex[:6]
    return f"{prefix}{arch}-{slug}-{suffix}" if slug else f"{prefix}{arch}-{suffix}"


def runner_tarball_arch(arch: str) -> str:
    """GitHub's release-asset arch name for a RunZero arch ("amd64"/"x64"/"x86_64" -> "x64", else "arm64")."""
    return "x64" if arch in ("amd64", "x64", "x86_64") else "arm64"


def windows_to_wsl_path(path: str) -> str:
    """Translate a Windows host path (C:\\foo or C:/foo) to WSL2's /mnt/c/foo mount path."""
    clean = path.replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", clean)
    if m:
        drive = m.group(1).lower()
        rest = m.group(2)
        return f"/mnt/{drive}/{rest}"
    if clean.startswith("/"):
        return clean
    return f"/mnt/c/{clean.lstrip('/')}"


def runner_download_snippet(arch: str, runner_version: str = RUNNER_VERSION, home: str = "/home/runner") -> str:
    """Shell snippet that downloads and unpacks the runner for `arch` into `<home>/actions-runner`."""
    runner_dir = shlex.quote(f"{home}/actions-runner")
    return f"""
mkdir -p {runner_dir} && cd {runner_dir}
RUNNER_ARCH={shlex.quote(runner_tarball_arch(arch))}
curl -fsSL -O "https://github.com/actions/runner/releases/download/v{runner_version}/actions-runner-linux-${{RUNNER_ARCH}}-{runner_version}.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-{runner_version}.tar.gz"
rm "./actions-runner-linux-${{RUNNER_ARCH}}-{runner_version}.tar.gz"
sudo ./bin/installdependencies.sh
"""


def register_and_run_snippet(
    runner_url: str,
    registration_token: str,
    runner_name: str,
    labels: str,
    home: str = "/home/runner",
    finish: str = "",
    env: dict[str, str] | None = None,
) -> str:
    """Shell snippet: register one ephemeral runner with `config.sh`, run it, then run `finish`.

    `registration_token` is the short-lived token from `github_api.create_registration_token`.
    `env` (see `runner_env.cache_env`) is exported first, so `run.sh` and every job step inherit it.
    `run.sh` failing still reaches `finish`, so the guest is always cleaned up.
    """
    return f"""
{export_block(env or {})}
cd {shlex.quote(f"{home}/actions-runner")}

./config.sh --url {shlex.quote(runner_url)} --token {shlex.quote(registration_token)} --name {shlex.quote(runner_name)} --work "_work" \\
  --unattended --replace --ephemeral --labels {shlex.quote(labels)}

echo "Starting runner "{shlex.quote(runner_name)}"..."
./run.sh || true
{finish}
"""
