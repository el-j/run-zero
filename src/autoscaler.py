#!/usr/bin/env python3
"""
⚡ RunZero — Local GitHub Actions Runner Autoscaler
Dual-Engine Fleet supporting ultra-fast Docker containers and dedicated Virtual Machines
(OrbStack macOS Linux Machines, Windows WSL2, Canonical Multipass).
Includes persistent multi-language package caching, proxy registries, real-time observability dashboard, and adaptive rate-limiting.

Structure: `Scaler` owns all fleet state and performs one poll cycle per `run_once()`
(quota refresh -> discovery -> collect -> scale -> publish); `main()` only wires config,
drivers, the dashboard and signal handling around that loop.
"""

from __future__ import annotations

import signal
import sys
import time
from collections import OrderedDict
from collections.abc import Callable
from typing import Any

import github_api
from cache_manager import init_cache_dirs
from config import Config, ConfigError, load_config
from dashboard import DashboardServer, dashboard_state
from discovery import discover_repositories
from drivers import RunnerDriver, RunnerInfo, get_available_drivers, select_default_driver
from github_api import get_queued_job_details, refresh_actions_billing, refresh_rate_limit
from reconciler import reconcile_idle_orphans, reconcile_zombie_runners
from router import select_driver_for_job
from version import __version__

ARM_LABELS = ("arm64", "aarch64", "arm")
# Job ids remembered for once-per-job routing statistics (oldest forgotten first).
RECORDED_JOBS_LIMIT = 4096
AMD_ARCH_ALIASES = ("amd64", "x64", "x86_64")


def log_print(msg: str, file: Any = None) -> None:
    """Print message to stdout/stderr and push to dashboard log ring buffer."""
    if file:
        print(msg, file=file)
    else:
        print(msg)
    dashboard_state.append_log(msg)


def get_target_architectures(runner_arch: str) -> list[str]:
    """Architectures to rotate through for the standby pool, from RUNNER_ARCH."""
    if runner_arch == "both":
        return ["arm64", "amd64"]
    if runner_arch in AMD_ARCH_ALIASES:
        return ["amd64"]
    return ["arm64"]


def resolve_job_arch(job_labels: list[str], runner_arch: str) -> str:
    """Pick the architecture for a job, mirroring GitHub-hosted runner defaults.

    A fleet pinned to one arch always uses it; with "both", an explicit ARM label selects
    arm64 and everything else gets amd64 (what `ubuntu-latest` would give the job).
    """
    if runner_arch in AMD_ARCH_ALIASES:
        return "amd64"
    if runner_arch != "both":
        return "arm64"
    if any(label in job_labels for label in ARM_LABELS):
        return "arm64"
    return "amd64"


def build_cache_scope(repo: str, job: dict[str, Any]) -> str:
    """Derive a stable per-job build-cache scope key: `repo + workflow file + job name`.

    Deliberately excludes `run_id`/`id` -- both are unique to a single execution and never
    repeat, so scoping on them (as this previously did) creates a brand-new, always-empty
    `build-cache/<scope>/go-build` directory on every single run: real isolation from other
    jobs, but zero actual cache reuse across repeated runs of the *same* job, defeating the
    entire point of a compilation build cache. Scoping on the job's stable identity instead
    still keeps unrelated/different jobs from colliding on one shared directory, while letting
    the same recurring job (the overwhelmingly common case -- CI running on every push) reuse
    its build cache like it's supposed to. `cache_manager._sanitize_scope()` already strips
    unsafe characters, so the workflow path's slashes and a matrix job's "(x, y)" suffix are
    fine to include as-is.
    """
    return f"{repo}_{job.get('workflow_path', '')}_{job.get('name', '')}".strip("_")


def ensure_driver_runtime_assets(driver: Any, arch: str) -> bool:
    """Ensure per-arch driver prerequisites exist before attempting to spawn."""
    ensure_fn = getattr(driver, "ensure_runtime_assets", None)
    if callable(ensure_fn):
        try:
            return bool(ensure_fn(arch=arch))
        except TypeError:
            return bool(ensure_fn(arch))
    return True


def _new_runner(spawned_id: str, target: str, arch: str, driver: RunnerDriver) -> RunnerInfo:
    return RunnerInfo(id=spawned_id, name=spawned_id, status="running", state="running", target_repo=target, target_arch=arch, backend=driver.name())


