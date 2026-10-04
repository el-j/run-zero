"""Unit tests for the runner instance control service."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from dashboard.runner_service import (
    _handle_spawn_extra,
    _handle_stop_runner,
    execute_runner_action,
)
from drivers import RunnerInfo


def test_handle_stop_runner_missing_id() -> None:
    """Test that stopping a runner without an ID raises ValueError."""
    with pytest.raises(ValueError, match="runner_id is required"):
        _handle_stop_runner(None, {})


def test_handle_stop_runner_not_found() -> None:
    """Test that stopping a nonexistent runner raises ValueError."""
    driver = MagicMock()
    driver.list_runners.return_value = []
    with pytest.raises(ValueError, match="not found"):
        _handle_stop_runner("runner-999", {"mock": driver})


def test_handle_stop_runner_by_id() -> None:
    """Test that stopping a runner by exact ID destroys the runner."""
    driver = MagicMock()
    runner = RunnerInfo("r-1", "runzero-r1", "busy", "running", "org/repo", "arm64", "docker")
    driver.list_runners.return_value = [runner]

    res = _handle_stop_runner("r-1", {"mock": driver})
    assert res["ok"] is True
    assert "r-1" in res["message"]
    driver.destroy_runner.assert_called_once_with("r-1")


def test_handle_stop_runner_by_name() -> None:
    """Test that stopping a runner by name destroys the runner."""
    driver = MagicMock()
    runner = RunnerInfo("r-1", "runzero-r1", "busy", "running", "org/repo", "arm64", "docker")
    driver.list_runners.return_value = [runner]

    res = _handle_stop_runner("runzero-r1", {"mock": driver})
    assert res["ok"] is True
    driver.destroy_runner.assert_called_once_with("r-1")


def test_handle_spawn_extra_no_scaler() -> None:
    """Test spawning extra runner when autoscaler is not supplied."""
    res = _handle_spawn_extra("org/repo", "arm64", None)
    assert res["ok"] is True
    assert "acknowledged" in res["message"]


def test_handle_spawn_extra_no_default_driver() -> None:
    """Test spawning extra runner when scaler lacks a default driver."""
    scaler = MagicMock(spec=[])
    res = _handle_spawn_extra("org/repo", "arm64", scaler)
    assert res["ok"] is True
    assert "acknowledged" in res["message"]


def test_handle_spawn_extra_success() -> None:
    """Test spawning extra runner successfully with scaler defaults."""
    scaler = MagicMock()
    scaler.tracked_repos = ["org/repo-default"]
    scaler.architectures = ["arm64"]
    scaler.config.access_token = "token123"
    scaler._scope_args.return_value = {"repository": "org/repo-default"}
    scaler.default_driver.spawn_runner.return_value = "r-spawned"

    res = _handle_spawn_extra(None, None, scaler)
    assert res["ok"] is True
    assert "r-spawned" in res["message"]
    scaler.default_driver.spawn_runner.assert_called_once_with(
        repository="org/repo-default",
        arch="arm64",
        access_token="token123",
    )


def test_handle_spawn_extra_fallback_empty_repo() -> None:
    """Test spawning extra runner when tracked_repos is empty."""
    scaler = MagicMock()
    scaler.tracked_repos = []
    scaler.architectures = ["x64"]
    scaler.config.access_token = "token123"
    scaler._scope_args.return_value = {}
    scaler.default_driver.spawn_runner.return_value = "r-x64"

    res = _handle_spawn_extra(None, None, scaler)
    assert res["ok"] is True
    scaler._scope_args.assert_called_once_with("")


def test_handle_spawn_extra_driver_failure() -> None:
    """Test spawning extra runner when driver returns None or fails."""
    scaler = MagicMock()
    scaler.tracked_repos = ["org/repo"]
    scaler.architectures = ["arm64"]
    scaler._scope_args.return_value = {"repository": "org/repo"}
    scaler.default_driver.spawn_runner.return_value = None

    with pytest.raises(RuntimeError, match="failed to spawn"):
        _handle_spawn_extra("org/repo", "arm64", scaler)


def test_execute_runner_action_invalid() -> None:
    """Test validation of invalid runner actions."""
    with pytest.raises(ValueError, match="Invalid runner action"):
        execute_runner_action("destroy-everything")


def test_execute_runner_action_stop() -> None:
    """Test execute_runner_action routing to stop."""
    driver = MagicMock()
    runner = RunnerInfo("r-2", "runner-2", "idle", "idle", "org/repo", "arm64", "docker")
    driver.list_runners.return_value = [runner]

    res = execute_runner_action("stop", runner_id="r-2", drivers={"test": driver})
    assert res["ok"] is True
    driver.destroy_runner.assert_called_once_with("r-2")


def test_execute_runner_action_pause_resume() -> None:
    """Test pausing and resuming fleet dispatch with and without scaler."""
    scaler = MagicMock()
    res_pause = execute_runner_action("pause", scaler=scaler)
    assert res_pause["ok"] is True
    assert scaler.dispatch_paused is True

    res_resume = execute_runner_action("resume", scaler=scaler)
    assert res_resume["ok"] is True
    assert scaler.dispatch_paused is False

    # Without scaler should not raise
    assert execute_runner_action("pause", scaler=None)["ok"] is True
    assert execute_runner_action("resume", scaler=None)["ok"] is True


def test_execute_runner_action_drain() -> None:
    """Test fleet draining action."""
    res = execute_runner_action("drain")
    assert res["ok"] is True
    assert "draining" in res["message"]


def test_execute_runner_action_start() -> None:
    """Test execute_runner_action routing to start."""
    scaler = MagicMock()
    scaler.tracked_repos = ["org/repo"]
    scaler.architectures = ["arm64"]
    scaler._scope_args.return_value = {"repository": "org/repo"}
    scaler.default_driver.spawn_runner.return_value = "r-extra"

    res = execute_runner_action("start", repo="org/repo", arch="arm64", scaler=scaler)
    assert res["ok"] is True
    assert "r-extra" in res["message"]
