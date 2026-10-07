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

Current dashboard journeys covered:

- Telemetry panel opens/closes correctly and slides from the right on desktop layouts
- Failed completed jobs show failure diagnostics and support retry (`rerun-failed`)
- Prune control triggers cleanup endpoint and confirms user-facing success feedback

## CI enforcement

GitHub Actions runs E2E in the `validate-dashboard-e2e` CI job
([`ci.yml`](./.github/workflows/ci.yml)) before image-build jobs.

## Manual hardware verification boundary

Host-hypervisor backends (OrbStack/WSL2/Multipass) depend on real local host capabilities.
Core lifecycle semantics for these paths are covered by Go tests and API/E2E flows, but
final host-specific performance/compatibility checks remain a local operator responsibility.
