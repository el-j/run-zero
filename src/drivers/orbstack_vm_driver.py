"""
🪐 OrbStack Virtual Machine Runner Driver
Spawns and manages dedicated, lightweight Linux Virtual Machines via OrbStack (Apple Virtualization framework).
Provides full systemd, dedicated kernel, internal Docker daemon, unconfined browser sandboxes,
and automatic integration with local caching proxies (Verdaccio, Athens, apt-cacher-ng).
"""

import json
import os
import shutil
import subprocess
import sys
import uuid
from typing import Dict, List, Optional

from . import RunnerDriver, RunnerInfo
from .orbstack_templates import docker_engine_snippet, registration_and_run_snippet, runner_download_snippet

RUNNER_VERSION = "2.336.0"
RUNNER_VM_PREFIX = "runzero-vm-"
BASE_IMAGE_PREFIX = "runzero-vm-base-"


class OrbStackVMDriver(RunnerDriver):
    def __init__(self, distro: str = "ubuntu:24.04"):
        self.distro = distro
        self._provision_script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "docker", "provision-toolchain.sh"
        )

    def name(self) -> str:
        return "orbstack-vm"

    def is_available(self) -> bool:
        if not shutil.which("orbctl") or not shutil.which("orb"):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, text=True, check=True)
            return "running" in res.stdout.lower()
        except Exception:
            return False

    @staticmethod
    def base_image_name(orb_arch: str) -> str:
        return f"{BASE_IMAGE_PREFIX}{orb_arch}"

    def _list_vm_names(self) -> List[str]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            return [vm.get("name", "") for vm in vms]
        except Exception:
            return []

    def base_image_exists(self, orb_arch: str) -> bool:
        return self.base_image_name(orb_arch) in self._list_vm_names()

    def _read_provision_script(self) -> Optional[str]:
        if not os.path.isfile(self._provision_script_path):
            print(
                f"[Autoscaler:OrbStack-VM] Error: shared provisioning script not found at "
                f"{self._provision_script_path}", file=sys.stderr
            )
            return None
        with open(self._provision_script_path, "r") as f:
            return f.read()

    def build_base_image(self, orb_arch: str) -> bool:
        """Build (or rebuild) the golden VM image ephemeral job VMs clone from."""
        script_content = self._read_provision_script()
        if script_content is None:
            return False

        base_name = self.base_image_name(orb_arch)
        print(f"[Autoscaler:OrbStack-VM] 🏗️  Building golden base image '{base_name}' ({self.distro})...")

        try:
            subprocess.run(["orbctl", "delete", "-f", base_name], capture_output=True)
            subprocess.run(
                ["orbctl", "create", "-a", orb_arch, "-u", "runner", self.distro, base_name],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            print(f"[Autoscaler:OrbStack-VM] Error creating base image: {stderr}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating base image: {e}", file=sys.stderr)
            return False

        full_script = f"""
exec > /home/runner/provision.log 2>&1
set -e
export ARCH="{orb_arch}"
set -- "{orb_arch}"
{docker_engine_snippet()}
{script_content}
{runner_download_snippet(orb_arch, RUNNER_VERSION)}
echo "Base image provisioning complete."
"""
        try:
            result = subprocess.run(
                ["orb", "-m", base_name, "-u", "runner", "bash", "-c", full_script],
                capture_output=True, timeout=1800
            )
            if result.returncode != 0:
                print(
                    f"[Autoscaler:OrbStack-VM] Base image provisioning failed (exit {result.returncode}). "
                    f"Check /home/runner/provision.log inside '{base_name}' for details.", file=sys.stderr
                )
                return False
        except subprocess.TimeoutExpired:
            print("[Autoscaler:OrbStack-VM] Base image provisioning timed out after 30 minutes.", file=sys.stderr)
            return False

        subprocess.run(["orbctl", "stop", base_name], capture_output=True)
        print(f"[Autoscaler:OrbStack-VM] ✅ Golden base image '{base_name}' ready. Future spawns will clone it.")
        return True

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
        vm_name = f"{RUNNER_VM_PREFIX}{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels += ",rosetta"
        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        proxy_env_block = ""
        if proxies_enabled:
            proxy_env_block = """
export npm_config_registry="http://host.orb.internal:49501"
export YARN_REGISTRY="http://host.orb.internal:49501"
export GOPROXY="http://host.orb.internal:49500,https://proxy.golang.org,direct"
"""

        if repo:
            api_base = f"https://api.github.com/repos/{repo}/actions/runners"
            runner_url = f"https://github.com/{repo}"
        else:
            api_base = f"https://api.github.com/orgs/{org}/actions/runners"
            runner_url = f"https://github.com/{org}"

        base_name = self.base_image_name(orb_arch)
        if not self.base_image_exists(orb_arch):
            print(
                f"[Autoscaler:OrbStack-VM] 🏗️  Golden base image '{base_name}' not found. "
                f"Creating master VM base image first (one-time setup)..."
            )
            built = self.build_base_image(orb_arch)
            if not built:
                print(
                    f"[Autoscaler:OrbStack-VM] ❌ Failed to build golden base image '{base_name}'.",
                    file=sys.stderr
                )
                return None

        reg_and_run = registration_and_run_snippet(
            api_base, runner_url, access_token or "", vm_name, runner_labels, proxy_env_block
        )

        print(
            f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' "
            f"(cloned from golden image '{base_name}')..."
        )
        clone_cmd = ["orbctl", "clone", base_name, vm_name]
        setup_script = f"""
exec > /home/runner/setup.log 2>&1
trap 'sudo shutdown -h now' EXIT
set -e
{reg_and_run}
"""

        try:
            subprocess.run(clone_cmd, check=True, capture_output=True)
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", setup_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return vm_name
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {stderr}", file=sys.stderr)
            return None

    def list_runners(self) -> List[RunnerInfo]:
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "[]")
            runners = []
            for vm in vms:
                name = vm.get("name", "")
                if name.startswith(RUNNER_VM_PREFIX) and not name.startswith(BASE_IMAGE_PREFIX):
                    status = vm.get("state", "running")
                    arch = "amd64" if "amd64" in name else "arm64"
                    status_lower = status.lower()
                    if status_lower in ("running", "active"):
                        state = "running"
                    elif status_lower in ("creating", "provisioning"):
                        # Transient startup states, NOT a terminal/prunable state --
                        # misclassifying these as "exited" undercounts genuinely
                        # in-flight VMs in main()'s active-runner tally, causing it
                        # to spawn a duplicate for the same job before the first one
                        # finishes booting (confirmed live: 3 runners registered for
                        # one real queued job, the 2 losers idle forever since
                        # ephemeral runners only self-terminate after completing a
                        # job, never just for being unclaimed).
                        state = "pending"
                    else:
                        state = "exited"
                    target_repo = ""
                    name_body = name[len(RUNNER_VM_PREFIX):]
                    body_parts = name_body.split("-")
                    if len(body_parts) >= 3:
                        target_repo = "-".join(body_parts[1:-1])
                    runners.append(RunnerInfo(
                        id=name,
                        name=name,
                        status=status,
                        state=state,
                        target_repo=target_repo,
                        target_arch=arch,
                        backend="orbstack-vm"
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def destroy_runner(self, runner_id: str) -> bool:
        try:
            subprocess.run(["orbctl", "delete", "-f", runner_id], check=True, capture_output=True)
            return True
        except Exception:
            return False

    def prune_exited(self, active_runners: List[RunnerInfo]) -> None:
        for r in active_runners:
            if r.backend == "orbstack-vm" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                self.destroy_runner(r.name)

    def cleanup_all(self) -> None:
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                self.destroy_runner(r.name)
