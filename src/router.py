"""
Hybrid routing engine for dynamically matching workflow jobs to container or VM drivers.
"""

import re
import sys
from typing import Any, Dict, Tuple

from drivers import RunnerDriver

VM_TRIGGER_LABELS = {
    "vm", "orbstack", "wsl", "multipass", "e2e", "browser", "chrome",
    "lighthouse", "systemd", "postgres", "mysql", "redis", "db",
    "database", "service", "services", "integration", "dind"
}


def select_driver_for_job(
    job: Dict[str, Any],
    default_driver: RunnerDriver,
    available_drivers: Dict[str, RunnerDriver],
    auto_route_vm: bool = True
) -> Tuple[RunnerDriver, str]:
    """Determine whether a job requires a VM driver or a standard container driver."""
    job_labels = job.get("labels", [])

    # Tokenize job name and check labels for VM triggers. This is a best-effort
    # guess when the job's actual `services:`/`container:` declaration isn't
    # known (see below) -- a name/label match alone is neither necessary nor
    # sufficient (a job named "e2e-smoke" with zero services still wants a VM
    # for its browser sandbox; a job named "api-test" with a real `services:
    # postgres:` block still needs one and won't get caught by name alone).
    job_name_tokens = set(re.findall(r"[a-z0-9]+", (job.get("name") or "").lower()))
    name_or_label_match = (
        any(trigger in job_labels for trigger in VM_TRIGGER_LABELS)
        or bool(job_name_tokens & VM_TRIGGER_LABELS)
    )

    # get_queued_job_details() resolves this from the actual workflow YAML at
    # the run's commit (see workflow_inspector.job_uses_services_or_container):
    # True/False when the job was located and parsed, None ("unknown") when
    # the workflow file couldn't be fetched/parsed or the job wasn't found by
    # name -- None must NOT be treated as False, or a real `services:` job
    # silently loses VM routing the moment the lookup itself fails (e.g. a
    # transient API error), which is exactly the failure mode this replaces.
    declares_services = job.get("declares_services")
    needs_vm = name_or_label_match or bool(declares_services)

    if needs_vm and auto_route_vm:
        for vm_name in ("orbstack-vm", "wsl2", "multipass"):
            if vm_name in available_drivers:
                return available_drivers[vm_name], "vm"
        print(
            f"[Router] ⚠️ Job '{job.get('name', '?')}' needs a VM "
            f"(declares_services={declares_services}, name/label match={name_or_label_match}) "
            f"but no VM driver is available -- falling back to {default_driver.name()}. "
            "A services:/container: job running here will likely fail to reach "
            "its service containers at localhost.",
            file=sys.stderr,
        )

    return default_driver, "container"
