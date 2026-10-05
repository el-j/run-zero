"""
Windows WSL2 Virtual Machine Driver for RunZero
Enables native lightweight Linux VM execution for GitHub Actions on Windows 10/11 & Windows Server,
with automatic integration with local caching proxies (Verdaccio, Athens, devpi, kellnr, apt-cacher-ng).

Each runner gets an ephemeral instance with an isolated actions-runner installation, registers
one runner with a host-issued registration token, runs one job and cleans itself up.
Repository, architecture, and creation timestamps are persisted host-side in an InstanceStore.
Host package cache paths are translated to WSL2 /mnt/<drive>/... mounts.
"""

import os
import shlex
import shutil
import subprocess
import sys
import time

from . import RunnerDriver, RunnerInfo, merge_labels
from .instance_store import InstanceStore, default_state_dir
from .orbstack_templates import cache_mount_snippet
from .runner_bootstrap import (
    host_arch,
    instance_name,
    normalize_arch,
    register_and_run_snippet,
    runner_download_snippet,
    windows_to_wsl_path,
)
from .runner_env import cache_env, export_block, registry_env

NAME_PREFIX = "runzero-wsl-"
GUEST_HOME = "/home/runner"


class WSL2Driver(RunnerDriver):
    """Runs ephemeral runners as processes inside a WSL2 Linux distro, for the Windows host case."""

    is_vm = True

    def __init__(
        self,
        distro_base: str = "Ubuntu-24.04",
        base_tarball: str | None = None,
        store: InstanceStore | None = None,
    ):
        """Configure which WSL distro to run jobs in (falls back to the WSL_DISTRO_BASE env var)."""
        self.distro_base = os.getenv("WSL_DISTRO_BASE", distro_base)
        self.base_tarball = os.getenv("WSL_BASE_TARBALL") or base_tarball
        self.store = store or InstanceStore(os.path.join(default_state_dir(), "wsl-instances.json"))
        self.wsl_dir = os.getenv("WSL_RUNNER_DIR") or os.path.join(default_state_dir(), "wsl")
        self._runner_created_at: dict[str, float] = {}

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

    @staticmethod
    def _proxy_env_block() -> str:
        """Generate shell script block configuring package manager proxies inside the WSL2 guest."""
        return (
            """
HOST_IP=$(ip route show default 2>/dev/null | awk '{print $3}' || echo "localhost")
"""
            + export_block(registry_env("http://${HOST_IP}:49501/"), expand=True)
            + """
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
        )

    def bootstrap_script(
        self,
        vm_name: str,
        arch: str,
        runner_url: str,
        registration_token: str,
        runner_labels: str,
        proxies_enabled: bool,
        cache_mounts: dict[str, str] | None = None,
        runner_home: str = GUEST_HOME,
    ) -> str:
        """The guest script: deps, proxy env, cache mounts, runner for arch, register + run one job, then finish."""
        cache_block = cache_mount_snippet(cache_mounts, host_to_guest=windows_to_wsl_path) if cache_mounts else ""
        finish = f"rm -rf {shlex.quote(runner_home)}" if runner_home != GUEST_HOME else ""
        return f"""
exec > {runner_home}/runzero-setup.log 2>&1
set -e
export DEBIAN_FRONTEND=noninteractive
{self._proxy_env_block() if proxies_enabled else ""}
{cache_block}
sudo apt-get update -y && sudo apt-get install -y curl jq git git-lfs ca-certificates build-essential
{runner_download_snippet(arch, home=runner_home)}
{register_and_run_snippet(runner_url, registration_token, vm_name, runner_labels, home=runner_home, finish=finish, env=cache_env(bool(cache_mounts)))}
"""

    def spawn_runner(
        self,
        repo: str | None = None,
        org: str | None = None,
        arch: str | None = None,
        labels: str | None = None,
        access_token: str | None = None,
        cache_mounts: dict[str, str] | None = None,
        proxies_enabled: bool = True,
        extra_env: dict[str, str] | None = None,
        runner_token: str | None = None,
    ) -> str | None:
        """Launch an ephemeral runner inside WSL2 and return its instance name."""
        resolved_arch = normalize_arch(arch) if arch else host_arch()
        if resolved_arch != host_arch():
            print(f"[Autoscaler:WSL2] Refusing {resolved_arch} runner: WSL2 only runs {host_arch()} guests on this host.", file=sys.stderr)
            return None

        registration_token = self._prepare_spawn(repo, org, labels, access_token, runner_token, extra_env)
        if not registration_token:
            return None

        target = repo or org or ""
        vm_name = instance_name(NAME_PREFIX, resolved_arch, target)
        runner_labels = merge_labels(f"self-hosted,local,wsl,vm,{resolved_arch},windows-host", labels)

        target_distro = self.distro_base
        runner_home = f"{GUEST_HOME}/{vm_name}"
        if self.base_tarball:
            target_distro = vm_name
            runner_home = GUEST_HOME
            install_path = os.path.join(self.wsl_dir, vm_name)
            os.makedirs(install_path, exist_ok=True)
            try:
                subprocess.run(["wsl", "--import", vm_name, install_path, self.base_tarball], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.decode(errors="replace") if e.stderr else str(e)
                print(f"[Autoscaler:WSL2] Error importing WSL distro: {stderr}", file=sys.stderr)
                return None

        script = self.bootstrap_script(
            vm_name=vm_name,
            arch=resolved_arch,
            runner_url=f"https://github.com/{target}",
            registration_token=registration_token,
            runner_labels=runner_labels,
            proxies_enabled=proxies_enabled,
            cache_mounts=cache_mounts,
            runner_home=runner_home,
        )

        print(f"[Autoscaler:WSL2] 🚀 Spawning ephemeral WSL2 runner '{vm_name}' for {target} with caching proxies...")
        try:
            cmd = [
                "wsl",
                "-d",
                target_distro,
                "-u",
                "runner",
                "--",
                "bash",
                "-c",
                script,
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._runner_created_at[vm_name] = time.time()
            self.store.put(vm_name, target=target, arch=resolved_arch, created_at=time.time())
            return vm_name
        except Exception as e:
            print(f"[Autoscaler:WSL2] Error launching WSL runner: {e}", file=sys.stderr)
            return None

    def list_runners(self) -> list[RunnerInfo]:
        """List registered WSL distro names (via `wsl --list --quiet`) starting with "runzero-wsl"."""
        try:
            res = subprocess.run(["wsl", "--list", "--quiet"], capture_output=True, text=True, check=True)
            lines = [line.strip().replace("\x00", "").replace("\r", "") for line in res.stdout.split("\n") if line.strip()]
            distro_names = set(lines)
        except Exception:
            return []

        runners = []
        for name in distro_names:
            if not name.startswith(NAME_PREFIX):
                continue
            meta = self.store.get(name)
            arch = meta.get("arch") or ("arm64" if name.startswith(f"{NAME_PREFIX}arm64-") else "amd64")
            created_at = meta.get("created_at") or self._runner_created_at.get(name)
            runners.append(
                RunnerInfo(
                    id=name,
                    status="running",
                    name=name,
                    state="running",
                    target_repo=meta.get("target", ""),
                    target_arch=arch,
                    backend="wsl2",
                    created_at=created_at,
                )
            )
        self.store.prune({r.name for r in runners})
        return runners

    def prune_exited(self, runners: list[RunnerInfo]) -> None:
        """Terminate any `runners` entries that are WSL2-backed and in "exited"/"stopped"/"dead" state."""
        for r in runners:
            if r.backend == "wsl2" and r.state in ("exited", "stopped", "dead"):
                print(f"[Autoscaler:WSL2] Terminating exited runner: {r.name}")
                self.destroy_runner(r.id)

    def destroy_runner(self, runner_id: str) -> bool:
        """Terminate the named WSL distro instance via `wsl --terminate`."""
        try:
            res = subprocess.run(["wsl", "--terminate", runner_id], capture_output=True, timeout=10)
            if self.base_tarball:
                subprocess.run(["wsl", "--unregister", runner_id], capture_output=True, timeout=10)
            self.store.remove(runner_id)
            self._runner_created_at.pop(runner_id, None)
            return res.returncode == 0
        except Exception as e:
            print(f"[Autoscaler:WSL2] Error destroying runner {runner_id}: {e}", file=sys.stderr)
            return False

    def cleanup_all(self) -> None:
        """Terminate every WSL2-backed runner this driver manages (used on autoscaler shutdown)."""
        runners = self.list_runners()
        for r in runners:
            if r.backend == "wsl2":
                self.destroy_runner(r.id)
