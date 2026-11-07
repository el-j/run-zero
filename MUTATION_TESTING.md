# Mutation Testing

Line coverage says code ran; mutation testing says a test would notice if it
were wrong. [gremlins](https://github.com/go-gremlins/gremlins) changes the Go
code one operator at a time (`<` to `<=`, `==` to `!=`, `+` to `-`, …) and
re-runs the package's tests. A mutant the tests catch is **killed**; one they
miss **lived**, meaning some behaviour is not pinned by any test.

## Running it

```bash
make mutate                        # every Go package, fails below 97% efficacy
gremlins unleash --workers 1 --timeout-coefficient 30 ./pkg/driver   # one package
```

`make mutate` runs one package at a time with one worker. With several
workers the slower packages (`pkg/daemon`, `pkg/driver`, `pkg/github`) time
out instead of finishing, which hides surviving mutants. It is too slow for
every commit, so CI runs it weekly and on demand
([`mutation.yml`](./.github/workflows/mutation.yml)); `make check` keeps the
100% line-coverage gate on every commit.

The gate is **test efficacy** (killed ÷ (killed + lived)) per package,
`MUTATION_EFFICACY` in [`mk/go.mk`](./mk/go.mk), currently 97%.

## Current result

Every Go package kills every mutant except `pkg/github`, which kills 205 of
210. Its 5 survivors are **equivalent mutants**: changes no input can tell
apart from the original.

| Location | Why it cannot be killed |
|---|---|
| `client.go` quota check, `rl.Limit > 0` → `>= 0` | Differs only for a limit of 0 with a reset in the future, which GitHub never reports |
| `priority.go`, `p2 < p1` → `<=` | The two priorities are always distinct |
| `reconciler.go`, priority, time and job-ID ordering (`<` → `<=`) | Each comparison only runs on values already known to differ |

Mutants reported as **not covered** are not counted in efficacy. They are
either constants (for example `5 * time.Second` in a `var` or `const`), which
Go's coverage profile does not track, or conditions in `switch` cases that
gremlins maps to no covered block although `go test -cover` shows them run.

## Keeping it at 100%

When a mutant lives, prefer, in order:

1. **A test that pins the behaviour** — usually a missing boundary
   (exactly at a limit) or an untested branch.
2. **Simpler code**, when the mutant is equivalent because the code is
   redundant: `min`/`max` instead of a clamp, dropping a guard the callee
   already performs, removing a dead write. This removed most equivalent
   mutants so far.
3. **Documenting it above**, only when neither applies.

Tests that exist mainly to kill mutants live in each package's
`mutation_test.go`.

## Dashboard (TypeScript)

The dashboard is gated by Vitest with 100% statement, branch, function and
line coverage (`web/vite.config.ts`). It has no mutation testing yet; adding
[Stryker](https://stryker-mutator.io/) for `web/src` is the next step.
