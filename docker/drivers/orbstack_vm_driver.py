"""
OrbStack Linux VM Execution Driver for RunZero
Spawns and manages dedicated, lightweight Linux Virtual Machines via OrbStack (Apple Virtualization framework).
Provides full systemd, dedicated kernel, internal Docker daemon, and unconfined browser sandboxes.
"""

import os
import sys
import uuid
import json
import shutil
import subprocess
from typing import List, Dict, Optional
from . import RunnerDriver, RunnerInfo


class OrbStackVMDriver(RunnerDriver):
    def __init__(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("ORB_DISTRO", distro)

    def name(self) -> str:
        return "orbstack-vm"

    def is_available(self) -> bool:
        if not (shutil.which("orbctl") or shutil.which("orb")):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def spawn_runner(
        self,
        repo: Optional[str] = None,
        org: Optional[str] = None,
        arch: str = "arm64",
        labels: Optional[str] = None,
        access_token: Optional[str] = None,
        cache_mounts: Optional[Dict[str, str]] = None,
        proxies_enabled: bool = True,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-vm-{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' ({self.distro})...")

        try:
            # 1. Create the VM
            create_cmd = [
                "orbctl", "create",
                "-a", orb_arch,
                "-u", "runner",
                self.distro,
                vm_name
            ]
            subprocess.run(create_cmd, check=True, capture_output=True)

            # 2. Setup runner workspace & runner binary inside the VM asynchronously
            runner_setup_script = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y && sudo apt-get install -y --no-install-recommends curl jq git git-lfs ca-certificates build-essential
sudo echo "runner ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers > /dev/null

mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-2.336.0.tar.gz"
sudo ./bin/installdependencies.sh

export ACCESS_TOKEN="{access_token}"
export RUNNER_NAME="{vm_name}"
export RUNNER_LABELS="{runner_labels}"
export EPHEMERAL="true"
export REPO="{repo or ''}"
export ORG="{org or ''}"

nohup ./run.sh --unattended --ephemeral --name "{vm_name}" --labels "{runner_labels}" > /home/runner/runner.log 2>&1 &
"""
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", runner_setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def list_runners(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith("runzero-vm-"):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    state = "running" if status.lower() in ("running", "active") else "exited"
                    runners.append(RunnerInfo(
                        id=name,
                        status=status,
                        name=name,
                        state=state,
                        target_repo="",
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def prune_exited(self, runners: List[RunnerInfo]) -> None:
        for r in runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "dead", "stopped"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)

    def destroy_runner(self, runner_id: str) -> bool:
        res = subprocess.run(["orbctl", "delete", "-f", runner_id], capture_output=True)
        return res.returncode == 0

    def cleanup_all(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                print(f"[Autoscaler:OrbStack-VM] Cleaning up VM: {r.name}")
                subprocess.run(["orbctl", "delete", "-f", r.name], capture_output=True)
