#!/usr/bin/env python3
"""
Local GitHub Actions Runner Autoscaler
Supports multi-architecture: Apple Silicon ARM64 (native) and AMD64 / x86_64 (via OrbStack Rosetta).
Includes persistent multi-language package caching & proxy registries (Verdaccio, Athens, Docker Mirror).
"""

import os
import sys
import time
import signal
import json
import urllib.request
import urllib.error
import subprocess
import uuid

# Configuration from environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("OWNER", "").strip()
ORG = os.getenv("ORG", "").strip()
REPOS_CONFIG = os.getenv("REPOS") or os.getenv("REPO", "")
AUTO_DISCOVER = os.getenv("AUTO_DISCOVER_REPOS", "true").lower() in ("true", "1", "yes")

# Architecture configuration: 'arm64', 'amd64', or 'both'
RUNNER_ARCH = os.getenv("RUNNER_ARCH", "both").lower().strip()
RUNNER_LABELS_CUSTOM = os.getenv("RUNNER_LABELS", "").strip()

MIN_RUNNERS = int(os.getenv("MIN_RUNNERS", "0"))
MAX_RUNNERS = int(os.getenv("MAX_RUNNERS", "4"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))
DOCKER_SOCK = os.getenv("DOCKER_SOCK", "/var/run/docker.sock")
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK", "runner-network")

# Persistent Cache & Proxy Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
PROXIES_ENABLED = os.getenv("PROXIES_ENABLED", "true").lower() in ("true", "1", "yes")
HOST_CACHE_DIR = os.getenv("HOST_CACHE_DIR") or os.path.expanduser("~/.local-github-runner/cache")

API_BASE = "https://api.github.com"
running = True

def signal_handler(signum, frame):
    global running
    print("\n[Autoscaler] Received shutdown signal. Cleaning up...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def init_cache_dirs():
    """Ensure host cache directories exist."""
    if not CACHE_ENABLED:
        return {}

    subdirs = {
        "toolcache": "/opt/hostedtoolcache",
        "npm": "/home/runner/.npm",
        "yarn": "/home/runner/.cache/yarn",
        "pnpm": "/home/runner/.local/share/pnpm/store",
        "pip": "/home/runner/.cache/pip",
        "uv": "/home/runner/.cache/uv",
        "go-mod": "/home/runner/go/pkg/mod",
        "go-build": "/home/runner/.cache/go-build",
        "cargo-registry": "/home/runner/.cargo/registry"
    }

    os.makedirs(HOST_CACHE_DIR, exist_ok=True)
    mount_mappings = {}
    for key, container_path in subdirs.items():
        host_path = os.path.join(HOST_CACHE_DIR, key)
        os.makedirs(host_path, exist_ok=True)
        mount_mappings[host_path] = container_path

    return mount_mappings

def github_request(endpoint):
    """Perform authenticated GitHub REST API GET request."""
    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "Local-GitHub-Runner-Autoscaler")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"[Autoscaler] API Error ({e.code}) for {endpoint}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[Autoscaler] Request Error for {endpoint}: {e}", file=sys.stderr)
        return None

def discover_repositories():
    """Discover list of repositories to monitor."""
    repos = set()

    # Explicit list from REPOS / REPO
    if REPOS_CONFIG:
        for r in REPOS_CONFIG.split(","):
            r = r.strip()
            if r:
                repos.add(r)

    # Auto-discover from authenticated user with pagination
    if AUTO_DISCOVER and ACCESS_TOKEN:
        page = 1
        while True:
            data = github_request(f"/user/repos?per_page=100&affiliation=owner&page={page}")
            if not isinstance(data, list) or not data:
                break
            for item in data:
                if isinstance(item, dict) and not item.get("archived", False):
                    full_name = item.get("full_name", "")
                    if OWNER and not full_name.startswith(f"{OWNER}/"):
                        continue
                    repos.add(full_name)
            if len(data) < 100:
                break
            page += 1

    return sorted(list(repos))

