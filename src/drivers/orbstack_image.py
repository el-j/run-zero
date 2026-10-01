"""
Golden base-image lifecycle for the OrbStack VM driver.

Ephemeral job VMs are `orbctl clone`s of a per-arch "golden" base VM that already has Docker,
the language toolchains and the Actions runner installed (docker/provision-toolchain.sh).
`OrbStackImageBuilder` builds that image under a "-building" staging name and atomically
promotes it on success, stops the base image whenever it is found running idle, and resumes
builds orphaned by a process restart. Build dedup/backoff is the driver's shared
`BuildBackoff`; the driver itself only clones, lists and destroys job VMs.
"""

import json
import os
import subprocess
import sys
import time
from collections.abc import Callable

from .backoff import BuildBackoff
from .orbstack_templates import docker_engine_snippet
from .runner_bootstrap import RUNNER_VERSION, runner_download_snippet

BASE_IMAGE_PREFIX = "runzero-vm-base-"

DEFAULT_PROVISION_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docker", "provision-toolchain.sh")


class OrbStackImageBuilder:
    """Builds, promotes and parks the per-arch golden base VMs job VMs are cloned from."""

    def __init__(
        self,
        distro: str,
        backoff: BuildBackoff,
        list_vm_names: Callable[[], list[str]],
        report_event: Callable[[str, str, str], None],
        resume_build: Callable[[str], None],
    ):
        """Bind the base distro, the shared build backoff and the driver's hooks.

        `list_vm_names`, `report_event(status, arch, detail)` and `resume_build(arch)` are
        callbacks into the owning driver (VM listing with retries, dashboard build events,
        and its async, backoff-gated build trigger).
        """
        self.distro = distro
        # Per-VM CPU/memory ceiling, forwarded to `orbctl create` (see build_base_image()).
        # `orbctl clone` has no resource flags of its own -- "the new machine will have all
        # the data and settings from the old machine" -- so every job VM cloned from the
        # golden base image inherits whatever was set here at create time. Left unset by
        # default (unlimited, OrbStack's own default); without it, MAX_RUNNERS concurrent VMs
        # can each claim the full host core/RAM count, which is exactly what starved a real
        # CI run's vitest workers into false 20s test timeouts and one outright "Failed to
        # start forks worker" crash (observed 2026-09-22 on el-j/herbful run 35768507392) --
        # set these once host capacity is known so MAX_RUNNERS * RUNNER_CPUS stays within
        # the host's real core count.
        self.runner_cpus = os.getenv("RUNNER_CPUS") or None
        self.runner_memory = os.getenv("RUNNER_MEMORY") or None
        self._provision_script_path = DEFAULT_PROVISION_SCRIPT
        self._backoff = backoff
        self._list_vm_names = list_vm_names
        self._report_image_event = report_event
        self._build_base_image_async = resume_build

    @staticmethod
    def base_image_name(orb_arch: str) -> str:
        """Return the golden base image's VM name for a given OrbStack arch (e.g. "arm64" -> "runzero-vm-base-arm64")."""
        return f"{BASE_IMAGE_PREFIX}{orb_arch}"

    def base_image_exists(self, orb_arch: str) -> bool:
        """True if the golden base image VM exists for `orb_arch`.

        Also opportunistically promotes a fully-provisioned "-building" staging VM to the
        final base image if one is found (self-heals a build that finished but never got
        renamed, e.g. after a process restart mid-build).
        """
        base_name = self.base_image_name(orb_arch)
        names = self._list_vm_names()
        if base_name in names:
            return True

        # Check if an existing -building staging VM was already fully provisioned
        staging_name = f"{base_name}-building"
        if staging_name in names:
            with self._backoff.lock:
                being_built = orb_arch in self._backoff.in_progress
            if not being_built and self._is_staging_provisioned(staging_name):
                print(f"[Autoscaler:OrbStack-VM] Found fully provisioned staging VM '{staging_name}' -- promoting to golden base image '{base_name}'...")
                if self._promote_staging_to_base(staging_name, base_name):
                    return True

        return False

    def _is_staging_provisioned(self, staging_name: str) -> bool:
        """Check if a staging VM completed its full provisioning script."""
        try:
            res = subprocess.run(
                [
                    "orb",
                    "-m",
                    staging_name,
                    "-u",
                    "runner",
                    "bash",
                    "-c",
                    "test -f /home/runner/actions-runner/run.sh || grep -q 'Base image provisioning complete' /home/runner/provision.log 2>/dev/null",
                ],
                capture_output=True,
                timeout=25,
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

        print(f"[Autoscaler:OrbStack-VM] Error: Failed to promote '{staging_name}' to '{base_name}' after rename attempts and clone fallback.", file=sys.stderr)
        return False

    def _read_provision_script(self) -> str | None:
        """Read provision script from disk or return None if file does not exist."""
        if not os.path.isfile(self._provision_script_path):
            print(f"[Autoscaler:OrbStack-VM] Error: shared provisioning script not found at {self._provision_script_path}", file=sys.stderr)
            return None
        with open(self._provision_script_path) as f:
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
            print(f"[Autoscaler:OrbStack-VM] Golden base image '{base_name}' already exists -- skipping build to avoid destroying a working image.")
            self._report_image_event("ready", orb_arch, "Already built -- skipping.")
            return True

        staging_name = f"{base_name}-building"
        # If staging_name already exists and completed provisioning, promote it immediately
        if staging_name in self._list_vm_names() and self._is_staging_provisioned(staging_name):
            print(f"[Autoscaler:OrbStack-VM] Staging VM '{staging_name}' already completed provisioning -- promoting directly to '{base_name}'.")
            if self._promote_staging_to_base(staging_name, base_name):
                self._report_image_event("ready", orb_arch, "Promoted completed staging VM.")
                return True

        print(f"[Autoscaler:OrbStack-VM] 🏗️  Building golden base image '{base_name}' ({self.distro})...")
        self._report_image_event("building", orb_arch, f"Building '{base_name}' ({self.distro})...")

        create_cmd = ["orbctl", "create", "-a", orb_arch, "-u", "runner"]
        if self.runner_cpus:
            create_cmd.extend(["--cpus", self.runner_cpus])
        if self.runner_memory:
            create_cmd.extend(["--memory", self.runner_memory])
        create_cmd.extend([self.distro, staging_name])

        try:
            subprocess.run(["orbctl", "delete", "-f", staging_name], capture_output=True)
            subprocess.run(create_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            print(f"[Autoscaler:OrbStack-VM] Error creating base image: {stderr}", file=sys.stderr)
            self._report_image_event("failed", orb_arch, f"Error creating base image: {stderr}")
            return False
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error creating base image: {e}", file=sys.stderr)
            self._report_image_event("failed", orb_arch, f"Error creating base image: {e}")
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
            result = subprocess.run(["orb", "-m", staging_name, "-u", "runner", "bash", "-c", full_script], capture_output=True, timeout=1800)
            if result.returncode != 0:
                detail = f"Base image provisioning failed (exit {result.returncode}). Check /home/runner/provision.log inside '{staging_name}' for details."
                print(f"[Autoscaler:OrbStack-VM] {detail}", file=sys.stderr)
                self._report_image_event("failed", orb_arch, detail)
                return False
        except subprocess.TimeoutExpired:
            detail = "Base image provisioning timed out after 30 minutes."
            print(f"[Autoscaler:OrbStack-VM] {detail}", file=sys.stderr)
            self._report_image_event("failed", orb_arch, detail)
            return False

        if not self._promote_staging_to_base(staging_name, base_name):
            self._report_image_event("failed", orb_arch, "Failed to promote staging VM to base image.")
            return False

        print(f"[Autoscaler:OrbStack-VM] ✅ Golden base image '{base_name}' ready. Future spawns will clone it.")
        self._report_image_event("ready", orb_arch, "Build succeeded.")
        return True

    def _stop_vm(self, vm_name: str) -> bool:
        """Stop a VM and verify it actually reached 'stopped', retrying a few
        times. A fire-and-forget `orbctl stop` here previously left the golden
        image running indefinitely -- burning host CPU/RAM for a VM that
        nothing was using -- any time the stop command didn't land cleanly."""
        for _attempt in range(3):
            subprocess.run(["orbctl", "stop", vm_name], capture_output=True)
            for _ in range(10):
                try:
                    res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True)
                    names_and_states = {vm.get("name", ""): vm.get("state", "") for vm in json.loads(res.stdout or "[]")}
                except (subprocess.CalledProcessError, OSError, ValueError, AttributeError):
                    # Listing failed: we can't tell whether the VM stopped, so don't claim it did.
                    time.sleep(1)
                    continue
                if names_and_states.get(vm_name, "stopped") == "stopped":
                    return True
                time.sleep(1)
        print(
            f"[Autoscaler:OrbStack-VM] Warning: '{vm_name}' did not confirm stopped after "
            f"repeated attempts -- it may still be running and consuming host resources.",
            file=sys.stderr,
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
            orb_arch = name[len(BASE_IMAGE_PREFIX) :].removesuffix("-building")
            with self._backoff.lock:
                being_built = orb_arch in self._backoff.in_progress
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
                        print(f"[Autoscaler:OrbStack-VM] Idle staging VM '{name}' is already provisioned -- promoting to '{base_name}'.")
                        self._promote_staging_to_base(name, base_name)
                    else:
                        print(f"[Autoscaler:OrbStack-VM] Golden base image '{name}' is running idle -- stopping it to free host resources for job VMs.")
                        self._stop_vm(name)
                else:
                    # Stopped, and no live builder in this process is tracking
                    # it: an orphaned/interrupted build. Resume it rather than
                    # leaving it inert forever -- build_base_image() already
                    # handles "found but not provisioned" by deleting and
                    # re-provisioning cleanly from scratch. Dedup'd and
                    # backoff-gated the same as any other build trigger, so
                    # this can't hot-loop even if the resume keeps failing.
                    print(f"[Autoscaler:OrbStack-VM] Found orphaned staging VM '{name}' with no active builder in this process -- resuming its build.")
                    self._build_base_image_async(orb_arch)
                continue

            if state == "running":
                print(f"[Autoscaler:OrbStack-VM] Golden base image '{name}' is running idle -- stopping it to free host resources for job VMs.")
                self._stop_vm(name)
