# End-to-End Testing

This repository is now fully Go + TypeScript. The E2E suite validates the real
runtime surfaces that operators use:

- Website pages (Astro)
- Dashboard rendering and interaction flows (Vite app served as built assets)
- Lifecycle controls (retry + prune actions)

## What runs automatically

| Layer | Command | Scope |
|---|---|---|
| Go engine tests | `go test ./...` (via `make check`) | API handlers, autoscaler, drivers, reconciliation, state |
| Dashboard static validation | `cd web && pnpm run lint && pnpm run build` (via `make check`) | Type safety + production bundling |
| Website + dashboard E2E | `make e2e` | Browser journeys through website and dashboard lifecycle flows |

## E2E suite entrypoint

```bash
make e2e
```

This executes Playwright tests under [`website/e2e/`](./website/e2e/).

Two kinds of dashboard tests run there:

**UI tests** (`dashboard.spec.js`) serve the built dashboard with `vite preview`
and stub every API call in the browser. They cover layout and interaction:

- Telemetry panel opens/closes correctly and slides from the right on desktop layouts
- Failed completed jobs show failure diagnostics and support retry (`rerun-failed`)
- Prune control triggers cleanup endpoint and confirms user-facing success feedback
- Mobile header menu reveals the controls

**Operator journeys** (`journeys.spec.js`) stub nothing in the browser. They run
the real Go API server, autoscaler and dashboard build through
[`test/e2e/harness`](./test/e2e/harness/main.go), which wires them to a fake
GitHub API and an in-memory runner driver that names runners like OrbStack
(hostname-safe, lossy repo). The journey covers:

- A queued job gets exactly one runner, shown with its real `owner/repo` and run link
- When the job fails, the runner is pruned and the job appears under completed
  jobs with its diagnosis and annotations
- Retrying from the dashboard calls GitHub's `rerun-failed-jobs` endpoint

The harness needs Go (`go run -tags e2e ./test/e2e/harness`; the `e2e` build tag
keeps it out of `go test ./...`). Playwright starts it on port 49515 with the
fake GitHub API and its scenario controls on 49599.

## CI enforcement

GitHub Actions runs E2E in the `validate-dashboard-e2e` CI job
([`ci.yml`](./.github/workflows/ci.yml)) before image-build jobs.

## Manual hardware verification boundary

Host-hypervisor backends (OrbStack/WSL2/Multipass) depend on real local host capabilities.
Core lifecycle semantics for these paths are covered by Go tests and API/E2E flows, but
final host-specific performance/compatibility checks remain a local operator responsibility.
