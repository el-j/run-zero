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
        # Consecutive build_base_image() failures per arch, and the earliest
        # time (time.monotonic()) the next attempt may start. Without this,
        # a build failure that ISN'T transient (confirmed live: OrbStack's own
        # `orbctl create` failing "machine didn't start in 30s (missing IP
        # address)" for EVERY new VM regardless of arch -- reproduced with a
        # bare `orbctl create`, no run-zero code involved at all, pointing at
        # host/OrbStack network-stack state rather than anything this driver
        # controls) gets retried on every single poll tick (~15-20s) forever:
        # delete the half-built staging VM, recreate it, fail identically,
        # repeat -- burning CPU/OrbStack-daemon load with zero chance of
        # success and no operator-visible signal that this isn't self-healing.
        self._build_failure_counts: Dict[str, int] = {}
        self._build_retry_after: Dict[str, float] = {}
        self._runner_created_at: Dict[str, float] = {}
        self._runner_repos: Dict[str, str] = {}

    def name(self) -> str:
        return "orbstack-vm"

    def is_available(self) -> bool:
        if not shutil.which("orbctl") or not shutil.which("orb"):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, text=True, check=True, timeout=3)
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
                    ["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True, timeout=5
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
        base_name = self.base_image_name(orb_arch)
        names = self._list_vm_names()
        if base_name in names:
            return True

        # Check if an existing -building staging VM was already fully provisioned
        staging_name = f"{base_name}-building"
        if staging_name in names:
            with self._building_lock:
                being_built = orb_arch in self._building_arches
            if not being_built and self._is_staging_provisioned(staging_name):
                print(
                    f"[Autoscaler:OrbStack-VM] Found fully provisioned staging VM '{staging_name}' "
                    f"-- promoting to golden base image '{base_name}'..."
                )
                if self._promote_staging_to_base(staging_name, base_name):
                    return True

        return False

    def _is_staging_provisioned(self, staging_name: str) -> bool:
        """Check if a staging VM completed its full provisioning script."""
        try:
            res = subprocess.run(
                [
                    "orb", "-m", staging_name, "-u", "runner", "bash", "-c",
                    "test -f /home/runner/actions-runner/run.sh || grep -q 'Base image provisioning complete' /home/runner/provision.log 2>/dev/null"
                ],
                capture_output=True, timeout=25
            )
            return res.returncode == 0
        except Exception:
            return False

    def _promote_staging_to_base(self, staging_name: str, base_name: str) -> bool:
        """Atomically promote a completed staging VM to the final golden base image.

        Uses retries and fallback to clone+delete if rename encounters disk or
        OrbStack locking issues.
        """
        self._stop_vm(staging_name)
        # If destination base_name already exists (e.g. stale/broken copy), delete it
        # so renaming doesn't collide with 'destination already exists'.
        if base_name in self._list_vm_names():
            subprocess.run(["orbctl", "delete", "-f", base_name], capture_output=True)

        for attempt in range(5):
            res = subprocess.run(["orbctl", "rename", staging_name, base_name], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[Autoscaler:OrbStack-VM] ✅ Successfully renamed '{staging_name}' to '{base_name}'.")
                return True
            time.sleep(1.0 + attempt * 0.5)

        # Fallback: if rename persistently fails, clone staging_name to base_name, then delete staging_name
        res_clone = subprocess.run(["orbctl", "clone", staging_name, base_name], capture_output=True, text=True)
        if res_clone.returncode == 0:
            subprocess.run(["orbctl", "delete", "-f", staging_name], capture_output=True)
            print(f"[Autoscaler:OrbStack-VM] ✅ Successfully promoted '{staging_name}' to '{base_name}' via clone fallback.")
            return True

        print(
            f"[Autoscaler:OrbStack-VM] Error: Failed to promote '{staging_name}' to '{base_name}' "
            f"after rename attempts and clone fallback.",
            file=sys.stderr
        )
        return False

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

        Builds under a temporary "-building" name and only promotes it
        to the real base_name on full success. This makes the build atomic
        from base_image_exists()'s point of view: that check only looks for
        the exact final name, so it can never see a half-provisioned image.
        """
        script_content = self._read_provision_script()
        if script_content is None:
            return False

        base_name = self.base_image_name(orb_arch)
        if self.base_image_exists(orb_arch):
            print(
                f"[Autoscaler:OrbStack-VM] Golden base image '{base_name}' already exists -- "
                f"skipping build to avoid destroying a working image."
            )
            return True

        staging_name = f"{base_name}-building"
        # If staging_name already exists and completed provisioning, promote it immediately
        if staging_name in self._list_vm_names() and self._is_staging_provisioned(staging_name):
            print(
                f"[Autoscaler:OrbStack-VM] Staging VM '{staging_name}' already completed provisioning "
                f"-- promoting directly to '{base_name}'."
            )
            if self._promote_staging_to_base(staging_name, base_name):
                return True

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

        if not self._promote_staging_to_base(staging_name, base_name):
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
        base itself never needs to be running for that."""
        try:
            res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
            states = {vm.get("name", ""): vm.get("state", "") for vm in json.loads(res.stdout or "[]")}
        except Exception:
            return
        for name, state in states.items():
            if not name.startswith(BASE_IMAGE_PREFIX):
                continue
            is_building_suffix = name.endswith("-building")
            orb_arch = name[len(BASE_IMAGE_PREFIX):].removesuffix("-building")
            with self._building_lock:
                being_built = orb_arch in self._building_arches
            if being_built:
                continue

            base_name = self.base_image_name(orb_arch)

            if is_building_suffix:
                # `being_built` above only reflects builds THIS process instance
                # is actively running. A "-building" VM can outlive that: e.g.
                # the bridge process gets restarted (a normal maintenance
                # operation) while a build's background thread is mid-flight --
                # the thread dies with the old process, but the half-provisioned
                # staging VM it created stays on disk. Confirmed live (2026-08-26):
                # with no live builder, this VM sat as an orphan and this exact
                # loop kept it stuck: `orb -m <stopped> exec ...` implicitly boots
                # a stopped VM as a side effect (confirmed: state flips
                # stopped->running from one exec call), so unconditionally
                # probing it here every poll woke it up only to have the
                # `state == "running"` stop-it branch below shut it down again
                # next tick -- an endless toggle that never let provisioning run
                # long enough to finish.
                if state == "running":
                    # Safe to probe here: this branch only ever sees a VM that
                    # was ALREADY running (not woken by our own probe), so the
                    # exec call below can't itself cause the oscillation above.
                    if self._is_staging_provisioned(name):
                        print(
                            f"[Autoscaler:OrbStack-VM] Idle staging VM '{name}' is already provisioned -- "
                            f"promoting to '{base_name}'."
                        )
                        self._promote_staging_to_base(name, base_name)
                    else:
                        print(
                            f"[Autoscaler:OrbStack-VM] Golden base image '{name}' is running idle -- "
                            f"stopping it to free host resources for job VMs."
                        )
                        self._stop_vm(name)
                else:
                    # Stopped, and no live builder in this process is tracking
                    # it: an orphaned/interrupted build. Resume it rather than
                    # leaving it inert forever -- build_base_image() already
                    # handles "found but not provisioned" by deleting and
                    # re-provisioning cleanly from scratch. Dedup'd and
                    # backoff-gated the same as any other build trigger, so
                    # this can't hot-loop even if the resume keeps failing.
                    print(
                        f"[Autoscaler:OrbStack-VM] Found orphaned staging VM '{name}' with no active "
                        f"builder in this process -- resuming its build."
                    )
                    self._build_base_image_async(orb_arch)
                continue

            if state == "running":
                print(
                    f"[Autoscaler:OrbStack-VM] Golden base image '{name}' is running idle -- "
                    f"stopping it to free host resources for job VMs."
                )
                self._stop_vm(name)

    def _build_cooldown_remaining(self, orb_arch: str) -> float:
        """Seconds until the next build_base_image() attempt for orb_arch is
        allowed, or 0.0 if none is in effect. Caller must hold _building_lock."""
        return max(0.0, self._build_retry_after.get(orb_arch, 0.0) - time.monotonic())

    def _build_base_image_async(self, orb_arch: str) -> None:
        """Kick off build_base_image() on a background thread, deduped per-arch.

        Called from spawn_runner() instead of building in-line so the main
        autoscaler poll loop is never blocked by a golden-image build -- it
        just gets None back this poll and retries on the next one.

        Gated by a per-arch exponential backoff (see __init__'s comment) after
        a failure, so a non-transient condition -- confirmed live: bare
        `orbctl create` failing "machine didn't start in 30s (missing IP
        address)" for EVERY arch, no run-zero code involved at all, pointing
        at host/OrbStack network-stack state -- doesn't retry on every single
        poll tick (~15-20s) forever. Without this, each failed attempt just
        deletes the half-built staging VM and recreates it identically on the
        next poll: guaranteed to fail the same way again, with zero chance of
        self-resolving and no operator-visible signal that it isn't.
        """
        with self._building_lock:
            if orb_arch in self._building_arches:
                return
            if self._build_cooldown_remaining(orb_arch) > 0:
                return
            self._building_arches.add(orb_arch)

        def _run() -> None:
            ok = False
            try:
                ok = self.build_base_image(orb_arch)
            finally:
                with self._building_lock:
                    self._building_arches.discard(orb_arch)
                    if ok:
                        self._build_failure_counts[orb_arch] = 0
                        self._build_retry_after.pop(orb_arch, None)
                    else:
                        failures = self._build_failure_counts.get(orb_arch, 0) + 1
                        self._build_failure_counts[orb_arch] = failures
                        cooldown = min(30 * (2 ** (failures - 1)), 900)
                        self._build_retry_after[orb_arch] = time.monotonic() + cooldown
                        hint = (
                            " This many consecutive failures usually isn't transient -- if "
                            "'orbctl create' is failing with a 'missing IP address' timeout, a "
                            "plain OrbStack app restart often doesn't clear it, but a full host "
                            "reboot usually does (stale macOS virtual-network-extension state "
                            "after long uptime). Verify with a bare `orbctl create -a "
                            f"{orb_arch} ubuntu:24.04 diag-test` outside run-zero before assuming "
                            "this is a run-zero bug."
                            if failures >= 3 else ""
                        )
                        print(
                            f"[Autoscaler:OrbStack-VM] Golden base image build for '{orb_arch}' "
                            f"has now failed {failures} time(s) in a row. Backing off {cooldown}s "
                            f"before retrying.{hint}",
                            file=sys.stderr
                        )

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
                cooldown_remaining = self._build_cooldown_remaining(orb_arch)
            if not already_building and cooldown_remaining <= 0:
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
cleanup() {{
    sudo systemctl poweroff 2>/dev/null || sudo poweroff 2>/dev/null || sudo shutdown -h now 2>/dev/null || true
}}
trap cleanup EXIT
set -e
{reg_and_run}
"""

        try:
            subprocess.run(clone_cmd, check=True, capture_output=True)
            self._runner_created_at[vm_name] = time.time()
            if repo:
                self._runner_repos[vm_name] = repo
            elif org:
                self._runner_repos[vm_name] = org

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
                        state = "pending"
                    else:
                        state = "exited"

                    if name not in self._runner_created_at:
                        self._runner_created_at[name] = time.time()

                    target_repo = self._runner_repos.get(name, "")
                    if not target_repo:
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
                        backend="orbstack-vm",
                        created_at=self._runner_created_at.get(name)
                    ))
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def destroy_runner(self, runner_id: str) -> bool:
        if runner_id.startswith(BASE_IMAGE_PREFIX):
            print(
                f"[Autoscaler:OrbStack-VM] Refusing to delete '{runner_id}' -- it looks like a "
                f"golden base image, not an ephemeral job runner.", file=sys.stderr
            )
            return False
        try:
            subprocess.run(["orbctl", "delete", "-f", runner_id], check=True, capture_output=True)
            self._runner_created_at.pop(runner_id, None)
            self._runner_repos.pop(runner_id, None)
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
