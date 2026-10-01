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
"""

from collections.abc import Iterator
from typing import Dict, List, Optional


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _unquote(value: str) -> str:
    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(value[0]) and len(value) >= 2:
        return value[1:-1]
    return value


def _matrix_base(name: str) -> str:
    """Strip a trailing matrix suffix: "Job Name (x, y)" -> "Job Name"."""
    return name.split(" (", 1)[0].strip()


def _looks_like_job_key(line: str, expected_indent: int) -> Optional[str]:
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


def _iter_jobs(workflow_text: str) -> Iterator[Dict[str, object]]:
    """Yield parsed job blocks from a workflow file's `jobs:` mapping."""
    lines = workflow_text.splitlines()
    jobs_idx: Optional[int] = None
    jobs_indent = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("jobs:"):
            jobs_idx = i
            jobs_indent = _indent(line)
            break

    if jobs_idx is None:
        return

    child_indent = jobs_indent + 2
    i = jobs_idx + 1
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped and _indent(line) <= jobs_indent:
            break

        key = _looks_like_job_key(line, child_indent)
        if not key:
            i += 1
            continue

        job_indent = _indent(line)
        j = i + 1
        name_value: Optional[str] = None
        has_services = False
        while j < len(lines):
            current = lines[j]
            current_stripped = current.strip()
            if current_stripped and _indent(current) <= job_indent:
                break

            current_indent = _indent(current)
            if current_indent == job_indent + 2:
                if current_stripped.startswith("name:"):
                    raw = current_stripped[len("name:"):]
                    name_value = _unquote(raw)
                elif current_stripped.startswith("services:") or current_stripped.startswith("container:"):
                    has_services = True

            j += 1

        yield {
            "job_id": key,
            "job_name": name_value,
            "has_services": has_services,
        }
        i = j


def _job_matches_target(target: str, job_id: str, job_name: Optional[str]) -> bool:
    candidates: List[str] = [job_id]
    if job_name:
        candidates.append(job_name)

    target_base = _matrix_base(target)
    for candidate in candidates:
        cand = candidate.strip()
        cand_base = _matrix_base(cand)
        if target == cand or target_base == cand or target_base == cand_base:
            return True
    return False


def job_uses_services_or_container(workflow_text: str, job_name: str) -> Optional[bool]:
    """Return True/False if the job (matched by its rendered `name:`) declares
    `services:`/`container:`, or None if the job couldn't be located in the
    file at all (caller should fall back to a different heuristic in that
    case -- this is a "don't know", not a "no").
    """
    if not workflow_text or not job_name:
        return None

    target = job_name.strip()
    matched: List[bool] = []
    for job in _iter_jobs(workflow_text):
        job_id = str(job["job_id"])
        rendered_name = job.get("job_name")
        if _job_matches_target(target, job_id, rendered_name if isinstance(rendered_name, str) else None):
            matched.append(bool(job["has_services"]))

    if matched:
        return any(matched)

    return None
