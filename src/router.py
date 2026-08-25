"""
Hybrid routing engine for dynamically matching workflow jobs to container or VM drivers.
"""

import re
from typing import Dict, Tuple, Any
from drivers import RunnerDriver

VM_TRIGGER_LABELS = {"vm", "orbstack", "wsl", "multipass", "e2e", "browser", "chrome", "lighthouse", "systemd"}


def select_driver_for_job(
    job: Dict[str, Any],
    default_driver: RunnerDriver,
    available_drivers: Dict[str, RunnerDriver],
    auto_route_vm: bool = True
) -> Tuple[RunnerDriver, str]:
    """Determine whether a job requires a VM driver or a standard container driver."""
    job_labels = job.get("labels", [])

    # Tokenize job name and check labels for VM triggers
    job_name_tokens = set(re.findall(r"[a-z0-9]+", (job.get("name") or "").lower()))
    needs_vm = (
        any(trigger in job_labels for trigger in VM_TRIGGER_LABELS)
        or bool(job_name_tokens & VM_TRIGGER_LABELS)
    )

    if needs_vm and auto_route_vm:
        for vm_name in ("orbstack-vm", "wsl2", "multipass"):
            if vm_name in available_drivers:
                return available_drivers[vm_name], "vm"

    return default_driver, "container"
