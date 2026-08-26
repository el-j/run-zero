# End-to-End Testing (issue #14)

This document draws an explicit line between what run-zero's test suite can
verify **automatically in CI** versus what genuinely requires a human and
real local hardware. Don't infer full e2e coverage across all four engines
from the automated suite alone — read this first.

## The honest boundary

| Engine | Automated in CI? | Why / why not |
|---|---|---|
| **Docker** | ✅ Yes — `tests/test_e2e_docker.py` | GitHub-hosted `ubuntu-latest` runners ship Docker out of the box, so a real `docker build`/`docker run`/`docker exec`/`docker rm` lifecycle can run on every CI execution, no special hardware needed. |
| **OrbStack VM** | ❌ No — manual only | OrbStack is a macOS-only, Apple Virtualization-framework product. There is no macOS-with-OrbStack CI runner available to this project. See [OrbStack VM engine](#orbstack-vm-engine-macos-only) below. |
| **WSL2** | ❌ No — manual only | Requires a real Windows 10/11 (or Windows Server) host with WSL2 enabled. See [WSL2 engine](#wsl2-engine-windows-only) below. |
| **Multipass** | ❌ No — manual only | Requires a real hypervisor (QEMU/Hyper-V/VirtualBox depending on host OS) and the Multipass daemon. See [Multipass engine](#multipass-engine-cross-platform) below. |

None of the three VM-based engines are technical dead ends for automation —
they're excluded specifically because no CI runner in this project's actual
CI (GitHub-hosted `ubuntu-latest`) can run OrbStack, WSL2, or Multipass. If a
self-hosted macOS or Windows CI runner is ever added to this project, this
boundary should be revisited.

## Docker engine — automated in CI

`tests/test_e2e_docker.py` is the automated half of this document. It:

1. `docker build`s a tiny, disposable Alpine test image (not the real
   production runner image — that one takes minutes and needs full toolchain
   provisioning, which is a different, slower concern from this test's
   actual job).
2. Calls `DockerDriver.spawn_runner()` for real — a real `docker run -d`.
3. Runs a real `docker exec` inside the resulting container to prove it's
   genuinely alive and executing commands, not just "created".
4. Calls `DockerDriver.list_runners()` for real — a real `docker ps -a`,
   parsed, confirmed to include the container just created.
5. Calls `DockerDriver.destroy_runner()` for real — a real `docker rm -f`,
   confirmed afterwards with a real `docker inspect` showing it's gone.

**What it explicitly does NOT cover:** real GitHub Actions runner
registration (`config.sh`/`run.sh`, a real registration token, a real queued
job). That would require a real GitHub token and a disposable repo with a
guaranteed cleanup path that isn't available in an unattended CI/agent
environment — attempting it risked registering a phantom runner against
real project infrastructure with no safe rollback if something went wrong,
so it was deliberately not attempted. See the test file's own module
docstring for the full reasoning.

Run it locally the same way CI does:

```bash
PYTHONPATH=src python3 -m pytest tests/test_e2e_docker.py -v
# or, without pytest installed:
PYTHONPATH=src python3 -m unittest tests.test_e2e_docker -v
```

It skips cleanly (not a hard failure) if the `docker` CLI isn't on `PATH` or
the daemon isn't reachable — this is why it stays green inside
`make test-suite`'s inner `python:3.11-slim` container, which has no Docker
socket mounted.

## Manual runbooks for the VM-based engines

Each of the following **must be run by a human, on real hardware, locally**.
None of these are wired into CI and none should be assumed to have run
recently unless someone explicitly reports doing so.

### OrbStack VM engine (macOS only)

Prerequisites: a Mac with [OrbStack](https://orbstack.dev/) installed and
running (`orbctl status` should print `running`).

1. **Golden base image build** — proves `OrbStackVMDriver.build_base_image()`
   actually produces a bootable, provisioned VM:
   ```bash
   make build-vm-base
   make vm-list          # confirm runzero-vm-base-<arch> shows up, state "stopped"
   ```
2. **Real spawn → run → cleanup, via the host-native bridge** — this is the
   same code path a containerized autoscaler uses in production:
   ```bash
   make bridge-start
   make bridge-status     # confirm "Running"
   curl -s http://localhost:49504/health | python3 -m json.tool
   # Spawn a real ephemeral VM runner (replace with a real repo you control):
   curl -s -X POST http://localhost:49504/api/drivers/orbstack-vm/spawn \
     -H 'Content-Type: application/json' \
     -d '{"repo": "your-org/your-repo", "arch": "arm64", "access_token": "ghp_..."}'
   make vm-list            # confirm the new ephemeral VM appears, then goes away
   make bridge-stop
   ```
3. **Real two-VM cache-sharing proof** (issue #10's own live test, already
   automated but deliberately opt-in — creates and destroys two real,
   disposable OrbStack VMs, ~30-60s):
   ```bash
   RUNZERO_LIVE_TESTS=1 PYTHONPATH=src python3 -m unittest \
     tests.test_orbstack_live_integration -v
   ```
4. Clean up when done:
   ```bash
   make vm-clean          # removes orphaned ephemeral VMs, keeps the golden base
   make vm-clean-all       # nuclear option: removes the golden base images too
   ```

Automated coverage for `orbstack_vm_driver.py` today is otherwise entirely
mocked (`tests/test_orbstack_driver.py`) — the steps above are the only way
to prove the real `orbctl`/`orb` subprocess calls and the real
`/mnt/mac`-backed cache mounts actually work end-to-end.

### WSL2 engine (Windows only)

Prerequisites: Windows 10/11 or Windows Server, with WSL2 enabled and a
`Ubuntu-24.04` distro installed (`wsl --status` should succeed;
`WSL_DISTRO_BASE` env var overrides the distro name if you use a different
one).

1. Configure `.env` for the WSL2 backend and run the autoscaler natively in
   the foreground so you can watch it:
   ```powershell
   # from a WSL2 shell or PowerShell with wsl.exe on PATH
   make env                       # set RUNNER_BACKEND=wsl2 in .env
   make run-dev                   # runs src/autoscaler.py in the foreground natively
   ```
2. Trigger a real job against a repo you control (push a commit / open a PR
   that queues a workflow run targeting `self-hosted` + `wsl` labels) and
   watch the autoscaler log for `WSL2Driver.spawn_runner()` launching
   `run.sh` inside the distro.
3. Confirm the runner picks up and completes the real queued job in the
   GitHub Actions UI, then confirm the driver's ephemeral instance is
   cleaned up (no lingering `runzero-wsl-*` background processes inside the
   distro).

Automated coverage for `wsl_driver.py` today is entirely mocked
(`tests/test_wsl_driver.py`) — there is no way to fake a real Windows/WSL2
host, so the steps above are the only way to prove the real `wsl`/`wsl.exe`
subprocess calls actually work.

### Multipass engine (cross-platform)

Prerequisites: [Multipass](https://multipass.run/) installed on macOS,
Linux, or Windows (`multipass version` should succeed).

1. Configure and run natively, same shape as the WSL2 runbook:
   ```bash
   make env                       # set RUNNER_BACKEND=multipass in .env
   make run-dev
   ```
2. Trigger a real job against a repo you control, targeting `self-hosted` +
   `multipass` labels, and watch the autoscaler log for
   `MultipassDriver.spawn_runner()` calling `multipass launch`.
3. Confirm the job completes in the GitHub Actions UI and that
   `multipass list` no longer shows the ephemeral `runzero-mp-*` VM once the
   job finishes (ephemeral cleanup).

Automated coverage for `multipass_driver.py` today is entirely mocked
(`tests/test_multipass_driver.py`) — same reasoning as WSL2 above.

## Related test layers (for contributors, not duplicated here)

- **White-box unit tests** (most of `tests/`) — fast, deterministic, mock
  every `subprocess`/HTTP call at the call site.
- **Blackbox process-boundary tests** (`tests/test_blackbox_*.py`, issue
  #18) — real HTTP client against a real dashboard/VM-bridge server on a
  real socket, and a real `make` subprocess invocation — but no real
  Docker/VM/GitHub infrastructure underneath. See
  `tests/test_blackbox_dashboard.py`'s module docstring for the full
  three-layer breakdown.
- **True e2e** (this document + `tests/test_e2e_docker.py`) — real
  infrastructure, real subprocess calls all the way down, for at least the
  one engine that's realistically automatable in this project's CI.
