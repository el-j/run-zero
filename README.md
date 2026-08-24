# Local GitHub Actions Runner & Autoscaler (OrbStack)

A local GitHub Actions runner setup with **multi-architecture support (ARM64 + AMD64/x86_64)**, **intelligent dynamic autoscaling**, **Verdaccio & Athens caching proxy registries**, **persistent multi-language caching**, and **owner-wide / multi-repo coverage**, optimized for **OrbStack** on Apple Silicon MacBooks (M1/M2/M3/M4).

---

## ⚡ Proxy Registries & Caching Architecture

When running CI jobs on fresh or ephemeral containers, packages are automatically proxied and cached locally on your machine via dedicated proxy sidecars:

```
   ┌─────────────────────────────────────────────────────────────┐
   │             Host Machine (OrbStack / Docker)                │
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

| Proxy / Cache Service | Host Port | Purpose |
|---|---|---|
| **Verdaccio** | [`http://localhost:4873`](http://localhost:4873) | Fast local NPM caching proxy + Web UI to inspect packages |
| **Athens** | [`http://localhost:3000`](http://localhost:3000) | Local immutable caching proxy for Go modules (`proxy.golang.org`) |
| **Docker Registry Mirror** | `http://localhost:5001` | Pull-through cache for Docker Hub images to bypass rate limits |
| **Tool Cache Volume** | `~/.local-github-runner/cache/` | Persistent `/opt/hostedtoolcache` for `actions/setup-*` |
| **Python / Rust / Yarn** | `~/.local-github-runner/cache/` | Direct volume cache for pip, uv, yarn, pnpm, and cargo |

---

## ⚡ Multi-Architecture on Apple Silicon (M3 MacBook)

Thanks to **OrbStack with Rosetta emulation**, you can run **both native ARM64 runners and AMD64 (x86_64) runners** directly on your MacBook:

- **ARM64 Native (`local-github-runner:arm64`)**: Runs at full bare-metal Apple Silicon speed. Labels: `[self-hosted, local, arm64]`.
- **AMD64 / x86_64 (`local-github-runner:amd64`)**: Runs x86_64 builds via OrbStack's Rosetta acceleration. Labels: `[self-hosted, local, x64, amd64]`.
- **Dual Support (`RUNNER_ARCH=both`)**: The autoscaler can spawn both ARM64 and AMD64 runner containers on demand!

---

## 🚀 Quick Start with `make`

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

### 2. Build images (one-time or on updates):
```bash
make build          # Builds ARM64 + AMD64 + Autoscaler
```

### 3. Start the Autoscaler & Proxies:
```bash
make start
```

### 4. Open Verdaccio Web UI:
```bash
make verdaccio-ui   # Opens http://localhost:4873 in your browser
```

### 5. Check status & live logs:
```bash
make status         # View active autoscaler, proxies, and dynamic runner containers
make logs           # Stream live autoscaler logs
make logs-all       # Stream logs from autoscaler + Verdaccio + Athens
```

### 6. Stop the Autoscaler & Proxies:
```bash
make stop
```

---

## 📋 Available Make Commands

| Command | Description |
|---|---|
| `make start` (or `make up`) | Launch the autoscaler, Verdaccio, Athens, and Docker mirror |
| `make stop` (or `make down`) | Gracefully stop the autoscaler, proxies, and active runners |
| `make status` (or `make ps`) | Display running autoscaler, proxies & active ephemeral runners |
| `make verdaccio-ui` | Open Verdaccio Web UI at `http://localhost:4873` |
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