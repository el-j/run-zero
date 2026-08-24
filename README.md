# Local GitHub Actions Runner & Autoscaler (OrbStack)

A local GitHub Actions runner setup with **multi-architecture support (ARM64 + AMD64/x86_64)**, **intelligent dynamic autoscaling**, and **multi-repo / owner-wide coverage**, built for **OrbStack** on Apple Silicon MacBooks (M1/M2/M3/M4).

---

## ⚡ Multi-Architecture on Apple Silicon (M3 MacBook)

Thanks to **OrbStack with Rosetta emulation**, you can run **both native ARM64 runners and AMD64 (x86_64) runners** directly on your MacBook:

- **ARM64 Native (`local-github-runner:arm64`)**: Runs at full bare-metal Apple Silicon speed. Labels: `[self-hosted, local, arm64]`.
- **AMD64 / x86_64 (`local-github-runner:amd64`)**: Runs x86_64 builds via OrbStack's Rosetta acceleration. Labels: `[self-hosted, local, x64, amd64]`.
- **Dual Support (`RUNNER_ARCH=both`)**: The autoscaler can spawn both ARM64 and AMD64 runner containers on demand!

---

## 🚀 How to Target Specific Architectures in Workflows

### Target AMD64 (x86_64) Specifically:
```yaml
jobs:
  build-amd64:
    runs-on: [ self-hosted, local, x64 ]
    steps:
      - uses: actions/checkout@v4
      - name: Build for AMD64
        run: |
          echo "Architecture: $(uname -m)" # Output: x86_64
          docker build --platform linux/amd64 -t myapp:x86_64 .
```

### Target ARM64 (Apple Silicon) Specifically:
```yaml
jobs:
  build-arm64:
    runs-on: [ self-hosted, local, arm64 ]
    steps:
      - uses: actions/checkout@v4
      - name: Build for ARM64
        run: |
          echo "Architecture: $(uname -m)" # Output: aarch64
```

### Multi-Architecture Matrix Build Locally:
```yaml
jobs:
  build-multiarch:
    strategy:
      matrix:
        arch: [ arm64, x64 ]
    runs-on: [ self-hosted, local, "${{ matrix.arch }}" ]
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "Building on local ${{ matrix.arch }} runner!"
          uname -m
```

---

## ⚡ Quick Start with `make`

The repository includes a [Makefile](file:///Users/rex-fab-alt/Documents/private/github-runner/Makefile) for simple management:

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
```

### 2. Build the images (one-time or on updates):
```bash
make build          # Builds ARM64 + AMD64 + Autoscaler
```

### 3. Start the Autoscaler:
```bash
make start
```

### 4. Check status & live logs:
```bash
make status   # View active autoscaler and dynamic runner containers
make logs     # Stream live autoscaler logs
```

### 5. Stop the Autoscaler:
```bash
make stop
```

---

## 📋 Available Make Commands

| Command | Description |
|---|---|
| `make start` (or `make up`) | Build & launch the autoscaler in background |
| `make stop` (or `make down`) | Gracefully stop the autoscaler and running runners |
| `make status` (or `make ps`) | Display running autoscaler & active ephemeral runners |
| `make logs` | Stream live autoscaler logs |
| `make build` (or `make build-all`) | Build all images (`arm64` + `amd64` + autoscaler) |
| `make build-arm64` | Build native Apple Silicon `arm64` runner |
| `make build-amd64` | Build Intel/AMD `amd64` (x86_64) runner |
| `make test` | Run in interactive foreground mode for debugging |
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
| `MIN_RUNNERS` | Minimum idle runners on standby | `0` |
| `MAX_RUNNERS` | Maximum concurrent runner containers | `4` |
| `POLL_INTERVAL` | Queue check interval in seconds | `5` |