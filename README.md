<div align="center">

# ⚡ RunZero

**Zero Cloud Minutes. Zero K8s Bloat. Zero Idle Waste.**

*An intelligent, autoscaling local GitHub Actions runner fleet with **Dual-Engine execution** (Docker Containers & Dedicated Linux VMs via **OrbStack**, **Windows WSL2**, and **Multipass**), with native Apple Silicon (`arm64`) & Intel/AMD (`amd64`), **Verdaccio**, **Athens**, and persistent multi-language caching.*

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
- [Architecture Overview](#-architecture-overview)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [Automatic Cloud Fallback in Workflows](#-automatic-cloud-fallback-in-workflows)
- [Proxy Registries & Caching](#-proxy-registries--caching)
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
| **Built-in Package Proxies** |  **Verdaccio + Athens + Mirrors** | ❌ None (Requires K8s PVC/NFS) | ❌ None | ❌ None |
| **Setup Complexity** |  **1 Command (`make start`)** | ❌ Complex Helm / CRDs |  Simple CLI | ⚠️ Moderate |

---

## 🚀 Dual-Engine Execution (Containers vs. Full VMs)

RunZero is the **first local runner fleet that gives you the choice between ultra-lightweight Docker containers and dedicated Linux Virtual Machines**:

| Engine Backend | Technology | Best Used For |
|---|---|---|
| 🐳 **Docker Containers** (`RUNNER_BACKEND=docker`) | Docker / OrbStack Containers | Fast unit tests, linting, build pipelines, JS/Node/Python steps (**instant ~0.3s boot, ~20MB RAM**). |
| 💻 **OrbStack Linux Machines** (`RUNNER_BACKEND=orbstack-vm`) | Apple Virtualization.framework | **Full systemd support**, background daemons, headless Chrome/Lighthouse, unconfined Docker daemon. |
| 🪟 **Windows WSL2** (`RUNNER_BACKEND=wsl2`) | Windows Subsystem for Linux 2 | Native Linux VM execution on Windows 10/11 & Windows Server. |
| 🐧 **Canonical Multipass** (`RUNNER_BACKEND=multipass`) | QEMU / Hyper-V / VirtualBox | Universal cross-platform VM backend for macOS, Linux, and Windows. |

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

## 🐳 Docker & VM Engine Compatibility

| Engine | macOS (Apple Silicon) | macOS (Intel) | Windows | Linux / Homelab |
|---|---|---|---|---|
| 🪐 **OrbStack** *(Recommended for Mac)* | ⭐ **Containers + Linux VMs** | ⭐ Fast | — | — |
| 🐳 **Docker Desktop** |  Native Containers |  Native Containers |  Native Containers |  Native Containers |
| 🪟 **Windows WSL2** | — | — | ⭐ **Native Linux VMs** | — |
| 🐧 **Native Linux Docker** |  Native (ARM64) |  Native (AMD64) | — | ⭐ **Native (Best for Servers)** |
| 🚀 **Canonical Multipass** |  Native VMs |  Native VMs |  Native VMs |  Native VMs |

---

## 🌟 Key Features

1. **Intelligent Dynamic Autoscaling**:
   - Watches your GitHub queue for unclaimed jobs.
   - Spins up ephemeral instances (`--ephemeral`) on-demand and tears them down immediately upon job completion (**0 MB RAM consumed when idle**).
2. **Owner-Wide Multi-Repo Auto-Discovery**:
   - Automatically monitors **all active repositories** under your personal GitHub account (`OWNER=your-username`), explicit repo lists, or GitHub Organizations.
3. **Pluggable Multi-Backend Drivers**:
   - Easily switch between Docker containers, OrbStack VMs, Windows WSL2, and Canonical Multipass via `RUNNER_BACKEND`.
4. **Adaptive GitHub API Rate-Limiting**:
   - Intelligently filters to active repositories and dynamically paces API calls to keep you safely within GitHub's 5,000 req/hr ceiling.
5. **Built-in Local Proxy Registries & Caching**:
   - **Verdaccio** (`:49501`) for instant npm/yarn/pnpm caching + web dashboard.
   - **Athens** (`:49500`) for immutable Go module caching.
   - **Docker Registry Mirror** (`:49502`) for Docker Hub pull-through caching.
   - **Tool Cache Volume** for `actions/setup-node`, `setup-python`, `setup-dotnet`, `setup-go` toolchains.
6. **Zero Cloud Bill**:
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
│   ├── autoscaler.py                      #    Dynamic queue monitor, rate limiter & hybrid router
│   └── drivers/                           #    Pluggable Execution Drivers
│       ├── __init__.py                    #    RunnerDriver interface & discovery factory
│       ├── docker_driver.py               #    Docker container engine
│       ├── orbstack_vm_driver.py          #    OrbStack macOS Linux VM engine (with proxy caching)
│       ├── wsl_driver.py                  #    Windows WSL2 engine (with proxy caching)
│       └── multipass_driver.py            #    Canonical Multipass engine (with proxy caching)
├── docker/                                # 🐳 Container Build Manifests & Entrypoints
│   ├── Dockerfile                         #    Multi-arch runner image (ARM64 + AMD64)
│   ├── Dockerfile.autoscaler              #    Autoscaler daemon container
│   └── start.sh                           #    Runner entrypoint with proxy auto-detect
├── tests/                                 # 🧪 Comprehensive Test Suite (66 Tests)
│   ├── test_autoscaler.py                 #    Autoscaler, rate limiting & hybrid routing tests
│   ├── test_drivers.py                    #    All driver lifecycle & error branch tests
│   └── test_shell_scripts.py              #    Shell script syntax & entrypoint tests
├── website/                               # 🚀 Astro Static Website & Documentation
│   ├── src/                               #    Astro components, pages (Hero + Docs) & styles
│   ├── public/                            #    Self-hosted fonts and SVG assets
│   ├── astro.config.mjs                   #    Astro static SSG configuration
│   └── package.json                       #    Website dependencies
├── docs/                                  # 🌐 Compiled GitHub Pages Website
│   ├── index.html                         #    Compiled Hero Landing Page
│   └── docs/index.html                    #    Compiled Dedicated Documentation Page
├── tests/                                 # 🧪 Comprehensive Test Suite (68 Tests)
│   ├── test_autoscaler.py                 #    Autoscaler, rate limiting & hybrid routing tests
│   ├── test_drivers.py                    #    All driver lifecycle & error branch tests
│   └── test_shell_scripts.py              #    Shell script syntax & wizard tests
├── .github/
│   ├── ISSUE_TEMPLATE/                    # 📋 Community Issue Templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/                         # 🤖 GitHub Actions CI/CD
│   │   ├── ci.yml                         #    Syntax, Flake8, Mypy, Pytest & Astro build validation
│   │   ├── deploy-pages.yml               #    Auto-deploys website to GitHub Pages
│   │   └── release.yml                    #    Automated SemVer releases & changelogs on main
│   └── PULL_REQUEST_TEMPLATE.md           # 📝 Reviewer checklist
├── docker-compose.yml                     # 🚀 Orchestration (Autoscaler + Verdaccio + Athens)
├── Makefile                               # 🛠️ Unified management commands
├── pyproject.toml                         # ⚙️ Python project configuration (Pytest, Mypy, Mutmut)
├── .env.example                           # ⚙️ Configuration template
├── CONTRIBUTING.md                        # 🤝 Contributor guidelines & Git-Flow guide
├── CODE_OF_CONDUCT.md                     # 📜 Community standards
├── SECURITY.md                            # 🔒 Security policy
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
PROXIES_ENABLED=true # Starts Verdaccio, Athens & Docker Mirror
```

### 2. Build images:
```bash
make build          # Builds ARM64 + AMD64 + Autoscaler
```

### 3. Start the Autoscaler & Proxies:
```bash
make start          # (or make run)
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
| `make test` | Run fast local unit tests directly (68 tests in ~0.9s) |
| `make test-suite` | Run Flake8 linter, Mypy static type checker, and Pytest coverage in container |
| `make mutation-test` | Run Mutmut mutation testing suite across all drivers and autoscaler |

---

## 📋 Makefile Commands

| Command | Description |
|---|---|
| `make start` (or `make run`, `make up`) | Launch autoscaler, Verdaccio, Athens, and Docker mirror |
| `make stop` (or `make down`) | Gracefully stop the autoscaler, proxies, and active runners |
| `make status` (or `make ps`) | Display running autoscaler, proxies & active ephemeral runners |
| `make test` | Run local unit tests directly with `unittest` |
| `make test-suite` | Run Flake8 linter, Mypy type-checker, and Pytest coverage report |
| `make mutation-test` | Run Mutmut mutation testing suite |
| `make website-dev` | Start Astro documentation website development server |
| `make website-build` | Build Astro static website and synchronize to `docs/` |
| `make docs` | Preview the documentation website locally in your browser |
| `make vm-list` | Display active OrbStack Linux runner VMs |
| `make vm-clean` | Clean up any orphaned RunZero VMs |
| `make verdaccio-ui` | Open Verdaccio Web UI at `http://localhost:49501` |
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
| `PROXIES_ENABLED` | Enable Verdaccio & Athens proxy registries for runners | `true` |
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