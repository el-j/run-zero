"""
OrbStack Linux VM Execution Driver for RunZero
Spawns and manages dedicated, lightweight Linux Virtual Machines via OrbStack (Apple Virtualization framework).
Provides full systemd, dedicated kernel, internal Docker daemon, unconfined browser sandboxes,
and automatic integration with local caching proxies (Verdaccio, Athens).

Ephemeral job VMs are cloned from a golden base image (`runzero-vm-base-<arch>`, built once via
`make build-vm-base`) rather than fully re-provisioned from scratch on every job -- cloning is a
disk-copy, seconds instead of the several minutes apt/curl/nvm provisioning takes cold. If the base
image doesn't exist yet, spawn_runner() falls back to full cold provisioning so VM routing still
works, just slowly, and tells the operator to build the base image for fast spins.

The actual toolchain (OS packages, .NET, Chrome, Node/nvm, Playwright deps) lives in
docker/provision-toolchain.sh -- the SAME script docker/Dockerfile bakes into the container image,
so the two execution engines can't drift apart on tool versions. Only Docker itself differs
deliberately per engine: the container gets the CLI only (talks to a mounted host socket), this VM
gets a full local daemon (it has no host socket to mount).
"""

import os
import sys
import time
import uuid
import json
import shutil
import subprocess
from typing import List, Dict, Optional
from . import RunnerDriver, RunnerInfo

RUNNER_VERSION = "2.336.0"

# VM names below this prefix are ephemeral, one-per-job instances (managed like any other
# runner: counted, pruned, destroyed). Names starting with BASE_IMAGE_PREFIX are golden
# template images -- never counted as active runners, never pruned/destroyed by the normal
# lifecycle methods.
RUNNER_VM_PREFIX = "runzero-vm-"
BASE_IMAGE_PREFIX = "runzero-vm-base-"


