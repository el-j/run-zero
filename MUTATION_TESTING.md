# Mutation Testing

RunZero is now implemented in Go + TypeScript. Mutation strategy focuses on
high-signal behavioral surfaces:

1. **Go lifecycle logic** (autoscaling, pruning, retry refresh semantics)
2. **Dashboard interaction flows** (retry controls, prune controls, telemetry behavior)
3. **API contract stability** (TypeSpec/OpenAPI + generated types)

## Current quality gate

The enforced baseline is:

```bash
make check
make e2e
```

- `make check` validates Go behavior and dashboard production correctness.
- `make e2e` validates end-to-end operator journeys through browser automation.

## Why this file exists

Historically, mutation guidance referenced a removed legacy runtime implementation.
This document is now aligned with the current Go/TypeScript codebase.
