# Local GitHub Actions Runner & Autoscaler

A local GitHub Actions runner setup with **intelligent dynamic autoscaling** and **multi-repo / owner-wide coverage**, built for **OrbStack** and Docker on macOS (Apple Silicon `arm64` & `x86_64`).

---

## ⚡ Quick Start with `make`

The repository includes a [Makefile](file:///Users/rex-fab-alt/Documents/private/github-runner/Makefile) for simple one-command management:

### 1. Initialize environment:
```bash
make env
```
Edit `.env` and fill in your GitHub PAT and username:
```env
ACCESS_TOKEN=ghp_yourPersonalAccessTokenHere
OWNER=el-j
AUTO_DISCOVER_REPOS=true
```

### 2. Start the Autoscaler:
```bash
make start
```

### 3. Check status & live logs:
```bash
make status   # View active autoscaler and dynamic runner containers
make logs     # Stream live autoscaler logs
```

### 4. Stop the Autoscaler:
```bash
make stop
```

---

## 💡 How GitHub Actions Minutes & Local Fallback Work

### How GitHub Works:
1. **GitHub Cloud Runners (`runs-on: ubuntu-latest`)**:
   - Consume your monthly included GitHub Actions minutes (2,000 min/mo on free accounts).
   - Once your minutes run out (and spending limits are reached), GitHub blocks cloud jobs with an insufficient quota error.
2. **Self-Hosted Local Runners (`runs-on: [self-hosted, local]`)**:
   - **100% FREE & UNLIMITED**: Self-hosted runners **never** consume GitHub Action minutes.
   - Run directly on your machine's hardware with no monthly limits.

---

## 🔄 How to Automatically Switch to the Local Runner When Minutes Run Out

GitHub workflows use the `runs-on` property to decide where a job executes. Here are the 3 recommended ways to automate the fallback:

### Strategy 1: Dynamic Repository Variable Switch (Recommended)

You can make your workflows check a GitHub repository variable (or organization variable) `USE_LOCAL_RUNNER`:

```yaml
jobs:
  build:
    runs-on: ${{ vars.USE_LOCAL_RUNNER == 'true' && fromJSON('["self-hosted", "local"]') || 'ubuntu-latest' }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

- **When you have cloud minutes**: Leave `USE_LOCAL_RUNNER` unset (or `false`), and jobs run on GitHub Cloud.
- **When minutes run out**: Simply set `USE_LOCAL_RUNNER=true` in your GitHub repository/organization settings (`Settings -> Secrets and variables -> Actions -> Variables`). **All your workflows will immediately route to your local runner without changing any code!**

---

### Strategy 2: Dedicated Local CI Workflows (Save 100% of Minutes)

To avoid consuming cloud minutes entirely, set all high-frequency jobs (like `push` on dev branches or PR tests) to run locally, and only use cloud for releases/main:

```yaml
jobs:
  test:
    # Run locally on dev/feature branches, or on self-hosted
    runs-on: ${{ github.ref == 'refs/heads/main' && 'ubuntu-latest' || fromJSON('["self-hosted", "local"]') }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

---

### Strategy 3: Dynamic Manual Dispatch with Auto-Default

Allow developers to manually select cloud or local, with an automatic fallback:

```yaml
on:
  push:
  workflow_dispatch:
    inputs:
      runner:
        description: 'Target runner'
        type: choice
        default: 'local'
        options:
          - local
          - cloud

jobs:
  build:
    runs-on: ${{ (inputs.runner == 'local' || vars.USE_LOCAL_RUNNER == 'true') && fromJSON('["self-hosted", "local"]') || 'ubuntu-latest' }}
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```

---

## 📋 Available Make Commands

| Command | Description |
|---|---|
| `make start` (or `make up`) | Build & launch the autoscaler in background |
| `make stop` (or `make down`) | Gracefully stop the autoscaler and running runners |
| `make status` (or `make ps`) | Display running autoscaler & active ephemeral runners |
| `make logs` | Stream live autoscaler logs |
| `make test` | Run in interactive foreground mode for debugging |
| `make build` | Rebuild runner & autoscaler Docker images |
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
| `MIN_RUNNERS` | Minimum idle runners on standby | `0` |
| `MAX_RUNNERS` | Maximum concurrent runner containers | `4` |
| `POLL_INTERVAL` | Queue check interval in seconds | `5` |
| `RUNNER_LABELS` | Runner labels registered on GitHub | `self-hosted,local` |