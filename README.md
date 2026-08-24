<div align="center">

# ⚡ RunZero

**Zero Cloud Minutes. Zero K8s Bloat. Zero Idle Waste.**

*An intelligent, autoscaling local GitHub Actions runner fleet for **OrbStack**, **Docker Desktop**, and **Linux Docker** on Apple Silicon (`arm64`) & Intel/AMD (`amd64`), with built-in **Verdaccio**, **Athens**, and persistent multi-language caching.*

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
- [Docker Engine Compatibility (OrbStack vs. Docker Desktop vs. Linux)](#-docker-engine-compatibility)
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
| **Target Environment** | **Local Mac / Workstation** | Enterprise Cloud K8s Fleet | Local CLI Scratchpad | Single Homelab Container |
| **Idle RAM Overhead** | **~20 MB (0 MB at idle)** | **1.5 GB – 3.5 GB (Heavy K8s)** | 0 MB (Manual CLI only) | ~500 MB+ (Always running) |
| **Runs Real GitHub Queue** |  **Yes** (Pulls live jobs) |  **Yes** | ❌ **No** (Local emulation only) |  **Yes** |
| **Personal Account Multi-Repo** |  **Automatic Discovery** | ❌ **No** (Org / Enterprise only) | ❌ N/A | ❌ **No** (1 repo per container) |
| **Multi-Arch (Apple Silicon + x86_64)** |  **Native ARM64 + Rosetta AMD64** | ⚠️ Complex (K8s node taints) | ⚠️ Partial | ❌ Fixed single arch |
| **Built-in Package Proxies** |  **Verdaccio + Athens + Mirrors** | ❌ None (Requires K8s PVC/NFS) | ❌ None | ❌ None |
| **Setup Complexity** |  **1 Command (`make start`)** | ❌ Complex Helm / CRDs |  Simple CLI | ⚠️ Moderate |

---

## 🐳 Docker Engine Compatibility

RunZero uses the standard Docker API socket (`/var/run/docker.sock`) and standard Docker Compose v2, making it **100% compatible across all major container engines**:

| Container Engine | macOS (Apple Silicon) | macOS (Intel) | Linux / Homelab | Highlights |
|---|---|---|---|---|
| 🪐 **OrbStack** *(Recommended for Mac)* | ⭐ **Native + Rosetta 2** | ⭐ Fast | — | **Fastest x86_64 emulation via Rosetta 2**, instant startup, ~0.1% idle CPU. |
| 🐳 **Docker Desktop** |  Native + QEMU/Rosetta |  Native |  Native | Standard Docker environment for Mac and Windows. |
| 🦭 **Colima / Lima** |  Native + QEMU/Rosetta |  Native | — | Lightweight CLI-based container runtime for macOS. |
| 🐧 **Native Linux Docker Engine** |  Native (ARM64) |  Native (AMD64) | ⭐ **Native (Best for Servers)** | Zero VM layer, runs on Ubuntu, Debian, Arch, Fedora, homelabs. |

---

## 🌟 Key Features

1. **Intelligent Dynamic Autoscaling**:
   - Watches your GitHub queue for unclaimed jobs.
   - Spins up ephemeral containers (`--ephemeral`) on-demand and tears them down immediately upon job completion (**0 MB RAM consumed when idle**).
2. **Owner-Wide Multi-Repo Auto-Discovery**:
   - Automatically monitors **all repositories** under your personal GitHub account (`OWNER=your-username`), explicit repo lists, or GitHub Organizations.
3. **Multi-Architecture on Apple Silicon**:
   - **Native ARM64** (`local-github-runner:arm64`) for bare-metal M-series speed.
   - **AMD64 / x86_64** (`local-github-runner:amd64`) via OrbStack's Rosetta 2 emulation.
4. **Built-in Local Proxy Registries & Caching**:
   - **Verdaccio** (`:4873`) for instant npm/yarn/pnpm caching + web dashboard.
   - **Athens** (`:3000`) for immutable Go module caching.
   - **Docker Registry Mirror** (`:5001`) for Docker Hub pull-through caching.
   - **Tool Cache Volume** for `actions/setup-node`, `setup-python`, `setup-go` toolchains.
5. **Zero Cloud Bill**:
   - Self-hosted runners **never** consume GitHub Actions minutes (100% free and unlimited).

---

## 🏗️ Architecture Overview

```
   ┌─────────────────────────────────────────────────────────────┐
   │             Host Machine (OrbStack / Docker on Mac)         │
   │                                                             │
   │  ┌──────────────────────┐        ┌──────────────────────┐  │
   │  │ Verdaccio (Port 4873)│        │ Athens (Port 3000)   │  │
   │  │ Caches NPM Packages  │        │ Caches Go Modules    │  │
   │  │ (Web UI at :4873)    │        │ (Immutable Go proxy) │  │
   │  └──────────▲───────────┘        └──────────▲───────────┘  │
   │             │                               │              │
   │  ┌──────────┴───────────────────────────────┴───────────┐  │
   │  │ Docker Registry Mirror (Port 5001 -> 5000)           │  │
   │  │ Pull-through cache for Docker Hub (Avoids limits)    │  │
   │  └──────────────────────▲───────────────────────────────┘  │
   └─────────────────────────┼───────────────────────────────────┘
                             │ (runner-network)
          ┌──────────────────┴──────────────────┐
          ▼                                     ▼
┌───────────────────────────┐         ┌───────────────────────────┐
│ Ephemeral Runner (ARM64)  │         │ Ephemeral Runner (AMD64)  │
│ NPM -> http://verdaccio   │         │ NPM -> http://verdaccio   │
│ Go  -> http://athens      │         │ Go  -> http://athens      │
└───────────────────────────┘         └───────────────────────────┘
```

---

## 📁 Repository Structure

```text
.
├── docker/                                # 🐳 Container Definitions & Runner Scripts
│   ├── autoscaler.py                      #    Dynamic queue monitor & container spawner
│   ├── Dockerfile                         #    Multi-arch runner image (ARM64 + AMD64)
│   ├── Dockerfile.autoscaler              #    Autoscaler daemon container
│   └── start.sh                           #    Runner entrypoint with proxy auto-detect
├── docs/                                  # 🌐 Documentation & GitHub Pages Website
│   ├── favicon.svg                        #    RunZero vector icon
│   ├── fonts/                             #    Self-hosted local fonts (zero CDN)
│   ├── index.html                         #    Interactive dark-mode landing page
│   ├── style.css                          #    Modular styles
│   └── script.js                          #    Client interactions
├── .github/
│   ├── ISSUE_TEMPLATE/                    # 📋 Community Issue Templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/                         # 🤖 GitHub Actions CI/CD
│   │   ├── ci.yml                         #    Syntax, config & build validation
│   │   └── deploy-pages.yml               #    Auto-deploys docs/ to GitHub Pages
│   └── PULL_REQUEST_TEMPLATE.md           # 📝 Reviewer checklist
├── docker-compose.yml                     # 🚀 Orchestration (Autoscaler + Verdaccio + Athens)
├── Makefile                               # 🛠️ Unified management commands
├── .env.example                           # ⚙️ Configuration template
├── CONTRIBUTING.md                        # 🤝 Contributor guidelines
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
OWNER=el-j
AUTO_DISCOVER_REPOS=true
RUNNER_ARCH=both    # 'both', 'amd64', or 'arm64'
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

### 4. Open Verdaccio Web UI:
```bash
make verdaccio-ui   # Opens http://localhost:4873 in your browser
```

### 5. Check status & live logs:
```bash
make status         # View active autoscaler, proxies, and dynamic runner containers
make logs           # Stream live autoscaler logs
```

### 6. Stop the Autoscaler & Proxies:
```bash
make stop           # (or make down)
```

---

## 🔄 Automatic Cloud Fallback in Workflows

To make your GitHub Actions automatically switch to the local runner when cloud minutes expire:

```yaml
jobs:
  build:
    runs-on: ${{ vars.USE_LOCAL_RUNNER == 'true' && fromJSON('["self-hosted", "local"]') || 'ubuntu-latest' }}
    steps:
      - uses: actions/checkout@v7
      - run: npm test
```

Set `USE_LOCAL_RUNNER=true` in GitHub Repository/Organization Variables, and all jobs will immediately route to your local RunZero fleet without touching workflow files!

---

## ⚡ Proxy Registries & Caching

| Service / Tool | Host Path / Port | Container Mount | Purpose |
|---|---|---|---|
| **Verdaccio** | [`http://localhost:4873`](http://localhost:4873) | `http://verdaccio:4873` | Fast local NPM caching proxy + Web UI |
| **Athens** | [`http://localhost:3000`](http://localhost:3000) | `http://athens:3000` | Immutable Go module proxy |
| **Docker Registry Mirror** | `http://localhost:5001` | `http://docker-mirror:5000` | Docker Hub pull-through cache |
| **Tool Cache** | `~/.local-github-runner/cache/toolcache` | `/opt/hostedtoolcache` | Preserves `actions/setup-*` binaries |
| **pip / uv / yarn / cargo** | `~/.local-github-runner/cache/` | Direct container caches | Instant package re-use |

---

## 🍎 Multi-Architecture Builds

### Target AMD64 (x86_64) Specifically:
```yaml
jobs:
  build-amd64:
    runs-on: [ self-hosted, local, x64 ]
    steps:
      - uses: actions/checkout@v7
      - run: uname -m # Prints: x86_64
```

### Target Native ARM64 (Apple Silicon):
```yaml
jobs:
  build-arm64:
    runs-on: [ self-hosted, local, arm64 ]
    steps:
      - uses: actions/checkout@v7
      - run: uname -m # Prints: aarch64
```

---

## 📋 Makefile Commands

| Command | Description |
|---|---|
| `make start` (or `make run`, `make up`) | Launch autoscaler, Verdaccio, Athens, and Docker mirror |
| `make stop` (or `make down`) | Gracefully stop the autoscaler, proxies, and active runners |
| `make status` (or `make ps`) | Display running autoscaler, proxies & active ephemeral runners |
| `make verdaccio-ui` | Open Verdaccio Web UI at `http://localhost:4873` |
| `make docs` | Preview the documentation website locally in your browser |
| `make logs` | Stream live autoscaler logs |
| `make logs-all` | Stream live logs from all services (autoscaler + proxies) |
| `make cache-size` | Display disk usage of package and tool caches |
| `make clean-cache` | Clear all shared package/tool caches |
| `make build` (or `make build-all`) | Build all images (`arm64` + `amd64` + autoscaler) |
| `make build-arm64` | Build native Apple Silicon `arm64` runner |
| `make build-amd64` | Build Intel/AMD `amd64` (x86_64) runner |
| `make clean` | Force-remove stopped containers and volumes |
| `make env` | Generate `.env` from template if missing |
| `make help` | Show all available Makefile commands |

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Description | Default |
|---|---|---|
| `ACCESS_TOKEN` | GitHub Personal Access Token (PAT) with `repo` scope | *Required* |
| `OWNER` | GitHub username to auto-discover all owned repos | *None* |
| `REPOS` | Comma-separated list of target repos (`owner/repo`) | *None* |
| `ORG` | Target GitHub Organization name | *None* |
| `AUTO_DISCOVER_REPOS` | Automatically discover and monitor all user repos | `true` |
| `RUNNER_ARCH` | Runner architectures to spawn (`arm64`, `amd64`, or `both`) | `both` |
| `PROXIES_ENABLED` | Enable Verdaccio & Athens proxy registries for runners | `true` |
| `CACHE_ENABLED` | Enable persistent package/tool caching across runners | `true` |
| `MIN_RUNNERS` | Minimum idle runners on standby | `0` |
| `MAX_RUNNERS` | Maximum concurrent runner containers | `4` |
| `POLL_INTERVAL` | Queue check interval in seconds | `5` |

---

## 🤝 Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.