class Scaler:
    """One autoscaler instance: fleet state plus the steps of a single poll cycle."""

    def __init__(
        self,
        config: Config,
        drivers: dict[str, RunnerDriver],
        default_driver: RunnerDriver,
        clock: Callable[[], float] = time.time,
        pause: Callable[[float], None] = time.sleep,
    ):
        """Bind configuration and the driver registry; `clock`/`pause` are injectable for tests."""
        self.config = config
        self.drivers = drivers
        self.default_driver = default_driver
        self.architectures = get_target_architectures(config.runner_arch)
        self.tracked_repos: list[str] = []
        self.runner_job_meta: dict[str, dict[str, Any]] = {}
        self._clock = clock
        self._pause = pause
        self._last_discovery = 0.0
        self._last_rate_limit_refresh = 0.0
        self._last_billing_refresh = 0.0
        self._standby_cursor = 0
        self._recorded_jobs: OrderedDict[Any, None] = OrderedDict()

    # -- quota & discovery --------------------------------------------------------------

    def refresh_quota(self, now: float) -> None:
        """Refresh the rate-limit and Actions-billing snapshots when their intervals elapse."""
        cfg = self.config
        if now - self._last_rate_limit_refresh >= max(10, cfg.rate_limit_refresh_interval):
            refresh_rate_limit(access_token=cfg.access_token)
            self._last_rate_limit_refresh = now
        if now - self._last_billing_refresh >= max(30, cfg.actions_billing_refresh_interval):
            owner = cfg.owner
            if not cfg.org and not owner and self.tracked_repos and "/" in self.tracked_repos[0]:
                owner = self.tracked_repos[0].split("/", 1)[0]
            refresh_actions_billing(access_token=cfg.access_token, owner=owner, org=cfg.org)
            self._last_billing_refresh = now

    @property
    def org(self) -> str | None:
        """The organization in ORG mode (runners register at org scope), else None."""
        return self.config.org or None

    def discover(self, now: float) -> None:
        """Refresh the tracked repositories and reconcile zombie runners.

        In ORG mode the org's own active repositories are tracked (discovery lists
        `/orgs/{org}/repos` for an organization owner) and runners are reconciled at org scope.
        """
        cfg = self.config
        if now - self._last_discovery > cfg.discovery_interval or not self.tracked_repos:
            discovered = discover_repositories(
                owner=cfg.org or cfg.owner,
                active_days=cfg.active_days,
                auto_discover=cfg.auto_discover,
                repos_config=cfg.repos_config,
                access_token=cfg.access_token,
            )
            self._last_discovery = now
            if discovered:
                self.tracked_repos = discovered
                self._log_tracked_repos()
        if self.tracked_repos:
            reconcile_zombie_runners(self.tracked_repos, access_token=cfg.access_token, org=self.org)

    def _log_tracked_repos(self) -> None:
        log_print(f"[Autoscaler] Monitoring {len(self.tracked_repos)} active repository(ies):")
        for repo_name in self.tracked_repos:
            log_print(f"  • {repo_name}")
        remaining, total = github_api.rate_limit_remaining, github_api.rate_limit_total
        if remaining is None or total is None:
            log_print("[Autoscaler] GitHub API Quota remaining: unknown/unknown")
        else:
            log_print(f"[Autoscaler] GitHub API Quota remaining: {remaining}/{total} ({github_api.rate_limit_resource or 'unknown'})")

    # -- fleet state -------------------------------------------------------------------

    def collect(self) -> list[RunnerInfo]:
        """List every driver's runners (pruning exited ones) and reap idle orphans."""
        all_runners: list[RunnerInfo] = []
        for driver in self.drivers.values():
            driver.prune_exited(driver.list_runners())
            all_runners.extend(driver.list_runners())
            ensure_stopped = getattr(driver, "ensure_base_images_stopped", None)
            if callable(ensure_stopped):
                ensure_stopped()
        if self.tracked_repos:
            reconcile_idle_orphans(
                self.tracked_repos,
                all_runners,
                self.drivers,
                access_token=self.config.access_token,
                busy_timeout_seconds=self.config.busy_timeout_seconds,
                org=self.org,
                standby_count=self.config.min_runners,
            )
        return all_runners

    # -- scaling -----------------------------------------------------------------------

    def ensure_standby(self, active_runners: list[RunnerInfo]) -> None:
        """Top the fleet up to MIN_RUNNERS warm runners (capped by MAX_RUNNERS), rotating arches.

        Standby runners register at org scope in ORG mode, otherwise round-robin across the
        tracked repositories. Runs after job scaling, so queued jobs get first claim on
        capacity. The reconciler spares up to MIN_RUNNERS idle runners (see collect()).
        """
        cfg = self.config
        targets = [cfg.org] if cfg.org else self.tracked_repos
        active_count = len(active_runners)
        if not targets or active_count >= cfg.min_runners or active_count >= cfg.max_runners:
            return
        needed = min(cfg.min_runners - active_count, cfg.max_runners - active_count)
        for i in range(needed):
            arch = self.architectures[i % len(self.architectures)]
            target = targets[self._standby_cursor % len(targets)]
            self._standby_cursor += 1
            if not ensure_driver_runtime_assets(self.default_driver, arch):
                continue
            spawned_id = self.default_driver.spawn_runner(
                **self._scope_args(target),
                arch=arch,
                access_token=cfg.access_token,
                cache_mounts=init_cache_dirs(cfg.host_cache_dir, arch, cfg.cache_enabled),
                proxies_enabled=cfg.proxies_enabled,
            )
            if spawned_id:
                active_runners.append(_new_runner(spawned_id, target, arch, self.default_driver))

    def _scope_args(self, repo: str) -> dict[str, Any]:
        """spawn_runner() target kwargs: org-scope registration in ORG mode, else the repo."""
        return {"org": self.config.org} if self.config.org else {"repo": repo}

    def gather_queued_jobs(self) -> dict[str, list[dict[str, Any]]]:
        """Queued self-hosted jobs per tracked repo (repos with none are omitted)."""
        queued: dict[str, list[dict[str, Any]]] = {}
        for repo in self.tracked_repos:
            jobs = get_queued_job_details(repo, access_token=self.config.access_token)
            if jobs:
                queued[repo] = jobs
            self._pause(0.1)  # spread per-repo API calls a little
        total = sum(len(jobs) for jobs in queued.values())
        if total:
            log_print(f"[Autoscaler] Detected {total} queued unclaimed job(s) across repos.")
        return queued

    def scale_jobs(self, queued_by_repo: dict[str, list[dict[str, Any]]], active_runners: list[RunnerInfo]) -> None:
        """One runner per queued job not already covered, up to MAX_RUNNERS overall.

        Repo mode counts coverage per repository. In ORG mode every org runner can take any
        repo's job, so coverage is counted across the whole org.
        """
        uncovered = self._uncovered_jobs(queued_by_repo, active_runners)
        for repo, jobs in queued_by_repo.items():
            for job in jobs:
                if len(active_runners) >= self.config.max_runners or uncovered.get(repo if not self.org else "*", 0) <= 0:
                    break
                spawned = self._spawn_for_job(repo, job)
                if spawned:
                    spawned_id, driver, arch = spawned
                    uncovered[repo if not self.org else "*"] -= 1
                    self.runner_job_meta[spawned_id] = {
                        "job_id": job.get("id"),
                        "run_id": job.get("run_id"),
                        "job_url": job.get("job_url", ""),
                        "run_url": job.get("run_url", ""),
                    }
                    active_runners.append(_new_runner(spawned_id, self.org or repo, arch, driver))

    def _uncovered_jobs(self, queued_by_repo: dict[str, list[dict[str, Any]]], active_runners: list[RunnerInfo]) -> dict[str, int]:
        """Queued jobs minus runners already serving them: per repo, or org-wide under "*"."""
        if self.org:
            return {"*": sum(len(jobs) for jobs in queued_by_repo.values()) - sum(1 for r in active_runners if r.target_repo in (self.org, ""))}
        return {repo: len(jobs) - sum(1 for r in active_runners if r.target_repo == repo) for repo, jobs in queued_by_repo.items()}

    def _spawn_for_job(self, repo: str, job: dict[str, Any]) -> tuple[str, RunnerDriver, str] | None:
        """Route `job` to a driver and spawn, falling back to the default driver on failure."""
        cfg = self.config
        driver, reason = select_driver_for_job(job, self.default_driver, self.drivers, cfg.auto_route_vm)
        arch = resolve_job_arch(job.get("labels", []), cfg.runner_arch)
        if not ensure_driver_runtime_assets(driver, arch):
            return None

        mounts = init_cache_dirs(cfg.host_cache_dir, arch, cfg.cache_enabled, scope=build_cache_scope(repo, job))
        spawn_args: dict[str, Any] = {
            **self._scope_args(repo),
            "arch": arch,
            "access_token": cfg.access_token,
            "cache_mounts": mounts,
            "proxies_enabled": cfg.proxies_enabled,
            # The job's runs-on labels, merged with the driver's defaults (#46).
            "labels": ",".join(job.get("labels", [])),
        }
        spawned_id = driver.spawn_runner(**spawn_args)
        if spawned_id:
            self._record_routing(job, driver, reason)
            return spawned_id, driver, arch
        if driver is self.default_driver or driver.name() == self.default_driver.name():
            return None  # already tried the default backend; nothing different to fall back to
        log_print(f"[Autoscaler] Driver '{driver.name()}' could not spawn runner for '{job.get('name')}' -- falling back to '{self.default_driver.name()}'.")
        if not ensure_driver_runtime_assets(self.default_driver, arch):
            return None
        spawned_id = self.default_driver.spawn_runner(**spawn_args)
        if not spawned_id:
            return None
        self._record_routing(job, self.default_driver, "container")
        return spawned_id, self.default_driver, arch

    def _record_routing(self, job: dict[str, Any], driver: RunnerDriver, reason: str) -> None:
        """Count a routing decision once per job, and only after its runner actually spawned.

        Counting before the spawn (as this used to) re-counted every queued job on every poll
        while it waited, e.g. for a golden-image build.
        """
        job_id = job.get("id")
        if job_id is not None:
            if job_id in self._recorded_jobs:
                return
            self._recorded_jobs[job_id] = None
            while len(self._recorded_jobs) > RECORDED_JOBS_LIMIT:
                self._recorded_jobs.popitem(last=False)
        dashboard_state.record_routing_decision(driver.is_vm, reason)

    # -- telemetry ---------------------------------------------------------------------

    def publish(self, all_runners: list[RunnerInfo], active_runners: list[RunnerInfo], queued_by_repo: dict[str, list[dict[str, Any]]]) -> None:
        """Push this cycle's fleet, quota and queue snapshot to the dashboard."""
        current = {runner.name for runner in active_runners}
        self.runner_job_meta = {k: v for k, v in self.runner_job_meta.items() if k in current}
        runners_for_dashboard = [{**runner.to_dict(), **self.runner_job_meta.get(runner.name, {})} for runner in all_runners]
        queued_jobs = [{**job, "repo": repo} for repo, jobs in queued_by_repo.items() for job in jobs]
        dashboard_state.update_fleet(
            runners=runners_for_dashboard,
            rate_limit=github_api.rate_limit_remaining,
            rate_limit_total=github_api.rate_limit_total,
            rate_limit_used=github_api.rate_limit_used,
            rate_limit_resource=github_api.rate_limit_resource,
            rate_limit_reset=github_api.rate_limit_reset,
            actions_billing=github_api.actions_billing,
            queued_jobs=queued_jobs,
            monitored_repos=self.tracked_repos,
            available_drivers=list(self.drivers),
            default_engine=self.default_driver.name(),
            version=__version__,
        )

    def run_once(self) -> None:
        """Run one full poll cycle: quota -> discovery -> collect -> scale -> publish."""
        now = self._clock()
        self.refresh_quota(now)
        self.discover(now)
        all_runners = self.collect()
        active_runners = [r for r in all_runners if r.state in ("running", "pending")]
        queued_by_repo = self.gather_queued_jobs()
        self.scale_jobs(queued_by_repo, active_runners)
        self.ensure_standby(active_runners)
        self.publish(all_runners, active_runners, queued_by_repo)

    def shutdown(self) -> None:
        """Destroy every managed runner on every driver."""
        for driver in self.drivers.values():
            driver.cleanup_all()


