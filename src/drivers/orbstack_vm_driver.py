"""
🪐 OrbStack Virtual Machine Runner Driver
Spawns and manages dedicated, lightweight Linux Virtual Machines via OrbStack (Apple Virtualization framework).
Provides full systemd, dedicated kernel, internal Docker daemon, unconfined browser sandboxes,
automatic integration with local caching proxies (Verdaccio, Athens, apt-cacher-ng, devpi, kellnr),
and real host-backed local disk caches via OrbStack's automatic /mnt/mac filesystem share
(see `orbstack_templates.cache_mount_snippet()`).
"""

import contextlib
import json
import shutil
import subprocess
import sys
import time
import uuid

from . import ImageEventCallback, RunnerDriver, RunnerInfo, merge_labels
from .backoff import BuildBackoff
from .orbstack_image import BASE_IMAGE_PREFIX, OrbStackImageBuilder
from .orbstack_templates import (
    cache_mount_snippet,
    registration_and_run_snippet,
)

RUNNER_VM_PREFIX = "runzero-vm-"

# A per-job clone that goes from "just spawned" to "stopped" faster than this
# never had a real chance to register and run a job -- see
# _record_spawn_outcome()'s docstring for why this specific failure mode
# (network-less clones) needs its own circuit breaker, separate from the
# existing build_base_image() one.
STARTUP_GRACE_PERIOD_SECONDS = 15.0
FAST_FAILURE_WINDOW_SECONDS = 60.0
MAX_CONSECUTIVE_FAST_FAILURES = 3

# Crockford base32 -- the alphabet OrbStack's VM "id" field (a ULID) is encoded
# with. See _vm_created_at_from_ulid() below for why this matters.
_ULID_ALPHABET_INDEX = {c: i for i, c in enumerate("0123456789ABCDEFGHJKMNPQRSTVWXYZ")}


def _vm_created_at_from_ulid(vm_id: str) -> float | None:
    """Decode the creation time OrbStack itself baked into a VM's `id`, as Unix epoch seconds.

    `orbctl list --format json` doesn't expose a created-at field directly, but the `id`
    it does return for every VM is a ULID: its first 10 characters are a 48-bit
    millisecond Unix timestamp, assigned once by OrbStack at creation and stable for the
    VM's lifetime -- unlike anything this driver tracks itself in memory.

    Without this, list_runners() fell back to time.time() the first time *this process*
    happened to observe a given VM name, via `_runner_created_at`. That dict lives only
    in the driver instance's memory, so it resets on every restart of whatever process
    owns this driver -- for the containerized autoscaler that's `vm_bridge.py` on the
    host (see its module docstring), which runs unsupervised and has no auto-restart.
    Confirmed live (2026-09-10): the bridge died mid-clone for 4 VMs; because it wasn't
    restarted, `.bridge.log` simply stopped, and once it silently came back into scope
    the *first* list_runners() call after any restart would have re-seeded every
    already-existing VM's age as "just now" -- permanently defeating this file's own
    FAST_FAILURE_WINDOW_SECONDS circuit breaker and reconciler.py's
    IDLE_ORPHAN_TIMEOUT_SECONDS / UNREGISTERED_ORPHAN_TIMEOUT_SECONDS, since both compare
    against `RunnerInfo.created_at`. Those 4 VMs sat "running" for 16+ hours, never
    having registered with GitHub (no queued/in-progress job left for them either),
    burning host CPU/RAM with nothing to reap them. Deriving the age from OrbStack's own
    per-VM ULID instead makes every one of those existing timeouts restart-proof for
    free, with no new API calls.

    Returns None (caller should fall back to its own tracking) if `vm_id` isn't a
    plausible ULID -- e.g. a test fixture with no/synthetic id, or a future OrbStack
    version changing this format.
    """
    if not vm_id or len(vm_id) < 10:
        return None
    try:
        ts_ms = 0
        for ch in vm_id[:10]:
            ts_ms = ts_ms * 32 + _ULID_ALPHABET_INDEX[ch.upper()]
    except KeyError:
        return None
    return ts_ms / 1000.0


