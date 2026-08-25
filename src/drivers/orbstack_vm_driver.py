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
import threading
import time
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
        # main()'s poll loop is single-threaded and synchronous -- a golden-image
        # build blocking in-line here used to freeze the ENTIRE autoscaler (every
        # repo, both engines) for up to 30 minutes on the first VM-routed job
        # after this image goes missing (fresh checkout, `make vm-clean-all`, a
        # new arch). Building in a background thread lets spawn_runner() return
        # None (skip this poll, retry later) so Docker-engine jobs and other
        # repos keep flowing while the one-time build finishes.
        self._building_lock = threading.Lock()
        self._building_arches: set = set()

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
        # Retried because a single transient "orbctl list" failure (CLI busy while
        # another orbctl/orb command is mid-flight, momentary daemon hiccup, etc.)
        # used to be indistinguishable from "no VMs exist at all". That false
        # negative fed straight into base_image_exists() -> False, which triggered
        # build_base_image() to unconditionally `orbctl delete -f` and rebuild a
        # perfectly healthy golden image from scratch (confirmed happening live).
        last_err: Optional[Exception] = None
        for attempt in range(3):
            try:
                res = subprocess.run(
                    ["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True
                )
                vms = json.loads(res.stdout or "[]")
                return [vm.get("name", "") for vm in vms]
            except Exception as e:
                last_err = e
                if attempt < 2:
                    time.sleep(0.5)
        print(f"[Autoscaler:OrbStack-VM] Warning: 'orbctl list' failed after retries: {last_err}", file=sys.stderr)
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
        """Build the golden VM image ephemeral job VMs clone from.

        Builds under a temporary "-building" name and only `orbctl rename`s it
        to the real base_name on full success. This makes the build atomic
        from base_image_exists()'s point of view: that check only looks for
        the exact final name, so it can never see a half-provisioned image.
        Without this, an interruption partway through provisioning (process
        killed, `make restart` landing mid-build, a host reboot) left a VM
        already sitting under the final name but missing everything after
        wherever it got cut off -- confirmed live: a base image interrupted
        mid-build was left without /home/runner/actions-runner ever created,
        base_image_exists() reported it "ready" forever after (it only checks
        the VM exists, not that provisioning finished), and every single job
        VM cloned from it died in seconds hitting `cd
        /home/runner/actions-runner: No such file or directory` -- exactly
        the churn loop this replaces.

        Never rebuilds/deletes an image that's already there under the final
        name -- see the retry comment on _list_vm_names(). If you genuinely
        need to force a rebuild, delete the image explicitly first (`make
        vm-clean-all` / `orbctl delete -f <base_name>`) rather than relying on
        this function to do it for you.
        """
        base_name = self.base_image_name(orb_arch)
        if self.base_image_exists(orb_arch):
            print(
                f"[Autoscaler:OrbStack-VM] Golden base image '{base_name}' already exists -- "
                f"skipping build to avoid destroying a working image."
            )
            return True

        script_content = self._read_provision_script()
        if script_content is None:
            return False

        staging_name = f"{base_name}-building"
        print(f"[Autoscaler:OrbStack-VM] 🏗️  Building golden base image '{base_name}' ({self.distro})...")

        try:
            subprocess.run(["orbctl", "delete", "-f", staging_name], capture_output=True)
            subprocess.run(
                ["orbctl", "create", "-a", orb_arch, "-u", "runner", self.distro, staging_name],
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
                ["orb", "-m", staging_name, "-u", "runner", "bash", "-c", full_script],
                capture_output=True, timeout=1800
            )
            if result.returncode != 0:
                print(
                    f"[Autoscaler:OrbStack-VM] Base image provisioning failed (exit {result.returncode}). "
                    f"Check /home/runner/provision.log inside '{staging_name}' for details.", file=sys.stderr
                )
                return False
        except subprocess.TimeoutExpired:
            print("[Autoscaler:OrbStack-VM] Base image provisioning timed out after 30 minutes.", file=sys.stderr)
            return False

        self._stop_vm(staging_name)
        try:
            subprocess.run(["orbctl", "rename", staging_name, base_name], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            print(
                f"[Autoscaler:OrbStack-VM] Provisioning succeeded but renaming '{staging_name}' to "
                f"'{base_name}' failed: {stderr}", file=sys.stderr
            )
            return False
        print(f"[Autoscaler:OrbStack-VM] ✅ Golden base image '{base_name}' ready. Future spawns will clone it.")
        return True

    def _stop_vm(self, vm_name: str) -> bool:
        """Stop a VM and verify it actually reached 'stopped', retrying a few
        times. A fire-and-forget `orbctl stop` here previously left the golden
        image running indefinitely -- burning host CPU/RAM for a VM that
        nothing was using -- any time the stop command didn't land cleanly."""
        for attempt in range(3):
            subprocess.run(["orbctl", "stop", vm_name], capture_output=True)
            for _ in range(10):
                names_and_states = {}
                try:
                    res = subprocess.run(
                        ["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True
                    )
                    for vm in json.loads(res.stdout or "[]"):
                        names_and_states[vm.get("name", "")] = vm.get("state", "")
                except Exception:
                    pass
                if names_and_states.get(vm_name, "stopped") == "stopped":
                    return True
                time.sleep(1)
        print(
            f"[Autoscaler:OrbStack-VM] Warning: '{vm_name}' did not confirm stopped after "
            f"repeated attempts -- it may still be running and consuming host resources.",
            file=sys.stderr
        )
        return False

    def ensure_base_images_stopped(self) -> None:
        """Stop any golden base image caught running while not actively being
        built. Ephemeral job VMs clone from the base's on-disk snapshot; the
        base itself never needs to be running for that. Anything that leaves
        it running (a manual `make build-vm-base`, a stop that didn't land, a
        host/OrbStack restart resuming it) just sits there burning CPU/RAM for
        no reason, competing with the very job VMs it's supposed to serve."""
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            states = {vm.get("name", ""): vm.get("state", "") for vm in json.loads(res.stdout or "[]")}
        except Exception:
            return
        for name, state in states.items():
            if not name.startswith(BASE_IMAGE_PREFIX) or state != "running":
                continue
            # Staging VMs ("<base_name>-building") are legitimately running for
            # the whole 15-25 min provisioning window -- strip the suffix so
            # they're matched against _building_arches the same as the final
            # name would be, or this stops the build out from under itself.
            orb_arch = name[len(BASE_IMAGE_PREFIX):]
            orb_arch = orb_arch.removesuffix("-building")
            with self._building_lock:
                being_built = orb_arch in self._building_arches
            if being_built:
                continue
            print(
                f"[Autoscaler:OrbStack-VM] Golden base image '{name}' is running idle -- "
                f"stopping it to free host resources for job VMs."
            )
            self._stop_vm(name)

    def _build_base_image_async(self, orb_arch: str) -> None:
        """Kick off build_base_image() on a background thread, deduped per-arch.

        Called from spawn_runner() instead of building in-line so the main
        autoscaler poll loop is never blocked by a golden-image build -- it
        just gets None back this poll and retries on the next one.
        """
        with self._building_lock:
            if orb_arch in self._building_arches:
                return
            self._building_arches.add(orb_arch)

        def _run() -> None:
            try:
                self.build_base_image(orb_arch)
            finally:
                with self._building_lock:
                    self._building_arches.discard(orb_arch)

        threading.Thread(target=_run, name=f"runzero-build-base-{orb_arch}", daemon=True).start()

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
            with self._building_lock:
                already_building = orb_arch in self._building_arches
            if not already_building:
                print(
                    f"[Autoscaler:OrbStack-VM] 🏗️  Golden base image '{base_name}' not found. "
                    f"Building it in the background (one-time setup, ~15-25 min) -- "
                    f"other repos/engines keep being served meanwhile. This job's "
                    f"VM will be spawned on a later poll once the image is ready."
                )
                self._build_base_image_async(orb_arch)
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
                    elif status_lower in ("creating", "provisioning", "starting"):
                        # Transient startup states, NOT a terminal/prunable state --
                        # misclassifying these as "exited" undercounts genuinely
                        # in-flight VMs in main()'s active-runner tally, causing it
                        # to spawn a duplicate for the same job before the first one
                        # finishes booting (confirmed live: 3 runners registered for
                        # one real queued job, the 2 losers idle forever since
                        # ephemeral runners only self-terminate after completing a
                        # job, never just for being unclaimed).
                        #
                        # "starting" was missing from this list and caused a much
                        # worse variant of the same bug: prune_exited() force-deletes
                        # anything classified "exited", so a VM caught mid-boot in
                        # "starting" wasn't just undercounted, it was destroyed
                        # outright before it could finish registering -- the job
                        # never ran, the autoscaler saw it still queued next poll,
                        # and spawned a fresh clone into the same fate. Confirmed
                        # live via `orbctl list` polled every 2s during a real clone
                        # boot. amd64-under-Rosetta boots slow enough that this
                        # "starting" window reliably spans a full poll tick, whereas
                        # native arm64 usually cleared it before the next poll --
                        # which is exactly why this got much more visible once
                        # amd64 became the default arch for unlabeled jobs.
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
        # Belt-and-suspenders: list_runners() already excludes base images so
        # prune_exited()/cleanup_all() never see one to pass in here, but this
        # guard makes it structurally impossible for *any* caller (present or
        # future) to delete the golden image through this single delete
        # chokepoint. Rebuilding it costs 15-25 min; nothing that walks
        # already-finished/exited job runners should ever be able to touch it.
        if runner_id.startswith(BASE_IMAGE_PREFIX):
            print(
                f"[Autoscaler:OrbStack-VM] Refusing to delete '{runner_id}' -- it looks like a "
                f"golden base image, not an ephemeral job runner.", file=sys.stderr
            )
            return False
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