# -- process entry point ----------------------------------------------------------------


def validate_startup(config: Config) -> None:
    """Exit(1) with a clear message when required settings are missing."""
    if not config.access_token:
        log_print("[Autoscaler] Error: ACCESS_TOKEN is required for autoscaling.", file=sys.stderr)
        sys.exit(1)
    if config.cache_enabled and not config.host_cache_dir:
        log_print(
            "[Autoscaler] Error: CACHE_ENABLED=true but HOST_CACHE_DIR is not set. "
            "It must be a real path on the Docker HOST (not a path inside this "
            "container) -- e.g. HOST_CACHE_DIR=/Users/you/.local-github-runner/cache "
            "on macOS. Set it in .env, or set CACHE_ENABLED=false to run without "
            "persistent caching.",
            file=sys.stderr,
        )
        sys.exit(1)


def _init_dashboard(scaler: Scaler) -> DashboardServer | None:
    cfg = scaler.config
    dashboard_state.version = __version__
    dashboard_state.default_engine = scaler.default_driver.name()
    dashboard_state.available_drivers = list(scaler.drivers)
    dashboard_state.hybrid_routing_enabled = cfg.auto_route_vm
    dashboard_state.target_architectures = scaler.architectures
    dashboard_state.cache_dir = cfg.host_cache_dir
    dashboard_state.cache_enabled = cfg.cache_enabled
    dashboard_state.max_concurrency = cfg.max_runners
    dashboard_state.min_runners = cfg.min_runners
    if not cfg.dashboard_enabled:
        return None
    try:
        server = DashboardServer(host=cfg.dashboard_host, port=cfg.dashboard_port, drivers=scaler.drivers)
        server.start(blocking=False)
        return server
    except Exception as e:
        log_print(f"[Autoscaler] Warning: Could not start Dashboard server: {e}", file=sys.stderr)
        return None


