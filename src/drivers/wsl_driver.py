"""
Windows WSL2 Virtual Machine Driver for RunZero
Enables native lightweight Linux VM execution for GitHub Actions on Windows 10/11 & Windows Server,
with automatic integration with local caching proxies (Verdaccio, Athens).
"""

import os
import sys
import uuid
import shutil
import subprocess
from typing import List, Dict, Optional
from . import RunnerDriver, RunnerInfo


class WSL2Driver(RunnerDriver):
    def __init__(self, distro_base: str = "Ubuntu-22.04"):
        self.distro_base = os.getenv("WSL_DISTRO_BASE", distro_base)

    def name(self) -> str:
        return "wsl2"

    def is_available(self) -> bool:
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
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        instance_name = f"runzero-wsl{name_suffix}-{unique_id}"
        runner_labels = labels if labels else "self-hosted,local,wsl,x64,windows-host"

        proxy_env_block = ""
        if proxies_enabled:
            proxy_env_block = """
HOST_IP=$(ip route show default 2>/dev/null | awk '{print $3}' || echo "localhost")
export NPM_CONFIG_REGISTRY="http://${HOST_IP}:49501/"
export GOPROXY="http://${HOST_IP}:49500,https://proxy.golang.org,direct"
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
            return instance_name

        except Exception as e:
            print(f"[Autoscaler:WSL2] Error launching WSL runner: {e}", file=sys.stderr)
            return None

    def list_runners(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["wsl", "--list", "--quiet"], capture_output=True, text=True, check=True)
            runners = []
            for line in res.stdout.strip().split("\n"):
                name = line.strip().replace("\x00", "")
                if name.startswith("runzero-wsl-"):
                    runners.append(RunnerInfo(
                        id=name,
                        status="running",
                        name=name,
                        state="running",
                        target_repo="",
                        target_arch="x64",
                        backend="wsl2"
                    ))
            return runners
        except Exception:
            return []

    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "wsl2" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:WSL2] Terminating exited runner: {r.name}")
                self.destroy_runner(r.id)

    def destroy_runner(self, runner_id: str) -> bool:
        try:
            res = subprocess.run(["wsl", "--terminate", runner_id], capture_output=True, timeout=10)
            return res.returncode == 0
        except Exception as e:
            print(f"[Autoscaler:WSL2] Error destroying runner {runner_id}: {e}", file=sys.stderr)
            return False

    def cleanup_all(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "wsl2":
                subprocess.run(["wsl", "--terminate", r.id], capture_output=True)
