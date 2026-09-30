"""
Canonical Multipass VM Execution Driver for RunZero
Cross-platform VM execution for macOS, Linux, and Windows using lightweight QEMU/Hyper-V/VirtualBox VMs,
with automatic integration with local caching proxies (Verdaccio, Athens).
"""

import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import uuid

from . import RunnerDriver, RunnerInfo, merge_labels


class MultipassDriver(RunnerDriver):
    """Runs ephemeral runners as Canonical Multipass VMs -- cross-platform fallback (macOS/Linux/Windows)."""

    is_vm = True

    def __init__(self, image: str = "24.04"):
        """Configure the Multipass base image (falls back to the MULTIPASS_IMAGE env var)."""
        self.image = os.getenv("MULTIPASS_IMAGE", image)
        self._runner_created_at: dict[str, float] = {}

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
            return "/home/ubuntu"
        if container_path.startswith("/home/runner/"):
            return container_path.replace("/home/runner/", "/home/ubuntu/", 1)
        return container_path

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
        """Launch a fresh Multipass VM (`multipass launch`) and bootstrap+register the runner inside it.

        The launch itself is synchronous; the apt-get/runner-download/registration bootstrap script
        runs detached (`multipass exec` via Popen) so this call returns as soon as the VM boots.
        Returns None (and prints to stderr) only if the `multipass launch` step itself fails.
        """
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"runzero-mp-{arch}{name_suffix}-{unique_id}"
        runner_labels = merge_labels(f"self-hosted,local,multipass,vm,{arch}", labels)
        registration_token = self._prepare_spawn(repo, org, labels, access_token, runner_token, extra_env)
        if not registration_token:
            return None
        register = (
            f"./config.sh --unattended --replace --ephemeral --url {shlex.quote(f'https://github.com/{repo or org}')} "
            f"--token {shlex.quote(registration_token)} --name {shlex.quote(vm_name)} --labels {shlex.quote(runner_labels)}"
        )

        proxy_env_block = ""
        if proxies_enabled:
            proxy_env_block = """
HOST_IP=$(ip route | awk '/default/ { print $3 }' || echo "192.168.64.1")
export NPM_CONFIG_REGISTRY="http://${HOST_IP}:49501/"
export YARN_REGISTRY="http://${HOST_IP}:49501/"
export GOPROXY="http://${HOST_IP}:49500,https://proxy.golang.org,direct"
export PIP_INDEX_URL="http://${HOST_IP}:49507/root/pypi/+simple/"
export UV_INDEX_URL="${PIP_INDEX_URL}"
export PIP_TRUSTED_HOST="${HOST_IP}"
sudo mkdir -p /etc/apt/apt.conf.d
echo "Acquire::http::Proxy \"http://${HOST_IP}:49503\";" | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
mkdir -p /home/ubuntu/.cargo
cat > /home/ubuntu/.cargo/config.toml <<CARGOCFG
[source.crates-io]
replace-with = "kellnr-proxy"

[source.kellnr-proxy]
registry = "sparse+http://${HOST_IP}:49506/api/v1/cratesio/"
CARGOCFG
"""

        print(f"[Autoscaler:Multipass] 🚀 Launching ephemeral VM '{vm_name}' with caching proxies...")

        try:
            # 1. Launch instance
            subprocess.run(["multipass", "launch", self.image, "--name", vm_name, "--cpus", "2", "--memory", "2G"], check=True, capture_output=True)
            self._runner_created_at[vm_name] = time.time()

            # 2. Best-effort mount host caches into VM so tool/cache directories persist across jobs.
            if cache_mounts:
                for host_path, container_path in cache_mounts.items():
                    vm_path = self._vm_cache_path(container_path)
                    try:
                        prep_cmd = f"sudo mkdir -p {shlex.quote(vm_path)} && sudo chown -R ubuntu:ubuntu {shlex.quote(vm_path)}"
                        subprocess.run(
                            ["multipass", "exec", vm_name, "--", "bash", "-lc", prep_cmd],
                            check=True,
                            capture_output=True,
                        )
                        subprocess.run(
                            ["multipass", "mount", host_path, f"{vm_name}:{vm_path}"],
                            check=True,
                            capture_output=True,
                        )
                    except subprocess.CalledProcessError as e:
                        stderr = e.stderr.decode(errors="replace") if e.stderr else str(e)
                        print(
                            f"[Autoscaler:Multipass] Warning: cache mount failed for {host_path} -> {vm_path}: {stderr}",
                            file=sys.stderr,
                        )

            # 3. Run bootstrap script inside the VM
            setup_script = f"""
export DEBIAN_FRONTEND=noninteractive
{proxy_env_block}
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner
curl -O -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-linux-arm64-2.336.0.tar.gz
tar xzf ./actions-runner-linux-arm64-2.336.0.tar.gz
sudo ./bin/installdependencies.sh
{register}
nohup ./run.sh > /home/ubuntu/runner.log 2>&1 &
"""
            subprocess.Popen(["multipass", "exec", vm_name, "--", "bash", "-c", setup_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return vm_name

        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:Multipass] Error launching VM: {e.stderr.decode()}", file=sys.stderr)
            return None

    def list_runners(self) -> list[RunnerInfo]:
        """List VMs whose name starts with "runzero-mp-" via `multipass list --format json`.

        Returns an empty list (silently) if the `multipass list` call itself fails.
        """
        try:
            res = subprocess.run(["multipass", "list", "--format", "json"], capture_output=True, text=True, check=True)
            data = json.loads(res.stdout or "{}")
            list_vms = data.get("list", [])
            runners = []
            for vm in list_vms:
                name = vm.get("name", "")
                if name.startswith("runzero-mp-"):
                    status = vm.get("state", "Running")
                    state = "running" if status.lower() == "running" else "exited"
                    if name not in self._runner_created_at:
                        self._runner_created_at[name] = time.time()
                    runners.append(
                        RunnerInfo(
                            id=name,
                            status=status,
                            name=name,
                            state=state,
                            target_repo="",
                            target_arch="arm64",
                            backend="multipass",
                            created_at=self._runner_created_at.get(name),
                        )
                    )
            return runners
        except Exception:
            return []

    def prune_exited(self, runners: list[RunnerInfo]) -> None:
        """Delete-and-purge any `runners` entries that are Multipass-backed and in a stopped state."""
        for r in runners:
            if r.backend == "multipass" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:Multipass] Deleting stopped VM: {r.name}")
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)

    def destroy_runner(self, runner_id: str) -> bool:
        """Delete and purge the named VM via `multipass delete --purge`."""
        res = subprocess.run(["multipass", "delete", "--purge", runner_id], capture_output=True)
        return res.returncode == 0

    def cleanup_all(self) -> None:
        """Delete and purge every Multipass-backed runner this driver manages (used on autoscaler shutdown)."""
        runners = self.list_runners()
        for r in runners:
            if r.backend == "multipass":
                subprocess.run(["multipass", "delete", "--purge", r.name], capture_output=True)