def get_queued_runs_for_repo(repo_full_name):
    """Count actual queued (unclaimed) jobs for a repository across active runs."""
    data = github_request(f"/repos/{repo_full_name}/actions/runs?status=queued")
    if not data or "workflow_runs" not in data:
        return 0
    total_jobs = 0
    for run in data["workflow_runs"]:
        jobs_data = github_request(f"/repos/{repo_full_name}/actions/runs/{run['id']}/jobs?filter=latest")
        if jobs_data and "jobs" in jobs_data:
            total_jobs += sum(1 for j in jobs_data["jobs"] if j.get("status") == "queued")
    return total_jobs

def get_managed_containers():
    """Get list of container IDs and their running states created by this autoscaler."""
    try:
        res = subprocess.run(
            [
                "docker", "ps", "-a",
                "--filter", "label=managed-by=local-autoscaler",
                "--format", "{{.ID}}|{{.Status}}|{{.Names}}|{{.State}}|{{.Label \"target-repo\"}}|{{.Label \"target-arch\"}}"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        containers = []
        for line in res.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 6:
                containers.append({
                    "id": parts[0],
                    "status": parts[1],
                    "name": parts[2],
                    "state": parts[3],
                    "target_repo": parts[4],
                    "target_arch": parts[5]
                })
        return containers
    except Exception as e:
        print(f"[Autoscaler] Docker ps error: {e}", file=sys.stderr)
        return []

def prune_exited_containers(containers):
    """Remove exited/stopped runner containers."""
    for c in containers:
        if c["state"] in ("exited", "dead"):
            print(f"[Autoscaler] Removing finished runner container: {c['name']} ({c['id']})")
            subprocess.run(["docker", "rm", "-f", c["id"]], capture_output=True)

def spawn_runner(repo=None, org=None, arch="arm64", cache_mounts=None):
    """Spawn a new ephemeral runner container with cache mounts and proxy network."""
    unique_id = uuid.uuid4().hex[:6]
    name_suffix = f"-{repo.replace('/', '-')}" if repo else (f"-{org}" if org else "")
    container_name = f"local-runner-{arch}{name_suffix}-{unique_id}"
    image_tag = f"local-github-runner:{arch}"
    platform_flag = f"linux/{arch}"

    default_labels = f"self-hosted,local,{arch}"
    if arch == "amd64":
        default_labels = "self-hosted,local,x64,amd64"

    labels = RUNNER_LABELS_CUSTOM if RUNNER_LABELS_CUSTOM else default_labels

    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--platform", platform_flag,
        "--network", DOCKER_NETWORK,
        "--label", "managed-by=local-autoscaler",
        "--label", f"target-repo={repo or ''}",
        "--label", f"target-arch={arch}",
        "-e", f"ACCESS_TOKEN={ACCESS_TOKEN}",
        "-e", f"RUNNER_NAME={container_name}",
        "-e", f"RUNNER_LABELS={labels}",
        "-e", "EPHEMERAL=true",
        "-e", "RUNNER_WORKDIR=_work",
        "-e", "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
        "-v", f"{DOCKER_SOCK}:/var/run/docker.sock"
    ]

    # Proxy registries configuration
    if PROXIES_ENABLED:
        cmd.extend([
            "-e", "NPM_CONFIG_REGISTRY=http://verdaccio:4873/",
            "-e", "GOPROXY=http://athens:3000,https://proxy.golang.org,direct"
        ])

    # Attach shared package and tool cache volume mounts
    if cache_mounts:
        for host_p, cont_p in cache_mounts.items():
            cmd.extend(["-v", f"{host_p}:{cont_p}"])

    if repo:
        cmd.extend(["-e", f"REPO={repo}"])
    elif org:
        cmd.extend(["-e", f"ORG={org}"])

    cmd.append(image_tag)

    print(f"[Autoscaler] 🚀 Spawning ephemeral [{arch.upper()}] runner {container_name} on network '{DOCKER_NETWORK}' for {repo or org}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return container_name
    except subprocess.CalledProcessError as e:
        print(f"[Autoscaler] Error launching container: {e.stderr.decode()}", file=sys.stderr)
        return None

def get_target_architectures():
    """Return list of architectures to spin up."""
    if RUNNER_ARCH in ("both", "all", "dual"):
        return ["arm64", "amd64"]
    elif RUNNER_ARCH in ("amd64", "x86_64", "x64"):
        return ["amd64"]
    else:
        return ["arm64"]

def main():
    if not ACCESS_TOKEN:
        print("[Autoscaler] Error: ACCESS_TOKEN is required for autoscaling.", file=sys.stderr)
        sys.exit(1)

    architectures = get_target_architectures()
    cache_mounts = init_cache_dirs()

    print("=" * 60)
    print(" Local GitHub Actions Runner Autoscaler (OrbStack)")
    print(f" Architectures: {', '.join([a.upper() for a in architectures])}")
    print(f" Cache Directory: {HOST_CACHE_DIR} ({'Enabled' if CACHE_ENABLED else 'Disabled'})")
    print(f" Proxy Registries: {'Enabled (Verdaccio, Athens, Docker Mirror)' if PROXIES_ENABLED else 'Disabled'}")
    print(f" Max Concurrency: {MAX_RUNNERS} | Min Runners: {MIN_RUNNERS}")
    print(f" Check Interval:  {POLL_INTERVAL}s")
    print("=" * 60)

    last_discovery_time = 0
    tracked_repos = []

    while running:
        # Refresh tracked repositories every 60 seconds if auto-discovering
        now = time.time()
        if not ORG and (now - last_discovery_time > 60 or not tracked_repos):
            tracked_repos = discover_repositories()
            last_discovery_time = now
            print(f"[Autoscaler] Monitoring {len(tracked_repos)} repository(ies): {', '.join(tracked_repos)}")

        # Check existing runner containers
        all_containers = get_managed_containers()
        prune_exited_containers(all_containers)

        active_containers = [c for c in get_managed_containers() if c["state"] == "running"]
        active_count = len(active_containers)

        if ORG:
            # For organizations
            if active_count < MIN_RUNNERS and active_count < MAX_RUNNERS:
                needed = min(MIN_RUNNERS - active_count, MAX_RUNNERS - active_count)
                for i in range(needed):
                    arch = architectures[i % len(architectures)]
                    spawn_runner(org=ORG, arch=arch, cache_mounts=cache_mounts)
        else:
            # For repositories: check queued runs per repository
            queued_by_repo = {}
            total_queued = 0

            for repo in tracked_repos:
                queued = get_queued_runs_for_repo(repo)
                if queued > 0:
                    queued_by_repo[repo] = queued
                    total_queued += queued

            # Check if we need to spawn runners for queued jobs
            if total_queued > 0:
                print(f"[Autoscaler] Detected {total_queued} queued unclaimed job(s) across repos: {queued_by_repo}")

            for repo, count in queued_by_repo.items():
                active_for_repo = sum(1 for c in active_containers if c["target_repo"] == repo)
                needed = count - active_for_repo

                while needed > 0 and len(active_containers) < MAX_RUNNERS:
                    for arch in architectures:
                        if len(active_containers) >= MAX_RUNNERS or needed <= 0:
                            break
                        spawned = spawn_runner(repo=repo, arch=arch, cache_mounts=cache_mounts)
                        if spawned:
                            active_containers.append({"name": spawned, "target_repo": repo, "state": "running", "target_arch": arch})
                            needed -= 1

            # Maintain MIN_RUNNERS if configured
            if active_count < MIN_RUNNERS and active_count < MAX_RUNNERS and tracked_repos:
                needed = min(MIN_RUNNERS - active_count, MAX_RUNNERS - active_count)
                for i in range(needed):
                    arch = architectures[i % len(architectures)]
                    spawn_runner(repo=tracked_repos[0], arch=arch, cache_mounts=cache_mounts)

        time.sleep(POLL_INTERVAL)

    # Cleanup remaining containers on stop
    print("[Autoscaler] Stopping managed containers on shutdown...")
    for c in get_managed_containers():
        subprocess.run(["docker", "stop", c["id"]], capture_output=True)
        subprocess.run(["docker", "rm", c["id"]], capture_output=True)
    print("[Autoscaler] Shutdown complete.")

if __name__ == "__main__":
    main()