class OrbStackVMDriver(RunnerDriver):
    def __init__(self, distro: str = "ubuntu:22.04"):
        self.distro = os.getenv("ORB_DISTRO", distro)
        # docker/provision-toolchain.sh, resolved relative to this file
        # (src/drivers/orbstack_vm_driver.py -> repo root -> docker/...).
        self._provision_script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "docker", "provision-toolchain.sh"
        )

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

    @staticmethod
    def _docker_engine_snippet() -> str:
        # Full daemon, not just the CLI -- this VM has no host docker.sock to bind-mount like
        # the container driver does, so `services:` containers in a job need a real local
        # daemon here.
        return """
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /tmp/docker.asc
sudo install -m 0644 /tmp/docker.asc /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \\
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker runner
sudo systemctl enable docker
"""

    @staticmethod
    def _runner_download_snippet(orb_arch: str) -> str:
        return f"""
mkdir -p /home/runner/actions-runner && cd /home/runner/actions-runner
RUNNER_ARCH="{orb_arch}"
[ "$RUNNER_ARCH" = "amd64" ] && RUNNER_ARCH="x64"
curl -O -L "https://github.com/actions/runner/releases/download/v{RUNNER_VERSION}/actions-runner-linux-${{RUNNER_ARCH}}-{RUNNER_VERSION}.tar.gz"
tar xzf "./actions-runner-linux-${{RUNNER_ARCH}}-{RUNNER_VERSION}.tar.gz"
rm "./actions-runner-linux-${{RUNNER_ARCH}}-{RUNNER_VERSION}.tar.gz"
sudo ./bin/installdependencies.sh
"""

    @staticmethod
    def _registration_and_run_snippet(
        api_base: str, runner_url: str, access_token: str, vm_name: str, runner_labels: str, proxy_env_block: str
    ) -> str:
        # Mirrors docker/start.sh: exchange the PAT for a short-lived registration token, THEN
        # config.sh (registers with GitHub), THEN a bare run.sh (the listener -- it takes no
        # --unattended/--ephemeral/--name/--labels flags at all; those are config.sh-only.
        # Passing them to run.sh fails immediately with "Not configured", which silently
        # stranded every VM-routed job before this was fixed).
        #
        # `sudo chmod 666 docker.sock`: usermod's docker-group change (baked into the golden
        # image, or done earlier in this same script on the cold-provision path) only takes
        # effect on a FRESH login -- and registration+run.sh execute later in this same
        # continuous session, not a new `orb -m` invocation. Fine for a single-tenant,
        # ephemeral, destroyed-after-one-job VM; not something to do on a persistent machine.
        #
        # Self-shutdown after run.sh exits: an ephemeral runner's process exits after exactly
        # one job, but the VM itself otherwise stays powered on indefinitely -- OrbStack has no
        # concept of "the process inside exited" the way a Docker container does. Powering off
        # transitions the VM to a state prune_exited() already knows how to clean up, so this
        # is the only change needed to stop ephemeral VMs from silently accumulating.
        return f"""
sudo systemctl start docker 2>/dev/null || true
sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
{proxy_env_block}
cd /home/runner/actions-runner

echo "Fetching registration token from GitHub API..."
TOKEN_RESPONSE=$(curl -s -X POST \\
  -H "Authorization: Bearer {access_token}" \\
  -H "Accept: application/vnd.github+json" \\
  -H "X-GitHub-Api-Version: 2022-11-28" \\
  "{api_base}/registration-token")
REG_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.token // empty')
if [ -z "$REG_TOKEN" ] || [ "$REG_TOKEN" = "null" ]; then
  echo "Error: Failed to obtain registration token. Response: $TOKEN_RESPONSE"
  exit 1
fi

./config.sh --url "{runner_url}" --token "$REG_TOKEN" --name "{vm_name}" --work "_work" \\
  --unattended --replace --ephemeral --labels "{runner_labels}"

echo "Starting runner {vm_name}..."
./run.sh

echo "Ephemeral run finished -- powering off so the autoscaler prunes this VM."
sudo shutdown -h now
"""

    def build_base_image(self, orb_arch: str) -> bool:
        """Build (or rebuild) the golden VM image ephemeral job VMs clone from.

        This is the slow path (apt/curl/nvm/.NET/Chrome/Docker-engine install, several
        minutes) -- meant to be run once via `make build-vm-base`, not per job.
        """
        script_content = self._read_provision_script()
        if script_content is None:
            return False

        base_name = self.base_image_name(orb_arch)
        print(f"[Autoscaler:OrbStack-VM] 🏗️  Building golden base image '{base_name}' ({self.distro})...")

        # Replace any existing base image so rebuilds are idempotent
        subprocess.run(["orbctl", "delete", "-f", base_name], capture_output=True)

        try:
            subprocess.run(
                ["orbctl", "create", "-a", orb_arch, "-u", "runner", self.distro, base_name],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating base image: {e.stderr.decode()}", file=sys.stderr)
            return False

        full_script = f"""
exec > /home/runner/provision.log 2>&1
set -e
{self._docker_engine_snippet()}
{script_content}
{self._runner_download_snippet(orb_arch)}
echo "Base image provisioning complete."
"""
        try:
            # provision-toolchain.sh's content is pasted inline (not sourced as a
            # separate file), so its own `$1` reference resolves against THIS
            # `bash -c`'s positional args -- "bash" becomes $0, orb_arch becomes $1.
            result = subprocess.run(
                ["orb", "-m", base_name, "-u", "runner", "bash", "-c", full_script, "bash", orb_arch],
                capture_output=True, timeout=1800
            )
            if result.returncode != 0:
                print(
                    f"[Autoscaler:OrbStack-VM] Base image provisioning failed (exit {result.returncode}). "
                    f"Check /home/runner/provision.log inside '{base_name}' (`orb -m {base_name} cat "
                    f"/home/runner/provision.log`) for details.", file=sys.stderr
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
            default_labels = "self-hosted,local,vm,x64,amd64"

        runner_labels = labels if labels else default_labels
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        proxy_env_block = ""
        if proxies_enabled:
            proxy_env_block = """
export NPM_CONFIG_REGISTRY="http://host.orb.internal:49501/"
export GOPROXY="http://host.orb.internal:49500,https://proxy.golang.org,direct"
"""

        if repo:
            api_base = f"https://api.github.com/repos/{repo}/actions/runners"
            runner_url = f"https://github.com/{repo}"
        else:
            api_base = f"https://api.github.com/orgs/{org}/actions/runners"
            runner_url = f"https://github.com/{org}"

        base_name = self.base_image_name(orb_arch)
        use_base_image = self.base_image_exists(orb_arch)

        reg_and_run = self._registration_and_run_snippet(
            api_base, runner_url, access_token or "", vm_name, runner_labels, proxy_env_block
        )

        if use_base_image:
            print(
                f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' "
                f"(cloned from golden image '{base_name}')..."
            )
            clone_cmd = ["orbctl", "clone", base_name, vm_name]
            setup_script = f"""
exec > /home/runner/setup.log 2>&1
set -e
{reg_and_run}
"""
        else:
            print(
                f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' "
                f"({self.distro}) -- no golden base image found, cold-provisioning from scratch "
                f"(several minutes). Run `make build-vm-base` once for near-instant spins."
            )
            script_content = self._read_provision_script()
            if script_content is None:
                return None
            clone_cmd = ["orbctl", "create", "-a", orb_arch, "-u", "runner", self.distro, vm_name]
            setup_script = f"""
exec > /home/runner/setup.log 2>&1
set -e
{self._docker_engine_snippet()}
{script_content}
{self._runner_download_snippet(orb_arch)}
{reg_and_run}
"""

        try:
            subprocess.run(clone_cmd, check=True, capture_output=True)
            # orb_arch as a positional arg: only load-bearing on the cold-provision
            # path (provision-toolchain.sh's content is inlined there and reads its
            # own $1), harmless no-op on the fast clone path -- see build_base_image.
            subprocess.Popen(
                ["orb", "-m", vm_name, "-u", "runner", "bash", "-c", setup_script, "bash", orb_arch],
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
                # Golden base images are templates, not runner instances -- never counted
                # toward active runners, never pruned/destroyed by the normal lifecycle.
                if name.startswith(RUNNER_VM_PREFIX) and not name.startswith(BASE_IMAGE_PREFIX):
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
