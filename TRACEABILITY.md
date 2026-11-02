# Traceability Matrix

Every feature RunZero advertises, mapped to the code that implements it, the
tests that verify it, and where it is documented. Gaps are listed under
[Unlinked](#unlinked) instead of being hidden.

`test/traceability` keeps this file honest: it fails when a path cited here no
longer exists, or when a setting the daemon reads is missing from the
README's configuration table.

**Status:** ✅ implemented, tested and documented · ⚠️ partly (see notes) ·
❌ advertised but not implemented.

Claimed in: **R** = `README.md`, **W** = website (`website/src`), **E** = `E2E_TESTING.md`.

## Features

| ID | Feature | Claimed in | Code | Tests | Status |
|---|---|---|---|---|---|
| F-01 | Queue-driven autoscaling: one ephemeral runner per queued job, torn down when the job completes | R, W | `pkg/daemon/scale_cycle.go`, `pkg/daemon/autoscaler.go` | `pkg/daemon/scale_cycle_test.go`, `pkg/daemon/autoscaler_test.go`, `website/e2e/journeys.spec.js` | ✅ |
| F-02 | Repo auto-discovery (owner, org or explicit list, active-days filter) | R, W | `pkg/github/discovery.go`, `pkg/github/poller.go` | `pkg/github/discovery_test.go`, `pkg/github/poller_test.go` | ✅ |
| F-03 | Org mode: runners register at org scope | R | `pkg/github/registration.go` | `pkg/github/registration_test.go` | ✅ |
| F-04 | Docker container backend | R, W | `pkg/driver/docker.go`, `pkg/driver/docker_ops.go` | `pkg/driver/docker_test.go` | ✅ |
| F-05 | OrbStack VM backend, direct or through the host VM bridge | R, W | `pkg/driver/orbstack.go`, `pkg/driver/orbstack_ops.go`, `pkg/driver/bridge.go`, `pkg/bridge/server.go`, `cmd/runzero/bridge.go` | `pkg/driver/orbstack_test.go`, `pkg/driver/bridge_test.go`, `pkg/bridge/server_test.go` | ✅ |
| F-06 | WSL2 backend | R | — | — | ❌ see U-01 |
| F-07 | Canonical Multipass backend | R | — | — | ❌ see U-01 |
| F-08 | Hybrid auto-routing of jobs to VMs by label (`AUTO_ROUTE_VM`, `VM_TRIGGER_LABELS`) | R, W | `pkg/driver/router.go`, `pkg/daemon/scale_cycle.go` | `pkg/driver/router_test.go`, `pkg/daemon/scale_cycle_test.go` | ✅ |
| F-09 | Golden VM base images, cloned per job (`build-vm-base`) | R, W | `pkg/builder/builder.go`, `pkg/builder/lifecycle.go`, `cmd/runzero/build_vm.go` | `pkg/builder/builder_test.go`, `pkg/builder/lifecycle_test.go` | ✅ |
| F-10 | Runner image builds from the dashboard, including rebuild of a missing image | W | `pkg/builder/manager.go`, `pkg/builder/rebuild.go`, `pkg/api/handlers_images.go` | `pkg/builder/manager_test.go`, `pkg/builder/rebuild_test.go`, `pkg/api/handlers_images_test.go` | ✅ |
| F-11 | Native ARM64 with AMD64 emulation; per-repo native-arch override (`NATIVE_ARCH_OVERRIDE`) | R, W | `pkg/arch/override.go`, `pkg/daemon/scale_cycle.go` | `pkg/arch/override_test.go` | ✅ |
| F-12 | Runner CPU and memory sizing (`RUNNER_CPUS`, `RUNNER_MEMORY`, or job labels such as `4cpu-8gb`) | R, W | `pkg/sizing/parsers.go`, `pkg/sizing/label_sizing.go`, `pkg/daemon/scale_cycle.go` | `pkg/sizing/sizing_test.go`, `pkg/daemon/scale_cycle_test.go` | ✅ |
| F-13 | Persistent per-runner package caches (`CACHE_ENABLED`, `HOST_CACHE_DIR`) | R, W | `pkg/cache/manager.go` | `pkg/cache/cache_test.go` | ✅ |
| F-14 | Cache size stats and purge from the dashboard | W | `pkg/cache/stats.go`, `pkg/cache/purge.go`, `pkg/api/handlers_cache.go` | `pkg/cache/cache_test.go`, `pkg/api/cache_test.go` | ✅ |
| F-15 | Local proxy registries (apt-cacher-ng, Verdaccio, Athens, Docker mirror, devpi, kellnr) | R, W | `docker-compose.yml`, `docker/start.sh` | — (manual `make cache-smoke`) | ⚠️ no automated test |
| F-16 | Reaping of idle, unregistered and stale-busy runners (`RUNNER_BUSY_TIMEOUT_SECONDS`) | R, W | `pkg/reaper/reaper.go`, `pkg/reaper/classify.go`, `pkg/daemon/init.go` | `pkg/reaper/reaper_test.go`, `pkg/reaper/cov_classify_test.go`, `pkg/daemon/scale_cycle_test.go` | ✅ |
| F-17 | Zombie healing: cancel jobs orphaned on dead runners | R, W | — | — | ❌ see U-02 |
| F-18 | Warm standby pool (`MIN_RUNNERS`) | R | `pkg/daemon/standby.go`, `pkg/daemon/scale_cycle.go` | `pkg/daemon/standby_test.go` | ✅ |
| F-19 | Adaptive GitHub API rate limiting: ETag caching, quota refresh every `RATE_LIMIT_REFRESH_INTERVAL`, polling slowed 2×/4×/8× as the quota drops below 50/20/10%, hard stop when exhausted | R, W | `pkg/github/client.go`, `pkg/daemon/autoscaler.go`, `pkg/daemon/pacing.go` | `pkg/github/client_etag_test.go`, `pkg/github/client_test.go`, `pkg/daemon/pacing_test.go` | ✅ |
| F-20 | Real-time dashboard over server-sent events | R, W | `pkg/api/handlers_stream.go`, `pkg/state/events.go`, `web/src/stream.ts` | `pkg/state/broker_test.go`, `web/src/stream.test.ts` | ✅ |
| F-21 | Completed-job history with failure diagnosis and annotations, refreshed within 30 s of a runner finishing | R, E | `pkg/github/history.go`, `pkg/state/history.go`, `pkg/daemon/autoscaler.go` | `pkg/github/history_test.go`, `pkg/daemon/history_refresh_test.go`, `website/e2e/journeys.spec.js` | ✅ |
| F-22 | Retry, rerun and cancel workflow runs from the dashboard | R, E | `pkg/github/workflow.go`, `pkg/api/handlers_workflow_actions.go` | `pkg/github/workflow_test.go`, `pkg/api/handlers_workflow_actions_test.go`, `website/e2e/journeys.spec.js` | ✅ |
| F-23 | Stop and prune runners from the dashboard; retained runner logs | R, E | `pkg/api/handlers_runner_actions.go`, `pkg/driver/prune.go` | `pkg/api/handlers_runner_actions_test.go`, `pkg/api/runner_log_test.go`, `website/e2e/dashboard.spec.js` | ✅ |
| F-24 | Open a terminal into a runner | W | `pkg/bridge/handlers.go`, `web/src/terminal.ts` | `pkg/bridge/coverage_test.go` | ⚠️ no dashboard test for `web/src/terminal.ts` |
| F-25 | Repo priority and pause | R | `pkg/github/priority.go`, `pkg/github/priority_store.go` | `pkg/github/priority_test.go` | ✅ |
| F-26 | Live settings edited from the dashboard, persisted to `.env` | W | `pkg/api/handlers_settings.go`, `pkg/settings/manager.go` | `pkg/api/settings_test.go`, `pkg/settings/settings_test.go`, `web/src/settings.test.ts` | ✅ |
| F-27 | GitHub Actions minutes panel | R | `pkg/github/registration.go` | `pkg/github/registration_test.go` | ✅ |
| F-28 | GitLab runners and jobs, multi-instance providers (`PROVIDERS_CONFIG`) | R | `pkg/gitlab/runners.go`, `pkg/gitlab/jobs.go`, `pkg/provider/manager.go`, `pkg/provider/config.go` | `pkg/gitlab/runners_test.go`, `pkg/gitlab/jobs_test.go`, `pkg/provider/manager_test.go` | ✅ |
| F-29 | `runzero doctor` host diagnostics | R | `pkg/doctor/checks.go`, `cmd/runzero/doctor_cmd.go` | `pkg/doctor/checks_test.go` | ✅ |
| F-30 | Control-plane API matches the TypeSpec contract | R | `spec/main.tsp`, `pkg/api/server.go` | `pkg/api/spec_drift_test.go` | ✅ |
| F-31 | "100% mutation tested" | W | — | — | ❌ see U-05 |

## Unlinked

### Advertised but not implemented

- **U-01 WSL2 and Multipass backends** (F-06, F-07). `RUNNER_BACKEND` accepts
  `wsl2`, `wsl`, `windows`, `multipass` and `canonical-multipass`
  (`pkg/config/validation.go`), but the Go engine has no driver for them:
  `pkg/daemon/init.go` only builds Docker and OrbStack drivers, so these values
  silently fall back to the router's default.
- **U-02 Zombie job cancellation** (F-17). The README and website say orphaned
  jobs on dead runners are cancelled. The reaper (`pkg/reaper/reaper.go`)
  stops local runners and deletes offline registrations; it never cancels a job.
- **U-05 Mutation testing** (F-31). The website claims 100% mutation testing;
  `MUTATION_TESTING.md` describes `make check` and `make e2e` only, and no
  mutation tool runs.

### Code that no feature reaches

- **U-08 `pkg/parity`** (VM vs container toolchain parity) is imported by no
  binary; `pkg/inspector` is imported only by `pkg/parity`.

### Settings missing from the website's environment reference

The README configuration table lists every setting (enforced by
`test/traceability`). The website page
`website/src/components/docs/DocsEnvReference.astro` does not yet cover
`AUTO_DISCOVER_REPOS`, `CACHE_ENABLED`, `DASHBOARD_ENABLED`, `DASHBOARD_HOST`,
`DASHBOARD_PORT`, `DISCOVERY_INTERVAL`, `GITHUB_TOKEN`, `HOST_CACHE_DIR`,
`MIN_RUNNERS`, `ORG`, `POLL_INTERVAL`, `REPO`, `REPOS`, `REPO_PRIORITY`,
`RUNNER_BUSY_TIMEOUT_SECONDS` and `VM_TRIGGER_LABELS` (**U-10**).

_Resolved: U-06 `RATE_LIMIT_REFRESH_INTERVAL` and U-07 `RUNNER_BUSY_TIMEOUT_SECONDS` are applied; U-09 label-based sizing is wired into spawning (F-12); U-03 the `MIN_RUNNERS` standby pool is implemented (F-18); U-04 polling is paced by the API quota (F-19)._
