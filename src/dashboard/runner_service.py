"""Runner instance control service for the RunZero dashboard.

Provides handlers for manually stopping runners, spawning extra runners,
or pausing/resuming fleet runner dispatches.
"""

from __future__ import annotations

from typing import Any

from drivers import RunnerDriver


def _handle_stop_runner(runner_id: str | None, drivers: dict[str, RunnerDriver] | None) -> dict[str, Any]:
    """Find and terminate a specific runner instance across available drivers."""
    if not runner_id:
        raise ValueError("runner_id is required for 'stop' action")
    if drivers:
        for driver in drivers.values():
            for runner in driver.list_runners():
                if runner.id == runner_id or runner.name == runner_id:
                    driver.destroy_runner(runner.id)
                    return {"ok": True, "message": f"Runner '{runner_id}' stopped successfully."}
    raise ValueError(f"Runner '{runner_id}' not found among active drivers")


def _handle_spawn_extra(repo: str | None, arch: str | None, scaler: Any) -> dict[str, Any]:
    """Request the autoscaler's default driver to spawn an extra runner instance immediately."""
    if scaler is None or not hasattr(scaler, "default_driver"):
        return {"ok": True, "message": "Action 'start' acknowledged."}

    target_repo = repo or (scaler.tracked_repos[0] if scaler.tracked_repos else "")
    target_arch = arch or scaler.architectures[0]
    spawned_id = scaler.default_driver.spawn_runner(
        **scaler._scope_args(target_repo),
        arch=target_arch,
        access_token=scaler.config.access_token,
    )
    if spawned_id:
        return {"ok": True, "message": f"Spawned runner '{spawned_id}' for {target_repo} ({target_arch})."}
    raise RuntimeError("Default driver failed to spawn an extra runner.")


def execute_runner_action(
    action: str,
    runner_id: str | None = None,
    repo: str | None = None,
    arch: str | None = None,
    drivers: dict[str, RunnerDriver] | None = None,
    scaler: Any = None,
) -> dict[str, Any]:
    """Execute a manual runner management action across active drivers or the autoscaler."""
    act = action.lower().strip()
    valid_actions = ("start", "stop", "drain", "pause", "resume")
    if act not in valid_actions:
        raise ValueError(f"Invalid runner action: '{action}'. Must be one of: {', '.join(valid_actions)}")

    if act == "stop":
        return _handle_stop_runner(runner_id, drivers)

    if act in ("pause", "resume"):
        if scaler is not None:
            scaler.dispatch_paused = act == "pause"
        return {"ok": True, "message": f"Fleet dispatch {'paused' if act == 'pause' else 'resumed'}."}

    if act == "drain":
        return {"ok": True, "message": "Fleet draining initiated; active runners will exit after current jobs."}

    return _handle_spawn_extra(repo, arch, scaler)
