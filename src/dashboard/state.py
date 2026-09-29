"""
RunZero Dashboard State & Telemetry Aggregator
Maintains thread-safe in-memory metrics, fleet status, log ring buffer, and SSE broadcasting.
"""

from __future__ import annotations

import collections
import os
import queue
import shutil
import threading
import time
from typing import Any


class DashboardState:
    """Thread-safe, process-wide singleton holding fleet/telemetry state and broadcasting it to SSE clients.

    A single instance (`dashboard_state`, defined at the bottom of this module) is imported and
    mutated by both `autoscaler.py`'s poll loop and the dashboard HTTP handlers -- every public
    method that reads/writes shared state takes `self._lock`.
    """

    def __init__(self, max_log_lines: int = 500):
        """Initialize state to its startup defaults; the real values arrive via `update_fleet()` on the first poll."""
        self._lock = threading.Lock()
        self.max_log_lines = max_log_lines
        self.log_buffer: collections.deque = collections.deque(maxlen=max_log_lines)
        self.subscribers: list[queue.Queue] = []

        # Telemetry & Fleet State
        self.version = "0.1.0"
        self.start_time = time.time()
        self.autoscaler_status = "running"
        self.default_engine = "docker"
        self.available_drivers: list[str] = ["docker"]
        self.hybrid_routing_enabled = True
        self.target_architectures: list[str] = ["arm64", "amd64"]
        self.cache_dir = os.getenv("HOST_CACHE_DIR", "")
        self.cache_enabled = True
        self.max_concurrency = 4
        self.min_runners = 0
        self.github_rate_limit_remaining: int | None = None
        self.github_rate_limit_total: int | None = None
        self.github_rate_limit_used: int | None = None
        self.github_rate_limit_resource: str | None = None
        self.github_rate_limit_reset: int | None = None
        self.github_actions_billing: dict[str, Any] = {}
        self.monitored_repos: list[str] = []
        self.total_queued_jobs = 0
        self.queued_jobs: list[dict[str, Any]] = []
        self.active_runners: list[dict[str, Any]] = []

        # Routing telemetry counters
        self.routing_docker_jobs: int = 0
        self.routing_vm_jobs: int = 0
        self.routing_triggers: dict[str, int] = {"services": 0, "dind": 0, "browser": 0, "e2e": 0, "systemd": 0, "custom_label": 0}

        # Golden image build status, keyed by "<driver>:<arch>:<profile-or-base>" -- see
        # report_image_build(). Populated by driver on_image_event callbacks (autoscaler.py
        # wires this in at driver construction time) so a build failure like a missing
        # build-context directory shows up here instead of only in scrolling logs.
        self.image_builds: dict[str, dict[str, Any]] = {}

        # Cache telemetry
        self.cache_sizes: dict[str, str] = {
            "npm": "0 B",
            "yarn": "0 B",
            "pnpm": "0 B",
            "pip": "0 B",
            "uv": "0 B",
            "go-mod": "0 B",
            "go-build": "0 B",
            "cargo": "0 B",
            "toolcache": "0 B",
            "total_host": "0 B",
            "verdaccio": "0 B",
            "athens": "0 B",
            "docker_mirror": "0 B",
            "apt_cacher": "0 B",
        }

    @property
    def routing_stats(self) -> dict[str, Any]:
        """Return the Docker-vs-VM job routing counters and per-trigger breakdown as a plain dict."""
        return {"docker_jobs": self.routing_docker_jobs, "vm_jobs": self.routing_vm_jobs, "vm_triggers_breakdown": dict(self.routing_triggers)}

    def append_log(self, line: str) -> None:
        """Add a log line to ring buffer and broadcast to active SSE subscribers."""
        line = line.rstrip()
        if not line:
            return
        timestamp = time.strftime("%H:%M:%S")
        entry = {"timestamp": timestamp, "message": line}

        with self._lock:
            self.log_buffer.append(entry)
            dead_subs = []
            for sub in self.subscribers:
                try:
                    sub.put_nowait({"type": "log", "data": entry})
                except queue.Full:
                    dead_subs.append(sub)
            for ds in dead_subs:
                if ds in self.subscribers:
                    self.subscribers.remove(ds)

    def subscribe(self) -> queue.Queue:
        """Register a new SSE client queue."""
        q: queue.Queue = queue.Queue(maxsize=100)
        with self._lock:
            self.subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        """Unregister an SSE client queue."""
        with self._lock:
            if q in self.subscribers:
                self.subscribers.remove(q)

    def broadcast_state(self) -> None:
        """Push a state snapshot to all SSE clients."""
        snapshot = self.get_snapshot()
        with self._lock:
            dead_subs = []
            for sub in self.subscribers:
                try:
                    sub.put_nowait({"type": "state", "data": snapshot})
                except queue.Full:
                    dead_subs.append(sub)
            for ds in dead_subs:
                if ds in self.subscribers:
                    self.subscribers.remove(ds)

    def update_fleet(
        self,
        runners: list[Any],
        rate_limit: int | None,
        queued_jobs: list[dict[str, Any]],
        monitored_repos: list[str],
        available_drivers: list[str],
        rate_limit_total: int | None = None,
        rate_limit_used: int | None = None,
        rate_limit_resource: str | None = None,
        rate_limit_reset: int | None = None,
        actions_billing: dict[str, Any] | None = None,
        default_engine: str = "docker",
        version: str = "0.1.0",
    ) -> None:
        """Replace the fleet/config snapshot with this poll's data, refresh cache sizes, and broadcast to SSE clients.

        `runners` entries may be `RunnerInfo` (or anything with `.to_dict()`), plain dicts, or
        arbitrary objects (stringified as a fallback); each gets a computed `duration` field
        added based on its `created_at`, or "active" if that isn't known.
        """
        with self._lock:
            self.version = version
            self.default_engine = default_engine
            self.available_drivers = available_drivers
            self.github_rate_limit_remaining = rate_limit
            self.github_rate_limit_total = rate_limit_total
            self.github_rate_limit_used = rate_limit_used
            self.github_rate_limit_resource = rate_limit_resource
            self.github_rate_limit_reset = rate_limit_reset
            self.github_actions_billing = dict(actions_billing or {})
            self.monitored_repos = monitored_repos
            self.queued_jobs = queued_jobs
            self.total_queued_jobs = len(queued_jobs)

            # Map runners
            runner_list = []
            now = time.time()
            for r in runners:
                if hasattr(r, "to_dict"):
                    d = r.to_dict()
                elif isinstance(r, dict):
                    d = r
                else:
                    d = {"id": str(r), "name": str(r)}

                # Calculate elapsed runtime
                created_at = d.get("created_at")
                if created_at and isinstance(created_at, (int, float)) and created_at > 0:
                    elapsed = max(0, int(now - created_at))
                    mins, secs = divmod(elapsed, 60)
                    hrs, mins = divmod(mins, 60)
                    d["duration"] = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs else f"{mins:02d}:{secs:02d}"
                else:
                    d["duration"] = "active"

                runner_list.append(d)
            self.active_runners = runner_list

        # Refresh cache sizes asynchronously or cheaply
        self._refresh_cache_metrics()
        self.broadcast_state()

    def record_routing_decision(self, engine: str, trigger: str | None = None) -> None:
        """Increment the Docker-vs-VM job counter for `engine`, and classify `trigger` into a bucket if it's a VM job.

        `trigger` is matched by substring against a fixed set of known reasons (service containers,
        Docker-in-Docker, browser/e2e testing, systemd) and falls into "custom_label" otherwise.
        """
        with self._lock:
            if "vm" in engine.lower():
                self.routing_vm_jobs += 1
                if trigger:
                    t = trigger.lower()
                    if "service" in t:
                        self.routing_triggers["services"] += 1
                    elif "dind" in t or "docker" in t:
                        self.routing_triggers["dind"] += 1
                    elif "browser" in t or "chrome" in t or "lighthouse" in t:
                        self.routing_triggers["browser"] += 1
                    elif "e2e" in t or "test" in t:
                        self.routing_triggers["e2e"] += 1
                    elif "systemd" in t:
                        self.routing_triggers["systemd"] += 1
                    else:
                        self.routing_triggers["custom_label"] += 1
            else:
                self.routing_docker_jobs += 1

    def report_image_build(self, event: dict[str, Any]) -> None:
        """Record a golden-image build status transition and broadcast it to SSE clients.

        `event` is the structured dict drivers emit via `_report_image_event()`
        (`driver`, `arch`, `profile`, `status`, `detail`, `ts`); missing/malformed events are
        dropped rather than raising, since this runs on driver background-build threads where
        an unhandled exception would be silent and hard to diagnose.
        """
        driver = event.get("driver")
        arch = event.get("arch")
        if not driver or not arch:
            return
        profile = event.get("profile") or "base"
        key = f"{driver}:{arch}:{profile}"

        with self._lock:
            self.image_builds[key] = {
                "driver": driver,
                "arch": arch,
                "profile": event.get("profile"),
                "status": event.get("status", "unknown"),
                "detail": event.get("detail", ""),
                "ts": event.get("ts", time.time()),
            }
        self.broadcast_state()

    def _format_bytes(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / (1024**2):.1f} MB"
        else:
            return f"{size_bytes / (1024**3):.2f} GB"

    def _get_dir_size(self, path: str) -> int:
        if not path or not os.path.isdir(path):
            return 0
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total += os.path.getsize(fp)
        except OSError:
            return total
        return total

    def _go_build_dirs(self, cache_root: str) -> list[str]:
        """Every real go-build cache directory under `cache_root`.

        `cache_manager.init_cache_dirs()` puts go-build under a per-job
        `build-cache/<scope>/go-build/` directory whenever a job scope is given (the normal,
        repo-job case -- see `autoscaler.build_cache_scope()`), or the flat `go-build/` only
        for unscoped (ORG-mode) spawns. Measuring/clearing just the flat path -- as this
        previously did -- always reported/cleared an empty, unused directory once scoping
        landed, while the actual (now correctly reused) data sat invisible under
        `build-cache/*/go-build/`.
        """
        dirs = []
        flat = os.path.join(cache_root, "go-build")
        if os.path.isdir(flat):
            dirs.append(flat)
        build_cache_root = os.path.join(cache_root, "build-cache")
        if os.path.isdir(build_cache_root):
            try:
                for scope_name in os.listdir(build_cache_root):
                    scoped = os.path.join(build_cache_root, scope_name, "go-build")
                    if os.path.isdir(scoped):
                        dirs.append(scoped)
            except OSError:
                pass
        return dirs

    def _refresh_cache_metrics(self) -> None:
        cache_root = self.cache_dir or os.path.expanduser("~/.local-github-runner/cache")
        if os.path.isdir(cache_root):
            # Keys match the display names already used by the webui/API; paths match the
            # real subdirectory names cache_manager.init_cache_dirs() actually creates and
            # mounts (previously "go-mod"/"cargo-registry"/"toolcache" here, none of which
            # exist on disk -- init_cache_dirs creates "go-pkg"/"rust"/"hostedtoolcache" --
            # so these three always read back as empty regardless of real usage).
            categories = {
                "npm": os.path.join(cache_root, "npm"),
                "yarn": os.path.join(cache_root, "yarn"),
                "pnpm": os.path.join(cache_root, "pnpm"),
                "pip": os.path.join(cache_root, "pip"),
                "uv": os.path.join(cache_root, "uv"),
                "go-mod": os.path.join(cache_root, "go-pkg"),
                "cargo": os.path.join(cache_root, "rust"),
                "toolcache": os.path.join(cache_root, "hostedtoolcache"),
            }
            total_host = 0
            for name, path in categories.items():
                sz = self._get_dir_size(path)
                total_host += sz
                self.cache_sizes[name] = self._format_bytes(sz)

            go_build_size = sum(self._get_dir_size(p) for p in self._go_build_dirs(cache_root))
            total_host += go_build_size
            self.cache_sizes["go-build"] = self._format_bytes(go_build_size)

            self.cache_sizes["total_host"] = self._format_bytes(total_host)

    def clean_cache(self, category: str = "all") -> dict[str, Any]:
        """Clear specific or all host package caches."""
        cache_root = self.cache_dir or os.path.expanduser("~/.local-github-runner/cache")
        category = category.lower().strip()
        cleared = []

        # See _refresh_cache_metrics() for why these paths (not "go-mod"/"cargo-registry"/
        # "toolcache") are the real on-disk directory names.
        mapping = {
            "npm": os.path.join(cache_root, "npm"),
            "yarn": os.path.join(cache_root, "yarn"),
            "pnpm": os.path.join(cache_root, "pnpm"),
            "pip": os.path.join(cache_root, "pip"),
            "uv": os.path.join(cache_root, "uv"),
            "go-mod": os.path.join(cache_root, "go-pkg"),
            "cargo": os.path.join(cache_root, "rust"),
            "toolcache": os.path.join(cache_root, "hostedtoolcache"),
        }

        def _clear_go_build() -> None:
            go_build_paths = self._go_build_dirs(cache_root)
            for path in go_build_paths:
                shutil.rmtree(path, ignore_errors=True)
                os.makedirs(path, exist_ok=True)
            if go_build_paths:
                cleared.append("go-build")

        if category in ("all", "host"):
            for name, path in mapping.items():
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)
                    os.makedirs(path, exist_ok=True)
                    cleared.append(name)
            _clear_go_build()
        elif category == "go-build":
            _clear_go_build()
        elif category in mapping:
            path = mapping[category]
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
                os.makedirs(path, exist_ok=True)
                cleared.append(category)

        self._refresh_cache_metrics()
        self.broadcast_state()
        return {"status": "success", "cleared": cleared}

    def get_snapshot(self) -> dict[str, Any]:
        """Return a complete JSON-serializable state snapshot."""
        with self._lock:
            uptime_secs = max(0, int(time.time() - self.start_time))
            mins, secs = divmod(uptime_secs, 60)
            hrs, mins = divmod(mins, 60)
            days, hrs = divmod(hrs, 24)
            uptime_str = f"{days}d {hrs}h {mins}m" if days else f"{hrs}h {mins}m {secs}s"

            return {
                "version": self.version,
                "uptime": uptime_str,
                "uptime_seconds": uptime_secs,
                "status": self.autoscaler_status,
                "default_engine": self.default_engine,
                "available_drivers": self.available_drivers,
                "hybrid_routing": self.hybrid_routing_enabled,
                "architectures": self.target_architectures,
                "concurrency": {"active": len(self.active_runners), "max": self.max_concurrency, "min": self.min_runners},
                "github": {
                    "rate_limit_remaining": self.github_rate_limit_remaining,
                    "rate_limit_total": self.github_rate_limit_total,
                    "rate_limit_used": self.github_rate_limit_used,
                    "rate_limit_resource": self.github_rate_limit_resource,
                    "rate_limit_reset": self.github_rate_limit_reset,
                    "actions_billing": self.github_actions_billing,
                    "monitored_repos": self.monitored_repos,
                    "queued_jobs_count": self.total_queued_jobs,
                    "queued_jobs": self.queued_jobs,
                },
                "runners": self.active_runners,
                "routing_stats": {
                    "docker_jobs": self.routing_docker_jobs,
                    "vm_jobs": self.routing_vm_jobs,
                    "vm_triggers_breakdown": dict(self.routing_triggers),
                },
                "cache": {"enabled": bool(self.cache_enabled), "dir": str(self.cache_dir) if self.cache_dir is not None else "", "sizes": self.cache_sizes},
                "image_builds": list(self.image_builds.values()),
                "recent_logs": list(self.log_buffer),
            }


# Global singleton instance
dashboard_state = DashboardState()