def _print_banner(scaler: Scaler) -> None:
    cfg = scaler.config
    log_print("=" * 65)
    log_print(f" ⚡ RunZero v{__version__} — Dual-Engine Local GitHub Runner Autoscaler")
    log_print(f" Default Engine:   {scaler.default_driver.name().upper()}")
    log_print(f" Available Drivers: {', '.join(k.upper() for k in scaler.drivers)}")
    log_print(f" Hybrid Routing:   {'Enabled (Auto-detecting VM vs Container jobs)' if cfg.auto_route_vm else 'Disabled'}")
    log_print(f" Architectures:    {', '.join(a.upper() for a in scaler.architectures)}")
    log_print(f" Cache Directory:  {cfg.host_cache_dir} ({'Enabled' if cfg.cache_enabled else 'Disabled'})")
    log_print(f" Max Concurrency:  {cfg.max_runners} | Min Runners: {cfg.min_runners}")
    log_print(f" Active Filter:    Pushed within last {cfg.active_days} days")
    if cfg.dashboard_enabled:
        log_print(f" Web Dashboard:    http://localhost:{cfg.dashboard_port}")
    log_print("=" * 65)


def _handle_shutdown_signal(signum: int, frame: Any) -> None:
    """Request shutdown: wakes the poll wait and any in-progress rate-limit throttle."""
    log_print("\n[Autoscaler] Received shutdown signal. Cleaning up...")
    github_api.shutdown_event.set()


