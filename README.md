<div align="center">

# ⚡ RunZero

**Zero Cloud Minutes. Zero K8s Bloat. Zero Idle Waste.**

*An intelligent, autoscaling local GitHub Actions runner fleet with **Dual-Engine execution** (Docker Containers & Dedicated Linux VMs via [OrbStack](https://orbstack.dev/), [Windows WSL2](https://learn.microsoft.com/en-us/windows/wsl/), and [Multipass](https://multipass.run/)), with native Apple Silicon (`arm64`) & Intel/AMD (`amd64`), [Verdaccio](https://verdaccio.org/), [Athens](https://github.com/gomods/athens), [apt-cacher-ng](https://www.unix-ag.uni-kl.de/~bloch/acng/), and persistent multi-language caching.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-20%2B%20%2F%20Desktop-blue.svg)](https://www.docker.com/)
[![OrbStack](https://img.shields.io/badge/OrbStack-Ultra--Fast-brightgreen.svg)](https://orbstack.dev/)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-ARM64%20%2B%20x86__64-purple.svg)](https://apple.com)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Runner%20v2.336-blue.svg)](https://github.com/actions/runner)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## 📖 Table of Contents

- [Why RunZero? (Competitive Landscape)](#-why-runzero)
- [Dual-Engine Execution (Containers vs. Full VMs)](#-dual-engine-execution-containers-vs-full-vms)
- [Hybrid Auto-Routing for Chrome / Lighthouse / Systemd](#-hybrid-auto-routing)
- [Docker & VM Engine Compatibility](#-docker--vm-engine-compatibility)
- [Key Features](#-key-features)
- [Proxy Registries & Upstream Ecosystem](#-proxy-registries--upstream-ecosystem)
- [Architecture Overview](#-architecture-overview)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [Automatic Cloud Fallback in Workflows](#-automatic-cloud-fallback-in-workflows)
- [Multi-Architecture Builds (ARM64 vs. AMD64)](#-multi-architecture-builds)
- [Makefile Commands Reference](#-makefile-commands)
- [Configuration Reference (`.env`)](#-configuration-reference-env)
- [Contributing](#-contributing)
- [License](#-license)

---

## 💡 Why RunZero?

| Feature / Metric | ⚡ RunZero | 🏢 Actions Runner Controller (ARC) | 🎭 nektos / act | 📦 Static Docker Runner |
|---|---|---|---|---|
| **Target Environment** | **Local Mac / Windows / Linux** | Enterprise Cloud K8s Fleet | Local CLI Scratchpad | Single Homelab Container |
| **Idle RAM Overhead** | **~20 MB (0 MB at idle)** | **1.5 GB – 3.5 GB (Heavy K8s)** | 0 MB (Manual CLI only) | ~500 MB+ (Always running) |
| **Execution Engines** | **Dual-Engine (Docker + VM)** | Containers Only (K8s Pods) | Containers Only | Container Only |
| **Runs Real GitHub Queue** |  **Yes** (Pulls live jobs) |  **Yes** | ❌ **No** (Local emulation only) |  **Yes** |
| **Personal Account Multi-Repo** |  **Automatic Discovery** | ❌ **No** (Org / Enterprise only) | ❌ N/A | ❌ **No** (1 repo per container) |
| **Multi-Arch (Apple Silicon + x86_64)** |  **Native ARM64 + Rosetta AMD64** | ⚠️ Complex (K8s node taints) | ⚠️ Partial | ❌ Fixed single arch |
| **Built-in Package Proxies** |  **APT + Verdaccio + Athens + Mirrors** | ❌ None (Requires K8s PVC/NFS) | ❌ None | ❌ None |
| **Setup Complexity** |  **1 Command (`make start`)** | ❌ Complex Helm / CRDs |  Simple CLI | ⚠️ Moderate |

---

## 🚀 Dual-Engine Execution (Containers vs. Full VMs)

RunZero is the **first local runner fleet that gives you the choice between ultra-lightweight Docker containers and dedicated Linux Virtual Machines**:

| Engine Backend | Upstream Runtime | Best Used For |
|---|---|---|
| 🐳 **Docker Containers** (`RUNNER_BACKEND=docker`) | [Docker Engine](https://docs.docker.com/engine/) / [OrbStack](https://orbstack.dev/) | Fast unit tests, linting, build pipelines, JS/Node/Python steps (**instant ~0.3s boot, ~20MB RAM**). |
| 💻 **OrbStack Linux Machines** (`RUNNER_BACKEND=orbstack-vm`) | [OrbStack Virtualization](https://orbstack.dev/) | **Full systemd support**, background daemons, headless Chrome/Lighthouse, unconfined Docker daemon. |
| 🪟 **Windows WSL2** (`RUNNER_BACKEND=wsl2`) | [Windows Subsystem for Linux 2](https://learn.microsoft.com/en-us/windows/wsl/) | Native Linux VM execution on Windows 10/11 & Windows Server. |
| 🐧 **Canonical Multipass** (`RUNNER_BACKEND=multipass`) | [Canonical Multipass](https://multipass.run/) | Universal cross-platform VM backend for macOS, Linux, and Windows. |

---

## 🧠 Hybrid Auto-Routing

You don't have to choose just one! With `RUNNER_BACKEND=auto` and `AUTO_ROUTE_VM=true`, RunZero **automatically inspects queued jobs and routes them intelligently**:

```yaml
# 1. Standard build job -> Automatically runs in ultra-fast Docker container (~0.3s)
jobs:
  unit-tests:
    runs-on: [ self-hosted, local ]
    steps:
      - run: npm test

# 2. Browser / Lighthouse / Systemd job -> Automatically routed to dedicated Linux VM!
jobs:
  e2e-lighthouse:
    runs-on: [ self-hosted, local, browser ]  # or 'vm', 'e2e', 'lighthouse', 'systemd'
    steps:
      - run: npx lhci autorun
```

---

## 📦 Proxy Registries & Upstream Ecosystem

RunZero runs local caching proxy registries alongside the autoscaler so your runners and image builds never re-download packages over the public internet:

| Service / Dependency | Upstream Project | Local Port | Dashboard / Report | Description |
|---|---|---|---|---|
| **APT Cacher NG** | [apt-cacher-ng](https://www.unix-ag.uni-kl.de/~bloch/acng/) | `:49503` | [http://localhost:49503/acng-report.html](http://localhost:49503/acng-report.html) | Caches Ubuntu/Debian `.deb` packages across Docker builds & VM golden image clones. |
| **Verdaccio** | [Verdaccio](https://verdaccio.org/) | `:49501` | [http://localhost:49501](http://localhost:49501) | Private npm/yarn/pnpm caching proxy registry with web UI. |
| **Athens** | [Athens Go Proxy](https://github.com/gomods/athens) | `:49500` | `http://localhost:49500` | Immutable Go module proxy and download cache. |
| **Docker Registry Mirror** | [Docker Registry](https://docs.docker.com/docker-hub/mirror/) | `:49502` | `http://localhost:49502` | Pull-through mirror for Docker Hub images. |
| **devpi** | [devpi-server](https://devpi.net/) | `:49507` | [http://localhost:49507/root/pypi/+simple/](http://localhost:49507/root/pypi/+simple/) | Real pull-through caching proxy for pip/uv (PyPI) via its built-in `root/pypi` mirror index. |
| **kellnr** | [kellnr](https://kellnr.io/) | `:49506` | `http://localhost:49506` | Real pull-through caching proxy for Cargo/crates.io via kellnr's built-in crates.io proxy. |
| **Node.js Toolchain** | [NVM](https://github.com/nvm-sh/nvm) & [Node.js](https://nodejs.org/) | Local | Pre-baked | Pre-installed Node.js 20 LTS, 22 LTS, and 24 Current with yarn & pnpm. |
| **.NET SDK** | [Microsoft .NET 8](https://dotnet.microsoft.com/) | Local | Pre-baked | Pre-installed .NET 8.0 SDK for C#/F# workflow pipelines. |
| **Browser Testing** | [Playwright](https://playwright.dev/) & [Google Chrome](https://www.google.com/chrome/) | Local | Pre-baked | Pre-installed system dependencies and browser runtimes for E2E testing. |

Cargo has no single "index URL" env var the way pip/uv (`PIP_INDEX_URL`/`UV_INDEX_URL`) and Go (`GOPROXY`) do --
pointing it at kellnr requires a real `~/.cargo/config.toml` source-replacement block (written automatically by
`docker/start.sh` for Docker-engine runners, and by `OrbStackVMDriver` for VM-engine runners); `CARGO_SOURCE_*`
env vars for a custom `[source.*]` table are silently ignored by Cargo. Likewise, pip refuses a plain-HTTP index
on any host other than `localhost`/`127.0.0.1` unless that host is explicitly trusted via `PIP_TRUSTED_HOST` --
both runner engines set this automatically alongside `PIP_INDEX_URL` wherever the index isn't reached via
`localhost`; uv has no equivalent restriction.

### 🪐 OrbStack VM Local Disk Caching

The proxy registries above cache package *downloads* over the network. Package managers also keep a local,
already-extracted disk cache (`~/.npm`, `~/.cache/pip`, `~/go/pkg`, `~/.cargo/registry`, etc.) so a *second* job
using the same package doesn't even need the network proxy -- this is what `HOST_CACHE_DIR` and the Cache
Analytics dashboard panel track. For the Docker engine this is a plain `-v host:container` bind mount. An
OrbStack VM is a real, separate guest filesystem with no such flag, but every non-isolated OrbStack VM (the kind
this project creates) automatically virtiofs-shares the entire host macOS filesystem into the guest at a fixed
path, `/mnt/mac<absolute-macOS-path>` -- confirmed live: a file written from inside a VM under
`/mnt/mac/Users/...` appears immediately, with matching ownership, at the real `/Users/...` path on the host,
and vice versa. `OrbStackVMDriver` uses this to `mount --bind` each host-side cache directory onto its
container-style destination path inside the VM before the job runs, so cache data written by one ephemeral VM
is really on host disk and visible to the next VM cloned for the same architecture. If a host cache directory
isn't visible via the mac share for some reason, the mount is skipped with a warning rather than failing the
job outright.

---

## 🐳 Docker & VM Engine Compatibility

| Engine | macOS (Apple Silicon) | macOS (Intel) | Windows | Linux / Homelab |
|---|---|---|---|---|
| 🪐 [OrbStack](https://orbstack.dev/) *(Recommended for Mac)* | ⭐ **Containers + Linux VMs** | ⭐ Fast | — | — |
| 🐳 [Docker Desktop](https://www.docker.com/) |  Native Containers |  Native Containers |  Native Containers |  Native Containers |
| 🪟 [Windows WSL2](https://learn.microsoft.com/en-us/windows/wsl/) | — | — | ⭐ **Native Linux VMs** | — |
| 🐧 [Native Linux Docker](https://docs.docker.com/engine/) |  Native (ARM64) |  Native (AMD64) | — | ⭐ **Native (Best for Servers)** |
| 🚀 [Canonical Multipass](https://multipass.run/) |  Native VMs |  Native VMs |  Native VMs |  Native VMs |

---

## 🌟 Key Features

1. **Intelligent Dynamic Autoscaling**:
   - Watches your GitHub queue for unclaimed jobs.
   - Spins up ephemeral instances (`--ephemeral`) on-demand and tears them down immediately upon job completion (**0 MB RAM consumed when idle**).
2. **Owner-Wide Multi-Repo Auto-Discovery**:
   - Automatically monitors **all active repositories** under your personal GitHub account (`OWNER=your-username`), explicit repo lists, or GitHub Organizations.
3. **Pluggable Multi-Backend Drivers**:
   - Easily switch between [Docker](https://www.docker.com/) containers, [OrbStack](https://orbstack.dev/) VMs, [Windows WSL2](https://learn.microsoft.com/en-us/windows/wsl/), and [Canonical Multipass](https://multipass.run/) via `RUNNER_BACKEND`.
4. **Golden VM Base Cloning (`make build-vm-base`)**:
   - Pre-bakes the unified toolchain into a golden base image (`runzero-vm-base-<arch>`). VM jobs launch in seconds by cloning the base image.
5. **Self-Healing Zombie Runner Reconciliation**:
   - Automatically detects offline runners that GitHub still marks as `busy: true` (e.g. after abrupt host restarts), cancels orphaned jobs, and unblocks your queue.
6. **Adaptive GitHub API Rate-Limiting**:
   - Intelligently filters to active repositories and dynamically paces API calls to keep you safely within GitHub's 5,000 req/hr ceiling.
7. **Built-in Local Proxy Registries & Caching**:
   - [apt-cacher-ng](https://www.unix-ag.uni-kl.de/~bloch/acng/) (`:49503`) for Debian/Ubuntu `.deb` packages.
   - [Verdaccio](https://verdaccio.org/) (`:49501`) for instant npm/yarn/pnpm caching + web dashboard.
   - [Athens](https://github.com/gomods/athens) (`:49500`) for immutable Go module caching.
   - [Docker Registry Mirror](https://docs.docker.com/docker-hub/mirror/) (`:49502`) for Docker Hub pull-through caching.
   - [devpi](https://devpi.net/) (`:49507`) for pip/uv PyPI pull-through caching.
   - [kellnr](https://kellnr.io/) (`:49506`) for Cargo/crates.io pull-through caching.
   - Per-VM local disk caches (`~/.npm`, `~/.cache/pip`, `~/go/pkg`, `~/.cargo/registry`, etc.) are real
     even for the OrbStack VM engine, bind-mounted from host storage via OrbStack's automatic `/mnt/mac`
     filesystem share -- see "OrbStack VM Local Disk Caching" below.
8. **Zero Cloud Bill**:
   - Self-hosted runners **never** consume GitHub Actions minutes (100% free and unlimited).

---

## 🏗️ Architecture Overview

```
                          ┌──────────────────────────────────────────────┐
                          │         RunZero Autoscaler Daemon            │
                          │   (Queue Monitor, Rate Limiting, Discovery)  │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                     Intelligent Auto-Router
                                 (Inspects Job Labels & Platform)
                                                 │
                       ┌─────────────────────────┴─────────────────────────┐
                       ▼                                                   ▼
         ┌───────────────────────────┐                       ┌───────────────────────────┐
         │     Container Driver      │                       │     Pluggable VM Driver   │
         │ (runs-on: [self-hosted])  │                       │ (runs-on: [..., vm, e2e]) │
         └─────────────┬─────────────┘                       └─────────────┬─────────────┘
                       │                                                   │
         ┌─────────────┴─────────────┐                       ┌─────────────┴─────────────┐
         ▼                           ▼                       ▼             ▼             ▼
   ┌───────────┐               ┌───────────┐           ┌───────────┐ ┌───────────┐ ┌───────────┐
   │ ARM64 Run │               │ AMD64 Run │           │ OrbStack  │ │ Windows   │ │Multipass  │
   │ (Docker)  │               │ (Rosetta) │           │ Machine   │ │ WSL2/VM   │ │(Cross-OS) │
   └───────────┘               └───────────┘           └───────────┘ └───────────┘ └───────────┘
```

---

## 📁 Repository Structure

```text
.
├── src/                                   # 🐍 Pure Python Application Code
│   ├── autoscaler.py                      #    Dynamic queue monitor, rate limiter, zombie healer & hybrid router
│   ├── version.py                         #    Dynamic SemVer resolver (main: 0.0.1, develop: beta, feat: alpha)
│   └── drivers/                           #    Pluggable Execution Drivers
│       ├── __init__.py                    #    RunnerDriver interface & discovery factory
│       ├── docker_driver.py               #    Docker container engine
│       ├── orbstack_vm_driver.py          #    OrbStack macOS Linux VM engine (with golden base cloning)
│       ├── wsl_driver.py                  #    Windows WSL2 engine (with proxy caching)
│       └── multipass_driver.py            #    Canonical Multipass engine (with proxy caching)
├── docker/                                # 🐳 Container Build Manifests & Entrypoints
│   ├── Dockerfile                         #    Multi-arch runner image (ARM64 + AMD64)
│   ├── Dockerfile.autoscaler              #    Autoscaler daemon container
│   ├── Dockerfile.devpi                   #    devpi pip/uv PyPI proxy image (no maintained multi-arch upstream)
│   ├── provision-toolchain.sh             #    Unified toolchain script (shared by Docker & VM base images)
│   └── start.sh                           #    Runner entrypoint with proxy auto-detect
├── tests/                                 # 🧪 Comprehensive Test Suite (90 Tests)
│   ├── test_autoscaler.py                 #    Autoscaler, rate limiting, zombie healing & hybrid routing tests
│   ├── test_drivers.py                    #    All driver lifecycle, base image & error branch tests
│   ├── test_version.py                    #    Dynamic SemVer branch resolver tests
│   └── test_shell_scripts.py              #    Shell script syntax & wizard tests
├── website/                               # 🚀 Astro Static Website & Documentation
│   ├── src/                               #    Astro components, pages (Hero + Docs + Versions) & styles
│   ├── public/                            #    Self-hosted fonts, versions.json, and SVG assets
│   ├── astro.config.mjs                   #    Astro static SSG configuration
│   └── package.json                       #    Website dependencies
├── docs/                                  # 🌐 Compiled GitHub Pages Website
│   ├── index.html                         #    Compiled Hero Landing Page
│   ├── docs/index.html                    #    Compiled Dedicated Documentation Page
│   └── versions/index.html                #    Compiled Release Version Archive Page
├── docker-compose.yml                     # 🚀 Orchestration (apt-cacher + Verdaccio + Athens + Docker Mirror + devpi + kellnr)
├── Makefile                               # 🛠️ Unified management commands
├── pyproject.toml                         # ⚙️ Python project configuration (Pytest, Mypy, Mutmut)
├── .env.example                           # ⚙️ Configuration template
├── CONTRIBUTING.md                        # 🤝 Contributor guidelines & Git-Flow guide
├── LICENSE                                # 📄 MIT License
└── README.md                              # 📖 Main repository documentation
```

---

## ⚡ Quick Start

### 1. Initialize environment:
```bash
make env
```
Edit `.env` and configure:
```env
ACCESS_TOKEN=ghp_yourPersonalAccessTokenHere
OWNER=your-username
AUTO_DISCOVER_REPOS=true
RUNNER_BACKEND=auto  # 'auto', 'docker', 'orbstack-vm', 'wsl2', or 'multipass'
RUNNER_ARCH=both     # 'both', 'amd64', or 'arm64'
PROXIES_ENABLED=true # Starts apt-cacher, Verdaccio, Athens & Docker Mirror
```

### 2. Build images & VM templates:
```bash
make build          # Builds ARM64 + AMD64 + Autoscaler container images
make build-vm-base  # Builds golden OrbStack VM base image for instant cloning
```

### 3. Start the Autoscaler & Proxies:
```bash
make start          # Starts apt-cacher, Verdaccio, Athens, Docker mirror, and Autoscaler
```

### 4. Check status & live logs:
```bash
make status         # View active autoscaler, proxies, and dynamic runner instances
make logs           # Stream live autoscaler logs
```

### 5. Stop the Autoscaler & Proxies:
```bash
make stop           # (or make down)
```

---

## 🧪 Testing & Quality Suite

RunZero includes a 100% verified test suite with type checking, linting, and mutation testing:

| Command | Description |
|---|---|
| `make test` | Run fast local unit tests directly (90 tests in ~1.0s) |
| `make test-suite` | Run Flake8 linter, Mypy static type checker, and Pytest coverage |
| `make mutation-test` | Run Mutmut mutation testing suite across all drivers and autoscaler |

The suite is layered:

- **White-box unit tests** (most of `tests/`) — mock every `subprocess`/HTTP call at the call site.
- **Blackbox process-boundary tests** (`tests/test_blackbox_*.py`) — real HTTP client against a
  real dashboard/VM-bridge server bound to a real socket, plus a real `make` subprocess
  invocation — no real Docker/VM/GitHub infrastructure required.
- **True end-to-end tests** (`tests/test_e2e_docker.py`) — a real, unmocked Docker container
  lifecycle. See [`E2E_TESTING.md`](E2E_TESTING.md) for exactly what's automated in CI (Docker)
  versus what requires a human running a manual runbook locally (OrbStack VM, WSL2, Multipass).

---

## 📋 Makefile Commands

| Command | Description |
|---|---|
| `make start` (or `make run`, `make up`) | Launch autoscaler, apt-cacher, Verdaccio, Athens, and Docker mirror |
| `make stop` (or `make down`) | Gracefully stop the autoscaler, proxies, and active runners |
| `make status` (or `make ps`) | Display running autoscaler, proxies & active ephemeral runners |
| `make test` | Run fast local unit tests directly with `unittest` (85 tests in 0.04s) |
| `make test-suite` | Run Flake8 linter, Mypy type-checker, and Pytest coverage report |
| `make install-hooks` | Install RunZero pre-commit quality guard into `.git/hooks/pre-commit` |
| `make pre-commit` | Run the pre-commit quality guard manually with auto-fixes |
| `make lint` | Run Flake8 linter and Mypy static type checker |
| `make lint-fix` | Auto-fix Python code formatting and strip trailing whitespace |
| `make mutation-test` | Run Mutmut mutation testing suite |
| `make build-vm-base` | Build golden OrbStack VM base image for near-instant VM spins |
| `make website-dev` | Start Astro documentation website development server |
| `make website-build` | Build Astro static website and synchronize to `docs/` |
| `make docs` | Preview the documentation website locally in your browser |
| `make verdaccio-ui` | Open Verdaccio Web UI at `http://localhost:49501` |
| `make apt-cacher-ui` | Open apt-cacher-ng statistics report at `http://localhost:49503/acng-report.html` |
| `make logs` | Stream live autoscaler logs |
| `make logs-all` | Stream live logs from all services (autoscaler + proxies) |
| `make cache-size` | Display disk usage of package and tool caches |
| `make clean-cache` | Clear all shared package/tool caches |
| `make build` (or `make build-all`) | Build all images (`arm64` + `amd64` + autoscaler) |
| `make clean` | Force-remove stopped containers and volumes |
| `make env` | Run interactive `.env` configuration wizard |
| `make help` | Show all available Makefile commands |

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Description | Default |
|---|---|---|
| `ACCESS_TOKEN` | GitHub Personal Access Token (PAT) with `repo` scope | *Required* |
| `OWNER` | GitHub username to auto-discover all owned repos | *None* |
| `REPOS` | Comma-separated list of target repos (`owner/repo`) | *None* |
| `ORG` | Target GitHub Organization name | *None* |
| `RUNNER_BACKEND` | Execution driver (`auto`, `docker`, `orbstack-vm`, `wsl2`, `multipass`) | `auto` |
| `AUTO_ROUTE_VM` | Automatically route browser/systemd/e2e jobs to VMs | `true` |
| `AUTO_DISCOVER_REPOS` | Automatically discover and monitor all user repos | `true` |
| `ACTIVE_REPO_DAYS` | Only monitor repos pushed in the last N days | `60` |
| `RUNNER_ARCH` | Runner architectures to spawn (`arm64`, `amd64`, or `both`) | `both` |
| `PROXIES_ENABLED` | Enable apt-cacher, Verdaccio & Athens proxy registries for runners | `true` |
| `CACHE_ENABLED` | Enable persistent package/tool caching across runners | `true` |
| `MIN_RUNNERS` | Minimum idle runners on standby | `0` |
| `MAX_RUNNERS` | Maximum concurrent runner instances | `4` |
| `POLL_INTERVAL` | Queue check interval in seconds | `10` |

---

## 🤝 Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
