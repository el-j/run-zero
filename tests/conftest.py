"""
Suite-wide guard: unit tests must never drive real host tooling.

A unit test that forgets to mock `subprocess` would otherwise call the developer's real
`docker`/`orbctl`/`multipass`/`wsl` -- slow (each call can wait out a timeout), dependent on
host state (coverage and results changed with the daemon's config), and occasionally
destructive (e.g. starting a real golden-image build). The guard wraps the *real*
subprocess entry points, so a test's own `patch("subprocess.run")` still takes precedence;
only calls that would genuinely reach the host fail, naming the offending command.

Modules that exist to exercise real tooling opt out via REAL_TOOLING_MODULES.
"""

import os
import subprocess
import threading
from collections.abc import Iterator
from typing import Any

import pytest

GUARDED_TOOLS = frozenset({"docker", "orbctl", "orb", "multipass", "wsl", "wsl.exe"})

# End-to-end / black-box modules whose whole point is the real binary.
REAL_TOOLING_MODULES = frozenset(
    {
        "test_e2e_docker",
        "test_e2e_compose_deployment",
        "test_blackbox_cli",
        "test_orbstack_live_integration",
        "test_e2e_github",
    }
)


def _tool_name(args: Any) -> str:
    argv = args if isinstance(args, (list, tuple)) else str(args).split()
    return os.path.basename(str(argv[0])) if argv else ""


@pytest.fixture(autouse=True)
def _forbid_real_host_tooling(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    if request.module.__name__.rsplit(".", 1)[-1] in REAL_TOOLING_MODULES:
        yield
        return

    violations: list[str] = []
    threads_before = set(threading.enumerate())

    def guard(real: Any) -> Any:
        def wrapper(args: Any, *a: Any, **kw: Any) -> Any:
            tool = _tool_name(args)
            if tool in GUARDED_TOOLS:
                violations.append(" ".join(map(str, args)) if isinstance(args, (list, tuple)) else str(args))
                # Code under test often swallows exceptions, so the failure is also
                # reported at teardown below rather than relying on this propagating.
                raise RuntimeError(f"unit test invoked real host tool {tool!r}")
            return real(args, *a, **kw)

        return wrapper

    monkeypatch.setattr(subprocess, "run", guard(subprocess.run))
    monkeypatch.setattr(subprocess, "Popen", guard(subprocess.Popen))
    monkeypatch.setattr(subprocess, "check_output", guard(subprocess.check_output))
    yield
    # A driver's background image-build thread that outlives its test runs after the test's
    # mocks are gone -- i.e. against the real host (this is how real `docker buildx build`s
    # used to start during unit runs). Give it a moment, then fail the test that leaked it.
    leaked = [t for t in threading.enumerate() if t not in threads_before and t.name.startswith("runzero-build-")]
    for t in leaked:
        t.join(timeout=2.0)
    still_alive = [t.name for t in leaked if t.is_alive()]
    if still_alive:
        pytest.fail(f"test leaked background build thread(s) {still_alive}; join them or mock the build", pytrace=False)
    if violations:
        pytest.fail("unit test reached real host tooling (mock subprocess):\n  " + "\n  ".join(violations[:5]), pytrace=False)
