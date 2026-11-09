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
line coverage (`web/vite.config.ts`) on every commit, and mutation-tested with
[Stryker](https://stryker-mutator.io/) weekly and on demand:

```bash
make mutate-web          # or: cd web && pnpm run mutate
```

The run takes about 25 minutes, writes an HTML report to
`web/reports/mutation/index.html`, and keeps an incremental result in
`web/reports/stryker-incremental.json`. Later runs only retest mutants in
changed code. Both files are git-ignored. The weekly
[`mutation.yml`](./.github/workflows/mutation.yml) job uploads the report as
an artifact.

`web/stryker.config.mjs` points `tsconfigFile` at a file that does not exist.
Stryker rewrites the sandbox's tsconfig through the TypeScript JS API, which
TypeScript 7 no longer ships, and our tsconfig has nothing to rewrite.

### Current result

The first full run scored **72.47%**: 2875 killed, 81 timed out, 1123 survived
out of 4087 mutants. The `break` threshold is set to 72, so the score cannot
fall, and is raised as survivors are killed.

| Area | Score |
|---|---|
| `render/jobs.ts` | 43.8% |
| `render/runners.ts` | 56.4% |
| `render/queue.ts` | 58.7% |
| `render/repos.ts` | 65.8% |
| `components/` | 68.1% |
| `handlers/` | 82.0% |
| `api/client.ts` | 85.4% |

By kind, 407 survivors are string literals (class names and text in rendered
markup), 285 conditional expressions, 125 logical operators and 55
comparisons. Those last three are untested branches. The render modules are
covered line by line but their output is rarely asserted, which is the main
gap.
