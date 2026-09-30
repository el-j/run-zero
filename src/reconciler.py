"""
Self-healing reconciliation of GitHub runner registrations against the runners we manage.

Two passes, both run by the autoscaler every reconciliation cycle:

- `reconcile_zombie_runners()` -- a registration GitHub shows as busy but offline is a
  runner that died mid-job. Its job would stay "in progress" forever, so the run is
  cancelled and the registration removed.
- `reconcile_idle_orphans()` -- a local container/VM that GitHub never dispatched to, whose
  ephemeral job already finished, or whose busy flag outlived its job is torn down.

Registrations are looked up per *scope*: the path fragment GitHub's runner API uses,
`repos/<owner>/<repo>` or `orgs/<org>` (so `/{scope}/actions/runners`).

Outage safety: a scope whose runner list could not be fetched is *unknown*. Absence from an
unknown scope proves nothing, so no runner that might be registered there is torn down in that
cycle (otherwise one failed API call would destroy every healthy, busy runner).
"""

import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from drivers import RunnerDriver, RunnerInfo
from github_api import github_paginate, github_request

# Prefixes used by all RunZero runner drivers (Docker, OrbStack VM, Multipass, WSL2)
MANAGED_RUNNER_PREFIXES = ("local-runner-", "runzero-vm-", "runzero-mp-", "runzero-wsl-")

# How long a spawned runner is allowed to sit without GitHub ever marking it
# busy before it's considered orphaned and torn down.
IDLE_ORPHAN_TIMEOUT_SECONDS = 600

# Grace period for a runner to boot and register. If a runner is older than this
# and is NOT found in GitHub's active runner list (e.g. ephemeral run already completed
# or failed, or registration failed), it is considered an orphan and reaped.
UNREGISTERED_ORPHAN_TIMEOUT_SECONDS = 180

# How long a runner marked busy by GitHub is allowed to run before being checked
# for stale execution (e.g. hung workflow where cancellation lagged).
# Normal CI test matrices and builds often take 10-45+ minutes; default is 2 hours.
# The autoscaler passes the validated RUNNER_BUSY_TIMEOUT_SECONDS (config.Config).
BUSY_RUNNER_TIMEOUT_SECONDS = 7200


def repo_scope(repo: str) -> str:
    """Return the runner-API scope for a repository ("owner/name")."""
    return f"repos/{repo}"


def org_scope(org: str) -> str:
    """Return the runner-API scope for an organization."""
    return f"orgs/{org}"


def normalize_repo_name(name: str) -> str:
    """Fold "owner/repo" and the legacy hyphenated "owner-repo" form to one comparable key."""
    return name.replace("/", "-").lower()


def resolve_repo(target: str, repos: Iterable[str]) -> str:
    """Map a runner's target ("owner/repo", or legacy "owner-repo") to a tracked repo, or ""."""
    if not target:
        return ""
    tracked = list(repos)
    if target in tracked:
        return target
    wanted = normalize_repo_name(target)
    return next((repo for repo in tracked if normalize_repo_name(repo) == wanted), "")


def _runner_name_matches(local_name: str, gh_name: str) -> bool:
    """Match exact names and legacy suffix variants used by older start.sh images."""
    if not local_name or not gh_name:
        return False
    return gh_name == local_name or gh_name.startswith(f"{local_name}-")


@dataclass(frozen=True)
class Registration:
    """One GitHub runner registration and the scope it was found in."""

    scope: str
    runner: dict[str, Any]

    @property
    def busy(self) -> bool:
        """Whether GitHub reports this runner as currently assigned to a job."""
        return bool(self.runner.get("busy"))


class RunnerRegistry:
    """GitHub's registered runners per scope, where None marks a scope that failed to load."""

    def __init__(self, by_scope: dict[str, list[dict[str, Any]] | None]):
        """Wrap an already-fetched scope -> runners (or None) mapping."""
        self.by_scope = by_scope

    @classmethod
    def fetch(cls, scopes: Iterable[str], access_token: str | None) -> "RunnerRegistry":
        """Fetch every scope's full (paginated) runner list."""
        # A capped (truncated) list can't prove absence, so it counts as unknown too.
        return cls({scope: github_paginate(f"/{scope}/actions/runners", "runners", access_token=access_token, allow_truncated=False) for scope in scopes})

    def find(self, local_name: str) -> Registration | None:
        """Return the registration matching `local_name` in any successfully loaded scope."""
        for scope, runners in self.by_scope.items():
            for runner in runners or []:
                if _runner_name_matches(local_name, str(runner.get("name", ""))):
                    return Registration(scope, runner)
        return None

    def is_conclusive_for(self, scope: str | None) -> bool:
        """Whether "not found" is trustworthy for a runner targeting `scope`.

        A known target scope must have loaded; an unknown target (legacy runner without
        a resolvable repo) requires every scope to have loaded.
        """
        if scope is not None and scope in self.by_scope:
            return self.by_scope[scope] is not None
        return all(runners is not None for runners in self.by_scope.values())


