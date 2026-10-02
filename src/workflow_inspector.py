"""
Lightweight, dependency-free workflow-YAML inspector.

The router (router.py) needs to know whether a queued job declares a
`services:`/`container:` block -- those jobs need a real, non-containerized
execution environment (a full VM) for GitHub's own `services:` networking
model (job steps reach a service container via `localhost:<published-port>`)
to work at all. A job running as ANOTHER Docker container (this fleet's
"docker" driver) can't satisfy that: the service container is a sibling on
the Docker host, not reachable at the runner container's own "localhost"
unless the runner container shares the host network namespace, which this
fleet deliberately does NOT do for the docker driver (see docker/start.sh
and DOCKER_NETWORK in .env -- host networking was traded away to fix
concurrent jobs colliding on the same fixed service port).

Deliberately avoids a real YAML parser (PyYAML etc.) to keep this project's
zero-third-party-dependency footprint -- GitHub Actions workflow files use
a very regular, predictable indentation style, so a structural (not
semantic) indentation scan is enough to answer one narrow question: "does
the job whose rendered `name:` is X have a `services:` or `container:` key
as a direct child?"

Known limitations (a False/None answer then falls back to the router's name/label
heuristic, so these degrade routing accuracy rather than break it):
- Exactly 2-space indentation is assumed: job keys must sit 2 spaces under `jobs:`,
  and `name:`/`services:`/`container:` 2 spaces under their job key.
- The FIRST line whose text starts with `jobs:` -- at any indentation, even inside a
  block scalar -- is taken as the jobs map.
- Jobs are matched by their key or literal `name:`; names built from `${{ }}`
  expressions (e.g. matrix-rendered names) never match.
- Anchors/aliases, flow-style mappings and reusable workflows (`uses:`) aren't resolved.
"""

from collections.abc import Iterator


def _indent(line: str) -> int:
    """Return the number of leading spaces on a line."""
    return len(line) - len(line.lstrip(" "))


def _unquote(value: str) -> str:
    """Strip matching single or double quotes surrounding a string value."""
    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(value[0]) and len(value) >= 2:
        return value[1:-1]
    return value


def _matrix_base(name: str) -> str:
    """Strip a trailing matrix suffix: "Job Name (x, y)" -> "Job Name"."""
    return name.split(" (", 1)[0].strip()


def _looks_like_job_key(line: str, expected_indent: int) -> str | None:
    """Return the job key identifier if line matches expected indentation and format, else None."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if _indent(line) != expected_indent:
        return None
    if stripped.startswith("-"):
        return None
    if not stripped.endswith(":"):
        return None
    key = stripped[:-1].strip()
    if not key or " " in key:
        return None
    return key


def _find_jobs_section(lines: list[str]) -> tuple[int, int] | None:
    """Find the line index and indentation of the top-level jobs: key."""
    for i, line in enumerate(lines):
        if line.strip().startswith("jobs:"):
            return i, _indent(line)
    return None


def _parse_job_properties(lines: list[str], start: int, job_indent: int) -> tuple[str | None, bool, int]:
    """Parse name and services flags for a job block, returning next line index."""
    j = start
    name_value: str | None = None
    has_services = False
    while j < len(lines):
        current = lines[j]
        current_stripped = current.strip()
        if current_stripped and _indent(current) <= job_indent:
            break
        if _indent(current) == job_indent + 2:
            if current_stripped.startswith("name:"):
                name_value = _unquote(current_stripped[len("name:") :])
            elif current_stripped.startswith(("services:", "container:")):
                has_services = True
        j += 1
    return name_value, has_services, j


def _iter_jobs(workflow_text: str) -> Iterator[dict[str, object]]:
    """Yield parsed job blocks from a workflow file's `jobs:` mapping."""
    lines = workflow_text.splitlines()
    section = _find_jobs_section(lines)
    if section is None:
        return

    jobs_idx, jobs_indent = section
    child_indent = jobs_indent + 2
    i = jobs_idx + 1
    while i < len(lines):
        line = lines[i]
        if line.strip() and _indent(line) <= jobs_indent:
            break

        key = _looks_like_job_key(line, child_indent)
        if not key:
            i += 1
            continue

        name_value, has_services, i = _parse_job_properties(lines, i + 1, _indent(line))
        yield {
            "job_id": key,
            "job_name": name_value,
            "has_services": has_services,
        }


def _job_matches_target(target: str, job_id: str, job_name: str | None) -> bool:
    """Check if target string matches the workflow job_id or display name, ignoring matrix suffixes."""
    candidates: list[str] = [job_id]
    if job_name:
        candidates.append(job_name)

    target_base = _matrix_base(target)
    for candidate in candidates:
        cand = candidate.strip()
        cand_base = _matrix_base(cand)
        if target == cand or target_base in (cand, cand_base):
            return True
    return False


def job_uses_services_or_container(workflow_text: str | None, job_name: str) -> bool | None:
    """Return True/False if the job (matched by its rendered `name:`) declares
    `services:`/`container:`, or None if the job couldn't be located in the
    file at all (caller should fall back to a different heuristic in that
    case -- this is a "don't know", not a "no").
    """
    if not workflow_text or not job_name:
        return None

    target = job_name.strip()
    matched: list[bool] = []
    for job in _iter_jobs(workflow_text):
        job_id = str(job["job_id"])
        rendered_name = job.get("job_name")
        if _job_matches_target(target, job_id, rendered_name if isinstance(rendered_name, str) else None):
            matched.append(bool(job["has_services"]))

    if matched:
        return any(matched)

    return None
