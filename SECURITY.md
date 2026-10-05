# Security Policy

## Supported Versions

RunZero is pre-1.0. Only the latest commit on `main` receives security fixes.

| Version        | Supported          |
| -------------- | ------------------ |
| `main` (0.0.x) | :white_check_mark: |
| anything older | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in RunZero, please do **NOT** file a public issue.

Instead, please report the vulnerability privately by opening a [GitHub Security Advisory](https://github.com/el-j/run-zero/security/advisories/new) or contacting the maintainers directly.

Please include:
- A description of the issue.
- Steps to reproduce the problem.
- Any potential remediations or workarounds.

We take security seriously and will investigate and address reported issues promptly.

## Threat Model & Hardening

RunZero turns your machine into a self-hosted runner fleet. Read this section before pointing it
at any repository.

### Trust boundaries

**Every workflow that runs on these runners is trusted code with near-root power over the
host.** Self-hosted runners give no isolation comparable to GitHub-hosted ones:

- **Docker backend:** each job container gets the host's `/var/run/docker.sock` and
  `--cap-add SYS_ADMIN`. Access to the Docker socket is equivalent to root on the Docker
  host. A job can start privileged containers, mount the host filesystem, or
  `docker inspect` any container, including the autoscaler (whose environment holds
  `ACCESS_TOKEN`).
- **VM backends (OrbStack, Multipass, WSL2):** jobs run inside a separate Linux guest with
  its own Docker daemon. This is a meaningfully stronger boundary, though it is not a
  sandbox for hostile code. OrbStack VMs also see the host filesystem under `/mnt/mac`.

Consequences:

- **Never enable RunZero for public repositories that accept fork pull requests.**
  Anyone who can open a PR could otherwise run code on your machine. In GitHub, set
  *Settings → Actions → General → Fork pull request workflows* to require approval, or
  keep self-hosted runners on private repositories only.
- Treat anyone with write access to a monitored repository as having local code
  execution on the runner host.

### Credentials and where they flow

| Credential | Held by | Reaches runners? |
| --- | --- | --- |
| `ACCESS_TOKEN` (admin PAT) | autoscaler process / container | **No.** Drivers exchange it on the host for a 1-hour **registration token** (`POST …/actions/runners/registration-token`) and pass only that. The Host VM Bridge never carries the PAT. |
| Registration token | the runner, during `config.sh` | Yes, briefly. `docker/start.sh` removes all credential variables from the environment `run.sh` and job steps inherit. On the Docker backend the container's initial environment is still readable in-container via `/proc/1/environ`. |
| `RUNZERO_BRIDGE_TOKEN` | autoscaler and Host VM Bridge (`.env`, launchd plist `0600`) | No. |

Use a fine-grained PAT scoped to exactly the repositories you monitor, with *Administration:
read & write* (for runner registration) and *Actions: read*. `make env` writes `.env` with
mode `0600`.

**Static compose runners** (the opt-in `profiles:` services) register themselves, so they
receive a credential directly. Prefer giving them `RUNNER_TOKEN` (a registration token) over
the PAT.

### Network exposure

Both control planes can change state: the dashboard can purge caches and prune runners, and
the bridge can spawn and destroy VMs. They are hardened as follows (`src/http_security.py`):

- **Loopback by default.** The dashboard and bridge bind `127.0.0.1`. Compose publishes the
  dashboard on the host's `127.0.0.1:49505` only. On Docker Desktop and OrbStack,
  containers reach a loopback-bound host service as `host.docker.internal`.
- **Host-header allowlist** (defends against DNS rebinding): `localhost`, `127.0.0.1`,
  `::1`, `host.docker.internal`, `host.orb.internal`. Add names with
  `RUNZERO_ALLOWED_HOSTS`.
- **JSON-only POSTs** (`application/json`, 64 KiB max, object bodies). There are **no CORS
  grants**, so another website open in your browser cannot drive these endpoints.
- **Bridge bearer token.** When `RUNZERO_BRIDGE_TOKEN` is set, every `/api/drivers/*`
  route requires `Authorization: Bearer <token>`. `make env` generates the token. The
  bridge **refuses to start** on a non-loopback address without a token. Without a token
  on loopback it logs a warning, because any local process or container could then drive
  it.
- **Validated spawn inputs.** `repo`/`org`/labels must match GitHub naming rules, and
  `extra_env` keys must be plain identifiers that don't override bootstrap variables.
  Every value interpolated into a VM bootstrap script is shell-quoted.

To expose the dashboard on a LAN deliberately, set both `DASHBOARD_PUBLISH_ADDR=0.0.0.0`
and `RUNZERO_ALLOWED_HOSTS=<the name you browse to>`. The dashboard has no login; put it
behind an authenticating reverse proxy.

**Linux Docker hosts:** `host.docker.internal` maps to the `docker0` gateway, not host
loopback. If the containerized autoscaler must reach the bridge there, set
`HOST_VM_BRIDGE_HOST` to that gateway address **and** set `RUNZERO_BRIDGE_TOKEN`.

### Proxy caches

Verdaccio, Athens, devpi, kellnr, apt-cacher-ng and the Docker registry mirror are shared,
unauthenticated pull-through caches on published ports. A job can read anything another job
pulled through them. Do not use them for private packages that must stay isolated between
repositories.