class Action(Enum):
    """What the reconciler does with one managed runner this cycle."""

    KEEP = "keep"
    REAP_UNREGISTERED = "reap-unregistered"
    REAP_IDLE = "reap-idle"
    CHECK_STALE_BUSY = "check-stale-busy"


@dataclass(frozen=True)
class Timeouts:
    """Age thresholds (seconds) that make a runner eligible for each reap path."""

    idle: int = IDLE_ORPHAN_TIMEOUT_SECONDS
    unregistered: int = UNREGISTERED_ORPHAN_TIMEOUT_SECONDS
    busy: int = BUSY_RUNNER_TIMEOUT_SECONDS


def classify(age_seconds: float, registration: Registration | None, registry_conclusive: bool, timeouts: Timeouts) -> Action:
    """Decide what to do with one runner. Pure: no I/O, all thresholds strict (>).

    - Not registered: reap once past the registration grace period, but only if the
      registry lookup was conclusive (see RunnerRegistry.is_conclusive_for).
    - Registered and busy: past the busy timeout it becomes a stale-busy *candidate*;
      the executor still verifies no active job references it before acting.
    - Registered and idle: reap once past the idle timeout.
    """
    if registration is None:
        if registry_conclusive and age_seconds > timeouts.unregistered:
            return Action.REAP_UNREGISTERED
        return Action.KEEP
    if registration.busy:
        return Action.CHECK_STALE_BUSY if age_seconds > timeouts.busy else Action.KEEP
    return Action.REAP_IDLE if age_seconds > timeouts.idle else Action.KEEP


def _repos_for_scope(scope: str, repos: list[str]) -> list[str]:
    """Repositories whose runs can hold jobs for runners registered in `scope`."""
    return [scope[len("repos/") :]] if scope.startswith("repos/") else list(repos)


def _active_jobs_by_runner(repos: list[str], access_token: str | None) -> dict[str, tuple[str, dict[str, Any]]] | None:
    """Map runner name -> (repo, in-progress run) for every job currently running in `repos`.

    Returns None if any lookup failed, so callers can tell "verified no active job" from
    "could not check".
    """
    active: dict[str, tuple[str, dict[str, Any]]] = {}
    for repo in repos:
        runs = github_paginate(f"/repos/{repo}/actions/runs?status=in_progress", "workflow_runs", access_token=access_token)
        if runs is None:
            return None
        for run in runs:
            if not run.get("id"):
                continue
            jobs = github_paginate(f"/repos/{repo}/actions/runs/{run['id']}/jobs", "jobs", access_token=access_token)
            if jobs is None:
                return None
            for job in jobs:
                runner_name = str(job.get("runner_name") or "").strip()
                if runner_name:
                    active[runner_name] = (repo, run)
    return active


def _get_in_progress_runner_names(repo: str, access_token: str | None = None) -> set[str] | None:
    """Return runner names attached to in-progress jobs in one repo, or None if the lookup failed."""
    active = _active_jobs_by_runner([repo], access_token)
    return None if active is None else set(active)


def _delete_registration(registration: Registration, access_token: str | None) -> bool:
    """Remove a registration from GitHub. False when GitHub refuses (e.g. 422: still running a job)."""
    return bool(github_request(f"/{registration.scope}/actions/runners/{registration.runner.get('id')}", access_token=access_token, method="DELETE"))


def reconcile_zombie_runners(repos: list[str], access_token: str | None = None, org: str | None = None) -> None:
    """Find and unstick runners GitHub still thinks are busy but that are actually dead.

    Cancels whatever run is pinned to a dead runner, then removes the stale registration.
    With `org`, registrations are read at org scope and runs are searched across `repos`.
    """
    scopes = [org_scope(org)] if org else [repo_scope(repo) for repo in repos]
    for scope in scopes:
        runners = github_paginate(f"/{scope}/actions/runners", "runners", access_token=access_token)
        zombies = [r for r in runners or [] if r.get("status") == "offline" and r.get("busy") and str(r.get("name", "")).startswith(MANAGED_RUNNER_PREFIXES)]
        if not zombies:
            continue

        active = _active_jobs_by_runner(_repos_for_scope(scope, repos), access_token) or {}
        for zombie in zombies:
            print(f"[Autoscaler] ⚠️  Zombie runner detected: {zombie['name']} (offline but marked busy) — reconciling...", file=sys.stderr)
            pinned = active.get(zombie["name"])
            if pinned:
                repo, run = pinned
                print(f"[Autoscaler] Cancelling run #{run.get('run_number')} ({run['id']}) pinned to dead runner {zombie['name']}", file=sys.stderr)
                github_request(f"/repos/{repo}/actions/runs/{run['id']}/cancel", access_token=access_token, method="POST")

            if _delete_registration(Registration(scope, zombie), access_token):
                print(f"[Autoscaler] Removed stale runner registration: {zombie['name']}", file=sys.stderr)
            else:
                print(f"[Autoscaler] Could not remove {zombie['name']} yet (run cancellation likely still in flight) — will retry next cycle", file=sys.stderr)


