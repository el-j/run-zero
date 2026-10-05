# Mutation Testing (issue #17)

Line coverage (see the `pytest --cov` output in CI, or `make test-suite`) only proves a line was
*executed* by some test -- not that a test would actually *fail* if that line's logic broke.
Mutation testing (via [mutmut](https://mutmut.readthedocs.io/)) answers that second question: it
introduces small, automated bugs ("mutants") into `src/` one at a time and re-runs the relevant
tests. A mutant that still passes ("survived") means no test actually asserts on that behavior.

## Running it locally (Differential & Fast)

Mutation testing runs locally using your development environment and is scoped **only to changed files** to keep feedback fast and avoid burning compute:

```bash
# Run mutation testing on only the changed files in your working branch / staged edits
make mutation-test

# Or run explicitly across all configured source paths
make mutation-test-all

# Generate or refresh trend dashboard artifacts
make mutation-report
```

Under the hood, `make mutation-test` executes `scripts/mutation_changed.py`, which:
1. Detects staged, unstaged, or branch-modified Python files under `src/` (comparing against `main`).
2. Filters out boilerplate/template files in `do_not_mutate` (such as `src/version.py`).
3. If no `src/` Python files changed, exits in milliseconds with `0` compute minutes consumed.
4. If files changed, dynamically isolates mutmut to mutate only those files.

## CI Wiring & Cloud Minute Conservation

To avoid wasting GitHub Actions runner minutes:
- **Automated CI triggers (schedule / PR) are disabled**: mutation testing is not run on standard pull requests or cron jobs.
- **Manual dispatch (`workflow_dispatch`)**: available in `.github/workflows/mutation-test.yml` if an explicit full cloud audit is ever needed.
- Developers run `make mutation-test` locally or via pre-push hooks (`RUNZERO_MUTATION_ON_PUSH=1 git push`).

- `reports/mutation/latest.md` (human-readable dashboard)
- `reports/mutation/history.json` (rolling trend points)
- `reports/mutation/mutmut-results.txt` (raw status output)
- `mutants/mutmut-cicd-stats.json` (machine-readable totals)

The dashboard is also appended to GitHub Actions' job summary for weekly drift visibility.

## Equivalent-mutant policy

Use the following policy when triaging survivors:

- `Missing assertion gap`: changed behavior is externally observable and should fail a test.
- `Equivalent mutant`: mutation only changes diagnostics, log text, or non-functional literals.

To reduce low-value noise, mutmut is configured with narrow `do_not_mutate` **file globs** for
template-heavy and version-metadata modules (currently `src/drivers/orbstack_templates.py` and
`src/version.py`). This keeps triage focused on control-flow and behavior mutations that can impact
real workloads.

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

Untangling which survivors are which, module by module, was systematically tracked across issues #30 through #36 and resolved as part of Milestone 2 and Milestone 8 (#60).

## Module Triage Outcomes & Equivalent-Mutant Classifications

The table below summarizes the triage classifications and equivalent-mutant justifications across all runtime modules:

| Module | Dominant Survivor Types | Classification & Justification | Validated In |
|---|---|---|---|
| `drivers/orbstack_templates.py` | Shell template script text, heredocs, env variable assignments | **Equivalent**: String-literal formatting templates. Changes do not alter Python runtime execution logic; excluded via `do_not_mutate`. | `tests/test_orbstack_driver.py` |
| `version.py` | Git fallback version strings, semantic version constant | **Equivalent**: Pure metadata constants; excluded via `do_not_mutate`. | `tests/test_version.py` |
| `drivers/orbstack_vm_driver.py` (#30) | VM boot retries, staging image names, IP discovery loops | **Killed / Equivalent**: Genuine control flow (readiness polling, retries) killed via `test_orbstack_driver.py`. Diagnostic log strings classified as equivalent. | `tests/test_orbstack_driver.py` |
| `dashboard/state.py` (#31) | Metrics dictionary keys, ring-buffer slice bounds, uptime math | **Killed / Equivalent**: State shape, queue broadcasting, and byte formatting math locked via targeted assertions. | `tests/test_dashboard_server.py` |
| `vm_bridge.py` (#32) | Route normalization, path segment extraction, action dispatch | **Killed / Equivalent**: Dispatch table mappings, route slash trimming, and destroy fallback assertions added. | `tests/test_vm_bridge.py` |
| `drivers/docker_driver.py` (#33) | Architecture label defaults, proxy URL branching, container removal flags | **Killed / Equivalent**: Explicit assertions verify `amd64`/`arm64` labels, network URL switching, and return codes. | `tests/test_docker_driver.py` |
| `autoscaler.py` (#33) | Scaling comparisons (`< MIN_RUNNERS`, `< MAX_RUNNERS`), modulo rotation | **Killed**: Added tests asserting cap enforcement, rotation order, and hybrid routing driver selection. | `tests/test_autoscaler_loop.py` |
| `bridge_driver.py` (#34) | Target backend passthrough, JSON error parsing, bearer auth headers | **Killed**: Assertions verify authentication forwarding and request timeout handling. | `tests/test_driver_factory.py` |
| `reconciler.py` (#34) | Active job ID matching, zombie threshold comparisons | **Killed**: Assertions lock runner name prefix matching, active job lookups, and unregistration refusal guards. | `tests/test_reconciler.py` |
| `github_api.py` (#34) | Pagination URL queries, rate limit quota extraction, HTTP error status | **Killed**: Added list pagination assertions and rate limit header parser tests. | `tests/test_github_api.py` |
| `config.py` | Integer/boolean parsing bounds, choice validation | **Killed**: String boolean mappings, integer bounds check, and architecture alias normalization locked. | `tests/test_config.py` |
| `http_security.py` | Host header parsing, IP address validation, request length limits | **Killed**: Rejection status codes (400, 413, 421) and hostname normalizations verified. | `tests/test_http_security.py` |
| `workflow_inspector.py` | YAML indentation calculation, quotation stripping, matrix suffix base | **Killed**: Conditionals (`or` vs `and`), matrix base name parsing, and service trigger detection verified. | `tests/test_workflow_inspector.py` |

