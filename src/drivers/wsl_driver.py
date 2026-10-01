"""
Windows WSL2 Virtual Machine Driver for RunZero
Enables native lightweight Linux VM execution for GitHub Actions on Windows 10/11 & Windows Server,
with automatic integration with local caching proxies (Verdaccio, Athens).
"""

import os
import shutil
import subprocess
import sys
import time
import uuid
from typing import Dict, List, Optional

from . import RunnerDriver, RunnerInfo


class WSL2Driver(RunnerDriver):
    """Runs ephemeral runners as processes inside a WSL2 Linux distro, for the Windows host case."""

    def __init__(self, distro_base: str = "Ubuntu-24.04"):
        """Configure which WSL distro to run jobs in (falls back to the WSL_DISTRO_BASE env var)."""
        self.distro_base = os.getenv("WSL_DISTRO_BASE", distro_base)
        self._runner_created_at: Dict[str, float] = {}

    def name(self) -> str:
        """Return this driver's backend identifier: "wsl2"."""
        return "wsl2"

    def is_available(self) -> bool:
        """True if a `wsl`/`wsl.exe` binary is on PATH and `wsl --status` succeeds."""
        if not shutil.which("wsl.exe") and not shutil.which("wsl"):
            return False
        try:
            res = subprocess.run(["wsl", "--status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def spawn_runner(
        self,
        repo: Optional[str] = None,
        org: Optional[str] = None,
        arch: str = "x64",
        labels: Optional[str] = None,
        access_token: Optional[str] = None,
        cache_mounts: Optional[Dict[str, str]] = None,
        proxies_enabled: bool = True,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Launch `run.sh` inside `distro_base` as a detached background process and return its name.

        Unlike the VM drivers, this doesn't create a new WSL instance per runner -- it runs directly
        inside the existing distro. Returns None (and prints to stderr) only if the `wsl` invocation
        itself fails to start; the runner's own registration/execution happens asynchronously.
        """
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        instance_name = f"runzero-wsl{name_suffix}-{unique_id}"
        runner_labels = labels if labels else "self-hosted,local,wsl,x64,windows-host"

        proxy_env_block = ""
        if proxies_enabled:
            proxy_env_block = """
HOST_IP=$(ip route show default 2>/dev/null | awk '{print $3}' || echo "localhost")
export NPM_CONFIG_REGISTRY="http://${HOST_IP}:49501/"
export YARN_REGISTRY="http://${HOST_IP}:49501/"
export GOPROXY="http://${HOST_IP}:49500,https://proxy.golang.org,direct"
export PIP_INDEX_URL="http://${HOST_IP}:49507/root/pypi/+simple/"
export UV_INDEX_URL="${PIP_INDEX_URL}"
export PIP_TRUSTED_HOST="${HOST_IP}"
sudo mkdir -p /etc/apt/apt.conf.d
echo "Acquire::http::Proxy \"http://${HOST_IP}:49503\";" | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
mkdir -p /home/runner/.cargo
cat > /home/runner/.cargo/config.toml <<CARGOCFG
[source.crates-io]
replace-with = "kellnr-proxy"

[source.kellnr-proxy]
registry = "sparse+http://${HOST_IP}:49506/api/v1/cratesio/"
CARGOCFG
"""

        print(f"[Autoscaler:WSL2] 🚀 Spawning ephemeral WSL2 runner '{instance_name}' for {repo or org} with caching proxies...")

        try:
            cmd = ["wsl", "-d", self.distro_base, "-u", "runner", "--", "bash", "-c", f"""
{proxy_env_block}
export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{instance_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"
cd /home/runner/actions-runner && ./run.sh --unattended --ephemeral --name "{instance_name}" --labels "{runner_labels}"
"""]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._runner_created_at[instance_name] = time.time()
            return instance_name

        except Exception as e:
            print(f"[Autoscaler:WSL2] Error launching WSL runner: {e}", file=sys.stderr)
            return None

    def list_runners(self) -> List[RunnerInfo]:
        """List registered WSL distro names (via `wsl --list --quiet`) starting with "runzero-wsl".

        Returns an empty list (silently) if the `wsl --list` call itself fails.
        """
        try:
            res = subprocess.run(["wsl", "--list", "--quiet"], capture_output=True, text=True, check=True)
            runners = []
            for line in res.stdout.strip().split("\n"):
                name = line.strip().replace("\x00", "")
                if name.startswith("runzero-wsl-") or name.startswith("runzero-wsl"):
                    if name not in self._runner_created_at:
                        self._runner_created_at[name] = time.time()
                    runners.append(RunnerInfo(
                        id=name,
                        status="running",
                        name=name,
                        state="running",
                        target_repo="",
                        target_arch="x64",
                        backend="wsl2",
                        created_at=self._runner_created_at.get(name)
                    ))
            return runners
        except Exception:
            return []

    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        """Terminate any `runners` entries that are WSL2-backed and in "exited"/"stopped"/"dead" state."""
        for r in runners:
            if r.backend == "wsl2" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:WSL2] Terminating exited runner: {r.name}")
                self.destroy_runner(r.id)

    def destroy_runner(self, runner_id: str) -> bool:
        """Terminate the named WSL distro instance via `wsl --terminate`.

        Returns False (and prints to stderr) on any exception, including a timeout.
        """
        try:
            res = subprocess.run(["wsl", "--terminate", runner_id], capture_output=True, timeout=10)
            return res.returncode == 0
        except Exception as e:
            print(f"[Autoscaler:WSL2] Error destroying runner {runner_id}: {e}", file=sys.stderr)
            return False

    def cleanup_all(self) -> None:
        """Terminate every WSL2-backed runner this driver manages (used on autoscaler shutdown)."""
        runners = self.list_runners()
        for r in runners:
            if r.backend == "wsl2":
                subprocess.run(["wsl", "--terminate", r.id], capture_output=True)
