"""
Canonical Multipass VM Execution Driver for RunZero
Cross-platform VM execution for macOS, Linux, and Windows using lightweight QEMU/Hyper-V/VirtualBox VMs,
with automatic integration with local caching proxies (Verdaccio, Athens, devpi, kellnr, apt-cacher-ng).

Each job gets a fresh Ubuntu VM (`multipass launch`) that installs the runner for its
architecture, registers one ephemeral runner with a host-issued registration token, runs one
job and powers itself off; `prune_exited()` then deletes and purges it. Multipass only runs
guests of the host's own architecture, so other-arch requests are refused (the autoscaler
falls back to its default driver). Which repo/org, arch and creation time an instance belongs
to is kept host-side in an `InstanceStore`.
"""

import json
import os
import shlex
import shutil
import subprocess
import sys
import time

from . import RunnerDriver, RunnerInfo, merge_labels
from .instance_store import InstanceStore, default_state_dir
from .runner_bootstrap import host_arch, instance_name, normalize_arch, register_and_run_snippet, runner_download_snippet

NAME_PREFIX = "runzero-mp-"
GUEST_HOME = "/home/ubuntu"

# The guest powers itself off on exit (success or failure) so a broken bootstrap can't leave
# a VM running forever; prune_exited() then deletes it.
_POWEROFF_TRAP = "trap 'sudo systemctl poweroff 2>/dev/null || sudo poweroff 2>/dev/null || true' EXIT"

_PROXY_ENV_BLOCK = f"""
HOST_IP=$(ip route | awk '/default/ {{ print $3 }}' || echo "192.168.64.1")
export NPM_CONFIG_REGISTRY="http://${{HOST_IP}}:49501/"
export YARN_REGISTRY="http://${{HOST_IP}}:49501/"
export GOPROXY="http://${{HOST_IP}}:49500,https://proxy.golang.org,direct"
export PIP_INDEX_URL="http://${{HOST_IP}}:49507/root/pypi/+simple/"
export UV_INDEX_URL="${{PIP_INDEX_URL}}"
export PIP_TRUSTED_HOST="${{HOST_IP}}"
sudo mkdir -p /etc/apt/apt.conf.d
echo "Acquire::http::Proxy \"http://${{HOST_IP}}:49503\";" | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
mkdir -p {GUEST_HOME}/.cargo
cat > {GUEST_HOME}/.cargo/config.toml <<CARGOCFG
[source.crates-io]
replace-with = "kellnr-proxy"

[source.kellnr-proxy]
registry = "sparse+http://${{HOST_IP}}:49506/api/v1/cratesio/"
CARGOCFG
"""