def _managed_candidates(local_runners: list[RunnerInfo], now: float, min_age: int) -> list[RunnerInfo]:
    """Running, RunZero-managed runners old enough that some reap path could apply."""
    return [
        r
        for r in local_runners
        if r.state == "running" and str(r.name).startswith(MANAGED_RUNNER_PREFIXES) and r.created_at is not None and now - r.created_at > min_age
    ]


class _OrphanExecutor:
    """Carries out classify()'s decisions, caching active-job lookups per scope for one cycle."""

    def __init__(self, repos: list[str], drivers: dict[str, RunnerDriver], access_token: str | None):
        """Bind the tracked repos, driver registry and token used for this cycle."""
        self.repos = repos
        self.drivers = drivers
        self.access_token = access_token
        self._active: dict[str, set[str] | None] = {}

    def _destroy(self, runner: RunnerInfo) -> None:
        driver = self.drivers.get(runner.backend)
        if driver:
            driver.destroy_runner(runner.id)

    def _active_names(self, scope: str) -> set[str] | None:
        if scope not in self._active:
            active = _active_jobs_by_runner(_repos_for_scope(scope, self.repos), self.access_token)
            self._active[scope] = None if active is None else set(active)
        return self._active[scope]

    def execute(self, action: Action, runner: RunnerInfo, registration: Registration | None, age_seconds: float) -> None:
        """Apply `action` to `runner` (a no-op for KEEP)."""
        age_minutes = max(1, int(age_seconds / 60))
        if action is Action.REAP_UNREGISTERED:
            print(
                f"[Autoscaler] 🧹 Orphaned runner detected: {runner.name} "
                f"(not registered in GitHub Actions / run finished, alive {age_minutes}m) — tearing down...",
                file=sys.stderr,
            )
            self._destroy(runner)
        elif action is Action.REAP_IDLE and registration is not None:
            print(
                f"[Autoscaler] 🧹 Orphaned runner detected: {runner.name} (idle {age_minutes}m, GitHub never dispatched a job to it) — tearing down...",
                file=sys.stderr,
            )
            self._destroy(runner)
            _delete_registration(registration, self.access_token)
        elif action is Action.CHECK_STALE_BUSY and registration is not None:
            self._reap_if_stale_busy(runner, registration, age_minutes)

    def _reap_if_stale_busy(self, runner: RunnerInfo, registration: Registration, age_minutes: int) -> None:
        active = self._active_names(registration.scope)
        # A failed lookup, or any in-progress job still naming this runner, means hands off.
        if active is None or any(_runner_name_matches(runner.name, name) for name in active):
            return
        # Unregister FIRST: GitHub refuses (422) while the runner is really executing a job,
        # which is the final guard against tearing down a live runner.
        if not _delete_registration(registration, self.access_token):
            print(
                f"[Autoscaler] ⚠️  Could not remove busy runner registration: {runner.name} "
                f"(GitHub rejected unregistration — runner likely still running a job) — skipping teardown",
                file=sys.stderr,
            )
            return
        print(
            f"[Autoscaler] 🧹 Stale busy runner detected: {runner.name} "
            f"(busy flag persisted, no in-progress job attached, age {age_minutes}m) — tearing down...",
            file=sys.stderr,
        )
        self._destroy(runner)


def reconcile_idle_orphans(
    repos: list[str],
    local_runners: list[RunnerInfo],
    drivers: dict[str, RunnerDriver],
    access_token: str | None = None,
    idle_timeout_seconds: int = IDLE_ORPHAN_TIMEOUT_SECONDS,
    unregistered_timeout_seconds: int = UNREGISTERED_ORPHAN_TIMEOUT_SECONDS,
    busy_timeout_seconds: int = BUSY_RUNNER_TIMEOUT_SECONDS,
    now: float | None = None,
    org: str | None = None,
) -> None:
    """Destroy our own runners that GitHub never dispatched to, that finished, or whose busy flag is stale.

    A local container/VM can end up permanently unused for reasons other than the zombie
    case -- a completed ephemeral job where the VM didn't power off, a mislabeled workflow,
    a race between our poll and GitHub's dispatch, or an API hiccup. With `org`, runners
    are matched against org-scope registrations. Makes no API calls when no runner is old
    enough to be eligible.
    """
    now = now if now is not None else time.time()
    timeouts = Timeouts(idle=idle_timeout_seconds, unregistered=unregistered_timeout_seconds, busy=busy_timeout_seconds)
    candidates = _managed_candidates(local_runners, now, min(timeouts.idle, timeouts.unregistered))
    if not candidates:
        return

    registry = RunnerRegistry.fetch([org_scope(org)] if org else [repo_scope(repo) for repo in repos], access_token)
    executor = _OrphanExecutor(repos, drivers, access_token)
    for runner in candidates:
        assert runner.created_at is not None  # guaranteed by _managed_candidates
        age_seconds = now - runner.created_at
        target_repo = resolve_repo(runner.target_repo, repos)
        target_scope = org_scope(org) if org else (repo_scope(target_repo) if target_repo else None)
        registration = registry.find(runner.name)
        action = classify(age_seconds, registration, registry.is_conclusive_for(target_scope), timeouts)
        executor.execute(action, runner, registration, age_seconds)
