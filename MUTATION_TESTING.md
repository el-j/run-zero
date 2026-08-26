# Mutation Testing (issue #17)

Line coverage (see the `pytest --cov` output in CI, or `make test-suite`) only proves a line was
*executed* by some test -- not that a test would actually *fail* if that line's logic broke.
Mutation testing (via [mutmut](https://mutmut.readthedocs.io/)) answers that second question: it
introduces small, automated bugs ("mutants") into `src/` one at a time and re-runs the relevant
tests. A mutant that still passes ("survived") means no test actually asserts on that behavior.

## Running it locally

```bash
make mutation-test
```

This runs mutmut inside a disposable `python:3.11-slim` container (same pattern as
`make test-suite`), so it needs nothing installed on the host beyond Docker. It is intentionally
**not** part of `make test-suite` or the default CI job -- a full mutation run is far slower than
the unit-test suite (see [CI wiring](#ci-wiring) below).

## Configuration notes

`pyproject.toml`'s `[tool.mutmut]` section has two non-obvious requirements that broke a prior,
never-actually-run configuration (see issue #17's original finding):

- **`source_paths` must be a TOML array**, e.g. `["src/"]`, not a bare string `"src/"`. mutmut 3.x
  does `[Path(p) for p in source_paths]` -- a bare string iterates character-by-character
  (`'s'`, `'r'`, `'c'`, `'/'`), and `Path('/')` then makes mutmut try to copy the entire root
  filesystem into its `mutants/` working copy.
- **`pytest_add_cli_args = ["--no-cov"]`** is required because mutmut 3.x runs pytest in-process,
  inheriting `[tool.pytest.ini_options]`'s `addopts` -- including `--cov-fail-under=100`. Each
  mutant run only executes the narrow subset of tests mutmut's dependency tracking determined
  relevant to the mutated line, which would almost never itself reach 100% coverage of the whole
  `src/` tree, so without `--no-cov` that unrelated gate would fail (and mark "killed") almost
  every mutant regardless of whether a real assertion caught the behavior change.
- **`also_copy = ["Makefile"]`** is required because `tests/test_blackbox_cli.py` shells out to a
  real `make` binary against the repo root, computed via `__file__` -- which resolves *inside*
  mutmut's `mutants/` sandbox copy once that test file itself gets copied there. Without this,
  mutmut's own baseline run fails with `make: *** No rule to make target 'cache-size'`, because
  the Makefile was never mirrored into the sandbox.

## CI wiring

Wired into `.github/workflows/mutation-test.yml`:

- **Weekly schedule** (Monday 06:00 UTC) -- baseline drift visibility without slowing down every
  push.
- **Pull requests targeting `main`** -- a release gate, so a real regression in surviving mutants
  is visible before a release-bound merge, without slowing down `develop`-bound day-to-day PRs.
- **Manual dispatch** (`workflow_dispatch`) for on-demand runs.

The `make mutation-test` target no longer swallows mutmut's exit code with `|| true` -- a
mutant-survival regression now fails the job for real.

## Baseline

First real completed run against `src/` in full (315 unit tests, 19 mutated files), recorded here
for future drift comparison:

| | Count | % |
|---|---|---|
| Total mutants | 5157 | 100% |
| Killed | 2502 | 48.5% |
| Survived | 2643 | 51.3% |
| Timeout | 12 | 0.2% |

**51% survival is an honest, real number, not a target already met.** It's dominated by two very
different things mixed together:

- Genuine missing-assertion gaps -- e.g. an `or` mutated to `and` in a conditional with no test
  distinguishing the two branches (see issue #22 for a concrete example from
  `workflow_inspector.py`).
- Low-value/likely-equivalent mutants -- e.g. mutmut's automatic string-literal mutation on a
  default-parameter value nothing ever asserts against (`"ubuntu:24.04"` -> `"XXubuntu:24.04XX"`).
  Killing every one of these would mean writing tests whose only purpose is satisfying the
  mutation tool, not verifying real behavior.

Untangling which survivors are which, module by module, is real, non-trivial work -- it is
deliberately **not** attempted wholesale in the PR that first got this tooling actually running
(see #17). It's tracked as its own scoped follow-up in **issue #22**, which also has the
per-module survivor breakdown (worst: `drivers/orbstack_vm_driver.py` at 467, `dashboard/state.py`
at 338, `vm_bridge.py` at 310).