def main(config: Config | None = None) -> None:
    """Entrypoint: validate config, start the dashboard, then poll-scale-reconcile until signalled.

    Exits(1) on invalid configuration, a missing ACCESS_TOKEN, or caching enabled without a
    HOST_CACHE_DIR. On SIGINT/SIGTERM it finishes the current cycle, destroys every managed
    runner and stops the dashboard before returning.
    """
    if config is None:
        try:
            config = load_config()
        except ConfigError as exc:
            log_print(f"[Autoscaler] Configuration error: {exc}", file=sys.stderr)
            sys.exit(1)
    validate_startup(config)

    # One registry per process; the default driver is taken FROM it (#43), so golden-image
    # build locks and cooldowns are never split across duplicate driver instances.
    drivers = get_available_drivers(on_image_event=dashboard_state.report_image_build)
    default_driver = select_default_driver(drivers, config.runner_backend, on_image_event=dashboard_state.report_image_build)
    scaler = Scaler(config, drivers, default_driver)
    dashboard_server = _init_dashboard(scaler)
    _print_banner(scaler)

    signal.signal(signal.SIGINT, _handle_shutdown_signal)
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)

    while not github_api.shutdown_event.is_set():
        scaler.run_once()
        github_api.shutdown_event.wait(config.poll_interval)

    log_print("[Autoscaler] Stopping managed runners on shutdown...")
    scaler.shutdown()
    if dashboard_server:
        dashboard_server.stop()
    log_print("[Autoscaler] Shutdown complete.")


if __name__ == "__main__":  # pragma: no cover -- CLI entrypoint guard, only runs via `python autoscaler.py`
    main()