class MultipassDriver(RunnerDriver):
    """Runs ephemeral runners as Canonical Multipass VMs -- cross-platform fallback (macOS/Linux/Windows)."""

    is_vm = True

    def __init__(self, image: str = "24.04", store: InstanceStore | None = None):
        """Configure the Ubuntu image (MULTIPASS_IMAGE), VM size (RUNNER_CPUS/RUNNER_MEMORY) and metadata store."""
        self.image = os.getenv("MULTIPASS_IMAGE", image)
        self.cpus = os.getenv("RUNNER_CPUS") or "2"
        self.memory = os.getenv("RUNNER_MEMORY") or "2G"
        self.store = store or InstanceStore(os.path.join(default_state_dir(), "multipass-instances.json"))

    def name(self) -> str:
        """Return this driver's backend identifier: "multipass"."""
        return "multipass"

    def is_available(self) -> bool:
        """True if the `multipass` CLI is on PATH and `multipass version` succeeds."""
        if not shutil.which("multipass"):
            return False
        try:
            res = subprocess.run(["multipass", "version"], capture_output=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _vm_cache_path(container_path: str) -> str:
        """Translate cache destinations from /home/runner to Multipass' /home/ubuntu.

        Autoscaler cache mappings are standardized around runner-container paths.
        Multipass bootstraps the runner under ubuntu, so mirror those paths there.
        """
        if container_path == "/home/runner":
            return GUEST_HOME
        if container_path.startswith("/home/runner/"):
            return container_path.replace("/home/runner/", f"{GUEST_HOME}/", 1)
        return container_path

    def _mount_caches(self, vm_name: str, cache_mounts: dict[str, str]) -> None:
        """Best-effort `multipass mount` of each host cache dir; a failure is a warning, not fatal."""
        for host_path, container_path in cache_mounts.items():
            vm_path = self._vm_cache_path(container_path)
            try:
                prep_cmd = f"sudo mkdir -p {shlex.quote(vm_path)} && sudo chown -R ubuntu:ubuntu {shlex.quote(vm_path)}"
                subprocess.run(["multipass", "exec", vm_name, "--", "bash", "-lc", prep_cmd], check=True, capture_output=True)
                subprocess.run(["multipass", "mount", host_path, f"{vm_name}:{vm_path}"], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.decode(errors="replace") if e.stderr else str(e)
                print(f"[Autoscaler:Multipass] Warning: cache mount failed for {host_path} -> {vm_path}: {stderr}", file=sys.stderr)

    def bootstrap_script(self, vm_name: str, arch: str, runner_url: str, registration_token: str, runner_labels: str, proxies_enabled: bool) -> str:
        """The guest script: deps, runner for `arch`, register + run one job, then power off."""
        return f"""
exec > {GUEST_HOME}/runzero-setup.log 2>&1
{_POWEROFF_TRAP}
set -e
export DEBIAN_FRONTEND=noninteractive
{_PROXY_ENV_BLOCK if proxies_enabled else ""}
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
{runner_download_snippet(arch, home=GUEST_HOME)}
{register_and_run_snippet(runner_url, registration_token, vm_name, runner_labels, home=GUEST_HOME)}
"""

    def spawn_runner(
        self,
        repo: str | None = None,
        org: str | None = None,
        arch: str = "arm64",
        labels: str | None = None,
        access_token: str | None = None,
        cache_mounts: dict[str, str] | None = None,
        proxies_enabled: bool = True,
        extra_env: dict[str, str] | None = None,
        runner_token: str | None = None,
    ) -> str | None:
        """Launch a fresh VM, mount caches, then bootstrap + register the runner in the background.

        `multipass launch` is synchronous; the guest bootstrap (`multipass exec` via Popen) is
        detached, so this returns as soon as the VM is up. Returns None if `arch` isn't the
        host's (Multipass has no emulation), the inputs are invalid, no registration token can
        be obtained, or the launch fails. Not yet verified on a real Multipass host (see #54).
        """
        arch = normalize_arch(arch)
        if arch != host_arch():
            print(f"[Autoscaler:Multipass] Refusing {arch} runner: Multipass only runs {host_arch()} guests on this host.", file=sys.stderr)
            return None
        registration_token = self._prepare_spawn(repo, org, labels, access_token, runner_token, extra_env)
        if not registration_token:
            return None

        target = repo or org or ""
        vm_name = instance_name(NAME_PREFIX, arch, target)
        runner_labels = merge_labels(f"self-hosted,local,multipass,vm,{arch}", labels)
        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}' for {target}...")
        try:
            subprocess.run(
                ["multipass", "launch", self.image, "--name", vm_name, "--cpus", self.cpus, "--memory", self.memory], check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="replace") if e.stderr else str(e)
            print(f"[Autoscaler:Multipass] Error launching VM: {stderr}", file=sys.stderr)
            return None
        self.store.put(vm_name, target=target, arch=arch, created_at=time.time())

        if cache_mounts:
            self._mount_caches(vm_name, cache_mounts)
        script = self.bootstrap_script(vm_name, arch, f"https://github.com/{target}", registration_token, runner_labels, proxies_enabled)
        subprocess.Popen(["multipass", "exec", vm_name, "--", "bash", "-c", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return vm_name

    def list_runners(self) -> list[RunnerInfo]:
        """List RunZero VMs via `multipass list --format json`, with metadata from the instance store.

        Stopped/deleted instances report state "exited" (the guest powers off after its job).
        Returns an empty list (silently) if `multipass list` itself fails.
        """
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            vms = json.loads(res.stdout or "{}").get("list", [])
        except Exception:
            return []
        runners = []
        for vm in vms:
            name = vm.get("name", "")
            if not name.startswith(NAME_PREFIX):
                continue
            status = vm.get("state", "Unknown")
            meta = self.store.get(name)
            arch = meta.get("arch") or ("amd64" if name.startswith(f"{NAME_PREFIX}amd64-") else "arm64")
            runners.append(
                RunnerInfo(
                    id=name,
                    status=status,
                    name=name,
                    state="running" if status.lower() in ("running", "starting") else "exited",
                    target_repo=meta.get("target", ""),
                    target_arch=arch,
                    backend="multipass",
                    created_at=meta.get("created_at"),
                )
            )
        self.store.prune({r.name for r in runners})
        return runners

    def prune_exited(self, runners: list[RunnerInfo]) -> None:
        """Delete-and-purge any `runners` entries that are Multipass-backed and no longer running."""
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                self.destroy_runner(r.id)

    def destroy_runner(self, runner_id: str) -> bool:
        """Delete and purge the named VM (`multipass delete --purge`) and forget its metadata."""
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=True)
        self.store.remove(runner_id)
        return res.returncode == 0

    def cleanup_all(self) -> None:
        """Delete and purge every Multipass-backed runner this driver manages (used on autoscaler shutdown)."""
        for r in self.list_runners():
            self.destroy_runner(r.id)