class OrbStackVMDriver(RunnerDriver):
    """Runs ephemeral runners as dedicated OrbStack Linux VMs, cloned per-job from a golden base image."""

    is_vm = True

    def __init__(self, distro: str = "ubuntu:24.04", on_image_event: ImageEventCallback | None = None):
        """Configure the base distro golden images are built from, and init per-arch build/tracking state.

        `on_image_event`, when given, is called with a structured dict on every golden base
        image build status transition (building/ready/failed/cooldown) -- see
        `_report_image_event()`.
        """
        self.distro = distro
        self._on_image_event: ImageEventCallback = on_image_event or (lambda event: None)
        # Golden-image builds run on a background thread (so the poll loop never blocks for
        # the 15-25 min a build takes) with per-arch dedup and exponential backoff after a
        # failure -- confirmed live: `orbctl create` can fail "machine didn't start in 30s
        # (missing IP address)" for EVERY new VM because of host/OrbStack network-stack state,
        # and retrying that every poll tick only burns OrbStack daemon load. See BuildBackoff.
        self._backoff = BuildBackoff()
        # Golden-image build/promote/stop lives in its own unit; the callbacks are late-bound
        # so they always reach this driver's current methods.
        self.images = OrbStackImageBuilder(
            distro,
            self._backoff,
            list_vm_names=lambda: self._list_vm_names(),
            report_event=lambda status, arch, detail: self._report_image_event(status, arch, detail),
            resume_build=lambda arch: self._build_base_image_async(arch),
        )
        # Separate backoff for a different failure mode: `orbctl clone` (not `orbctl create`) succeeding, then
        # the clone itself never getting a network address -- see _record_spawn_outcome().
        self._spawn_failure_counts: dict[str, int] = {}
        self._spawn_retry_after: dict[str, float] = {}
        self._runner_created_at: dict[str, float] = {}
        self._runner_repos: dict[str, str] = {}

    def _report_image_event(self, status: str, arch: str, detail: str, profile: str | None = None) -> None:
        """Emit a structured build-status event alongside the existing stdout/stderr prints.

        Never raises -- a broken/misbehaving callback must not be able to break an actual build.
        """
        with contextlib.suppress(Exception):
            self._on_image_event(
                {
                    "driver": self.name(),
                    "arch": arch,
                    "profile": profile,
                    "status": status,
                    "detail": detail,
                    "ts": time.time(),
                }
            )

    def name(self) -> str:
        """Return this driver's backend identifier: "orbstack-vm"."""
        return "orbstack-vm"

    def is_available(self) -> bool:
        """True if `orbctl`/`orb` are on PATH and `orbctl status` reports the OrbStack daemon running."""
        if not shutil.which("orbctl") or not shutil.which("orb"):
            return False
        try:
            res = subprocess.run(["orbctl", "status"], capture_output=True, text=True, check=True, timeout=3)
            return "running" in res.stdout.lower()
        except Exception:
            return False

    base_image_name = staticmethod(OrbStackImageBuilder.base_image_name)

    def _list_vm_names(self) -> list[str]:
        # Retried because a single transient "orbctl list" failure (CLI busy while
        # another orbctl/orb command is mid-flight, momentary daemon hiccup, etc.)
        # used to be indistinguishable from "no VMs exist at all". That false
        # negative fed straight into base_image_exists() -> False, which triggered
        # build_base_image() to unconditionally `orbctl delete -f` and rebuild a
        # perfectly healthy golden image from scratch (confirmed happening live).
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                res = subprocess.run(["orbctl", "list", "--format", "json"], capture_output=True, text=True, check=True, timeout=5)
                vms = json.loads(res.stdout or "[]")
                return [vm.get("name", "") for vm in vms]
            except Exception as e:
                last_err = e
                if attempt < 2:
                    time.sleep(0.5)
        print(f"[Autoscaler:OrbStack-VM] Warning: 'orbctl list' failed after retries: {last_err}", file=sys.stderr)
        return []

    def base_image_exists(self, orb_arch: str) -> bool:
        """True if the golden base image VM exists for `orb_arch` (see OrbStackImageBuilder)."""
        return self.images.base_image_exists(orb_arch)

    def build_base_image(self, orb_arch: str) -> bool:
        """Build the golden base image synchronously (see OrbStackImageBuilder.build_base_image)."""
        return self.images.build_base_image(orb_arch)

    def ensure_base_images_stopped(self) -> None:
        """Stop idle base images and resume orphaned builds (see OrbStackImageBuilder)."""
        self.images.ensure_base_images_stopped()

    def _spawn_cooldown_remaining(self, orb_arch: str) -> float:
        """Seconds until the next spawn_runner() clone for orb_arch is allowed, or 0.0 if none is in effect."""
        return max(0.0, self._spawn_retry_after.get(orb_arch, 0.0) - time.monotonic())

    def _record_spawn_outcome(self, orb_arch: str, got_network: bool) -> None:
        """Track whether recently-cloned VMs are actually getting a network address, and back off
        spawning more of them for this arch once they consistently aren't.

        `prune_exited()` calls this once per poll with `got_network=False` for every clone it's
        about to delete that died younger than FAST_FAILURE_WINDOW_SECONDS, and `got_network=True`
        for every still-running clone older than that window (proof this arch is currently healthy).

        This exists for a *different* failure mode than the build backoff (`_backoff`)
        above: that pair guards `orbctl create` (building the golden image) failing outright.  This
        one guards `orbctl clone` succeeding -- so spawn_runner() has already returned a VM name and
        the caller thinks a runner is on its way -- but the clone then never gets a network address
        inside the guest, so it can never reach the GitHub API to register, and self-powers-off via
        the `trap cleanup EXIT` in orbstack_templates.py's setup script. Without this circuit
        breaker, that failure is invisible to spawn_runner() itself (the registration/run happens in
        a detached, fire-and-forget `orb exec`) and the poll loop's ~10s cadence just clones a
        replacement for the still-queued job every tick -- confirmed live (2026-09-09): 355 clones
        in under 20 minutes, zero of which ever registered with GitHub, while burning a GitHub
        registration-token API call each time.

        This is an OrbStack-side bug, not something fixable from here: a bare `orbctl create`
        reproduces the same "missing IP address" failure with zero run-zero code involved, and it
        survives BOTH an OrbStack app restart and a full `orbctl stop && orbctl start` engine
        cycle (confirmed live -- a diagnostic VM created immediately after a cold `orbctl
        stop`/`start` failed identically). Filed upstream as
        https://github.com/orbstack/orbstack/issues/2688. From this driver's side, all that's
        knowable is "clones for this arch keep dying before they could possibly have registered,"
        which is exactly what's tracked here.
        """
        if got_network:
            self._spawn_failure_counts[orb_arch] = 0
            self._spawn_retry_after.pop(orb_arch, None)
            return

        failures = self._spawn_failure_counts.get(orb_arch, 0) + 1
        self._spawn_failure_counts[orb_arch] = failures
        if failures < MAX_CONSECUTIVE_FAST_FAILURES:
            return

        cooldown = min(30 * (2 ** (failures - MAX_CONSECUTIVE_FAST_FAILURES)), 900)
        self._spawn_retry_after[orb_arch] = time.monotonic() + cooldown
        print(
            f"[Autoscaler:OrbStack-VM] {failures} consecutive '{orb_arch}' clones in a row died "
            f"within {int(FAST_FAILURE_WINDOW_SECONDS)}s of being created -- never long enough to "
            f"register a runner. This almost always means the clone never got a network address -- "
            f"an OrbStack-side issue, not a run-zero bug. Confirmed live (2026-09-09) that neither "
            f"an OrbStack app restart NOR a full `orbctl stop && orbctl start` engine cycle clears "
            f"it once it starts (a bare `orbctl create` fails identically right after either); a "
            f"full macOS reboot has cleared it in the past but is not a guaranteed permanent fix "
            f"and it has recurred after enough VM churn. Tracked upstream at "
            f"https://github.com/orbstack/orbstack/issues/2688 -- not fixable from run-zero's "
            f"side. Backing off {cooldown}s before spawning another '{orb_arch}' VM.",
            file=sys.stderr,
        )

    def reset_spawn_cooldown(self, orb_arch: str | None = None) -> None:
        """Reset the consecutive fast failure counts and cooldown for an arch (or all arches)."""
        arches = [orb_arch] if orb_arch else list(self._spawn_failure_counts.keys())
        for a in arches:
            self._spawn_failure_counts[a] = 0
            self._spawn_retry_after.pop(a, None)

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

        def on_failure(failures: int, cooldown: int) -> None:
            hint = (
                " This many consecutive failures usually isn't transient -- if "
                "'orbctl create' is failing with a 'missing IP address' timeout, a "
                "plain OrbStack app restart often doesn't clear it, but a full host "
                "reboot usually does (stale macOS virtual-network-extension state "
                "after long uptime). Verify with a bare `orbctl create -a "
                f"{orb_arch} ubuntu:24.04 diag-test` outside run-zero before assuming "
                "this is a run-zero bug."
                if failures >= 3
                else ""
            )
            detail = f"Has now failed {failures} time(s) in a row. Backing off {cooldown}s before retrying.{hint}"
            print(f"[Autoscaler:OrbStack-VM] Golden base image build for '{orb_arch}' {detail}", file=sys.stderr)
            self._report_image_event("cooldown", orb_arch, detail)

        self._backoff.run_async(orb_arch, lambda: self.build_base_image(orb_arch), f"runzero-build-base-{orb_arch}", on_failure, "[Autoscaler:OrbStack-VM]")

    def ensure_runtime_assets(self, arch: str = "arm64") -> bool:
        """Ensure the per-arch golden VM base image exists, triggering async build when missing."""
        orb_arch = "arm64" if arch == "arm64" else "amd64"
        base_name = self.base_image_name(orb_arch)

        if self.base_image_exists(orb_arch):
            return True

        with self._backoff.lock:
            already_building = orb_arch in self._backoff.in_progress
            cooldown_remaining = self._backoff.remaining(orb_arch)

        if not already_building and cooldown_remaining <= 0:
            print(
                f"[Autoscaler:OrbStack-VM] 🏗️  Golden base image '{base_name}' not found. "
                f"Building it in the background (one-time setup, ~15-25 min) -- "
                f"other repos/engines keep being served meanwhile. This job's "
                f"VM will be spawned on a later poll once the image is ready."
            )
            self._build_base_image_async(orb_arch)
        elif already_building:
            print(f"[Autoscaler:OrbStack-VM] Golden base image '{base_name}' is currently building. This queued job will be retried on the next poll.")
        else:
            print(
                f"[Autoscaler:OrbStack-VM] Golden base image '{base_name}' is missing, but build retry is "
                f"cooling down for {int(cooldown_remaining)}s after a previous failure.",
                file=sys.stderr,
            )

        return False

    def join_background_build_threads(self, timeout: float = 10.0) -> bool:
        """Block until every background build_base_image() thread started via
        `_build_base_image_async` has finished, up to `timeout` seconds each.

        Exists primarily for tests: it gives a deterministic point to wait for
        a driver-owned background thread to fully exit, instead of polling
        shared state (racy) or letting the thread run un-joined past the
        caller's own scope. A thread left running past a test's mock.patch
        context stops seeing that test's mocked subprocess.run and starts
        issuing REAL orbctl/orb calls against a real OrbStack daemon if one is
        installed -- see issue #20.

        Returns True if every tracked thread has finished (already, or within
        `timeout`); False if at least one is still alive when this returns.
        Callers that must guarantee "no thread survives past this point"
        (e.g. a test's tearDown) should treat False as a hard failure.
        """
        return self._backoff.join(timeout)

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
        """Clone the golden base image and boot a per-job VM that registers, runs, then self-powers-off.

        The VM receives only a registration token (see `RunnerDriver._prepare_spawn`), never
        the PAT; returns None when inputs are invalid or no token can be obtained.

        If the base image for this arch doesn't exist yet, kicks off an async background build
        (see `_build_base_image_async`) and returns None immediately -- callers should treat that
        as "not ready this poll, try again later," not a hard failure. Also returns None if the
        `orbctl clone` step itself fails. The clone is synchronous; registration/run/shutdown inside
        the VM happens via a detached `orb exec` (Popen), so this call doesn't block on job execution.

        `cache_mounts` (host path -> container-style path, from `cache_manager.init_cache_dirs()`)
        is turned into real bind mounts inside the VM via `cache_mount_snippet()` -- see that
        function's docstring for the OrbStack `/mnt/mac` mechanism this relies on. Previously this
        parameter was accepted here and silently discarded.
        """
        unique_id = uuid.uuid4().hex[:6]
        name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
        vm_name = f"{RUNNER_VM_PREFIX}{arch}{name_suffix}-{unique_id}"

        default_labels = f"self-hosted,local,vm,{arch}"
        if arch in ("amd64", "x64", "x86_64"):
            default_labels += ",rosetta"
        runner_labels = merge_labels(default_labels, labels)
        orb_arch = "arm64" if arch == "arm64" else "amd64"

        cooldown_remaining = self._spawn_cooldown_remaining(orb_arch)
        if cooldown_remaining > 0:
            print(
                f"[Autoscaler:OrbStack-VM] Spawning for '{orb_arch}' is cooling down for "
                f"{int(cooldown_remaining)}s after {self._spawn_failure_counts.get(orb_arch, 0)} "
                f"consecutive clones failed to get a network address within "
                f"{int(FAST_FAILURE_WINDOW_SECONDS)}s of being created. This queued job will be "
                f"retried once the cooldown lifts.",
                file=sys.stderr,
            )
            return None

        proxy_env_block = ""
        if proxies_enabled:
            proxy_env_block = """
export npm_config_registry="http://host.orb.internal:49501"
export NPM_CONFIG_REGISTRY="http://host.orb.internal:49501/"
export YARN_REGISTRY="http://host.orb.internal:49501"
export GOPROXY="http://host.orb.internal:49500,https://proxy.golang.org,direct"
export PIP_INDEX_URL="http://host.orb.internal:49507/root/pypi/+simple/"
export UV_INDEX_URL="http://host.orb.internal:49507/root/pypi/+simple/"
export PIP_TRUSTED_HOST="host.orb.internal"
echo 'Acquire::http::Proxy "http://host.orb.internal:49503";' | sudo tee /etc/apt/apt.conf.d/01runzero-proxy > /dev/null
"""
            # pip implicitly trusts "localhost"/"127.0.0.1" for a plain-HTTP index but
            # refuses any other host -- verified live (2026-08-26) inside a real OrbStack
            # VM: without PIP_TRUSTED_HOST, pip printed "is not a trusted or secure host",
            # silently skipped the index, and exited 0 having installed nothing. uv has no
            # equivalent restriction (verified: identical install succeeds unmodified).
            # kellnr's crates.io proxy has no single "index URL" env var: verified live
            # (2026-08-26) that cargo silently ignores CARGO_SOURCE_<name>_* env vars for a
            # dynamic/custom [source.*] table (a real cargo limitation, not a typo) --
            # tracing cargo's own network layer showed it still fetching straight from
            # https://index.crates.io with the env vars set, and only switching to the
            # proxy once a real ~/.cargo/config.toml source-replacement block existed.
            # Written directly here (rather than via a curl-based runtime probe like
            # start.sh's, since host.orb.internal always resolves to the real Mac host from
            # inside an OrbStack VM -- no "is it up" detection needed the way Mode 2's
            # bridge-network containers need one).
            proxy_env_block += """
sudo mkdir -p /home/runner/.cargo 2>/dev/null || true
sudo chown -R runner:runner /home/runner/.cargo 2>/dev/null || true
mkdir -p /home/runner/.cargo
cat > /home/runner/.cargo/config.toml <<'CARGOCFG'
[source.crates-io]
replace-with = "kellnr-proxy"

[source.kellnr-proxy]
registry = "sparse+http://host.orb.internal:49506/api/v1/cratesio/"
CARGOCFG
"""

        cache_mount_block = cache_mount_snippet(cache_mounts)

        runner_url = f"https://github.com/{repo or org}"

        if not self.ensure_runtime_assets(orb_arch):
            return None
        base_name = self.base_image_name(orb_arch)

        registration_token = self._prepare_spawn(repo, org, labels, access_token, runner_token, extra_env)
        if not registration_token:
            return None

        reg_and_run = registration_and_run_snippet(runner_url, registration_token, vm_name, runner_labels, proxy_env_block, cache_mount_block)

        print(f"[Autoscaler:OrbStack-VM] 🚀 Spawning ephemeral [{arch.upper()}] Linux VM '{vm_name}' (cloned from golden image '{base_name}')...")
        clone_cmd = ["orbctl", "clone", base_name, vm_name]
        setup_script = f"""
exec > /home/runner/setup.log 2>&1
cleanup() {{
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "[RunZero VM Error] Setup script failed with exit code $EXIT_CODE" >&2
    fi
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

            subprocess.Popen(["orb", "-m", vm_name, "-u", "runner", "bash", "-c", setup_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return vm_name
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            print(f"[Autoscaler:OrbStack-VM] Error creating VM: {stderr}", file=sys.stderr)
            return None

    def list_runners(self) -> list[RunnerInfo]:
        """List job VMs (name starts with the runner prefix, excluding golden base images).

        Returns an empty list (and prints to stderr) if the `orbctl list` call itself fails.
        """
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

                    # Prefer OrbStack's own creation timestamp (see
                    # _vm_created_at_from_ulid's docstring for why this matters) --
                    # fall back to this process's own first-observed time only if the
                    # id isn't a decodable ULID (e.g. test fixtures).
                    created_at = _vm_created_at_from_ulid(vm.get("id", ""))
                    if created_at is None:
                        created_at = self._runner_created_at.get(name, time.time())
                    self._runner_created_at[name] = created_at

                    target_repo = self._runner_repos.get(name, "")
                    if not target_repo:
                        name_body = name[len(RUNNER_VM_PREFIX) :]
                        body_parts = name_body.split("-")
                        if len(body_parts) >= 3:
                            target_repo = "-".join(body_parts[1:-1])

                    runners.append(
                        RunnerInfo(
                            id=name,
                            name=name,
                            status=status,
                            state=state,
                            target_repo=target_repo,
                            target_arch=arch,
                            backend="orbstack-vm",
                            created_at=created_at,
                        )
                    )
            return runners
        except Exception as e:
            print(f"[Autoscaler:OrbStack-VM] Error listing VMs: {e}", file=sys.stderr)
            return []

    def destroy_runner(self, runner_id: str) -> bool:
        """Delete the named job VM via `orbctl delete -f`.

        Refuses (returns False) if `runner_id` looks like a golden base image name, to guard
        against a caller accidentally destroying the shared image instead of an ephemeral clone.
        """
        if runner_id.startswith(BASE_IMAGE_PREFIX):
            print(
                f"[Autoscaler:OrbStack-VM] Refusing to delete '{runner_id}' -- it looks like a golden base image, not an ephemeral job runner.", file=sys.stderr
            )
            return False
        try:
            subprocess.run(["orbctl", "delete", "-f", runner_id], check=True, capture_output=True)
            self._runner_created_at.pop(runner_id, None)
            self._runner_repos.pop(runner_id, None)
            return True
        except Exception:
            return False

    def prune_exited(self, active_runners: list[RunnerInfo]) -> None:
        """Delete any `active_runners` entries that are OrbStack-VM-backed and in a stopped state.

        Also feeds `_record_spawn_outcome()` (see its docstring) so a run of clones that all die
        implausibly young -- never long enough to have registered a runner -- trips a backoff
        instead of being reclone'd every ~10s poll forever.
        """
        for r in active_runners:
            if r.backend != "orbstack-vm" or r.name.startswith(BASE_IMAGE_PREFIX):
                continue
            age = (time.time() - r.created_at) if r.created_at is not None else None
            # Protect newly spawned clones during initial boot and registration
            if age is not None and age < STARTUP_GRACE_PERIOD_SECONDS:
                continue
            if r.state in ("exited", "stopped", "dead"):
                if age is not None and age < FAST_FAILURE_WINDOW_SECONDS:
                    self._record_spawn_outcome(r.target_arch, got_network=False)
                print(f"[Autoscaler:OrbStack-VM] Deleting stopped VM: {r.name}")
                self.destroy_runner(r.name)
            elif r.state == "running" and age is not None and age >= FAST_FAILURE_WINDOW_SECONDS:
                self._record_spawn_outcome(r.target_arch, got_network=True)

    def cleanup_all(self) -> None:
        """Delete every job VM this driver manages (used on autoscaler shutdown). Golden base images are untouched."""
        runners = self.list_runners()
        for r in runners:
            if r.backend == "orbstack-vm":
                self.destroy_runner(r.name)
