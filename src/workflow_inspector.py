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

from typing import Optional


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def job_uses_services_or_container(workflow_text: str, job_name: str) -> Optional[bool]:
    """Return True/False if the job (matched by its rendered `name:`) declares
    `services:`/`container:`, or None if the job couldn't be located in the
    file at all (caller should fall back to a different heuristic in that
    case -- this is a "don't know", not a "no").
    """
    if not workflow_text or not job_name:
        return None

    lines = workflow_text.splitlines()
    target = job_name.strip()

    for i, line in enumerate(lines):
        stripped = line.strip()
        # A job's own `name:` is a direct mapping key (no leading "- "),
        # unlike a step's `name:` inside `steps:` (always a list item, "- name: ...").
        if stripped.startswith("- ") or not stripped.startswith("name:"):
            continue

        value = stripped[len("name:"):].strip()
        if value.startswith(("'", '"')) and value.endswith(value[0]) and len(value) >= 2:
            value = value[1:-1]

        if value != target:
            continue

        job_indent = _indent(line)
        if _block_has_services_key(lines, i + 1, job_indent, direction=1):
            return True
        if _block_has_services_key(lines, i - 1, job_indent, direction=-1):
            return True
        return False

    return None


def _block_has_services_key(lines: list, start: int, job_indent: int, direction: int) -> bool:
    j = start
    while 0 <= j < len(lines):
        line = lines[j]
        if line.strip():
            ind = _indent(line)
            if ind < job_indent:
                break
            if ind == job_indent and (
                line.strip().startswith("services:") or line.strip().startswith("container:")
            ):
                return True
        j += direction
    return False
