"""
Environment every RunZero runner exports so job tooling actually uses the host caches (#66-#69).

One source of truth for all drivers (Docker, OrbStack, Multipass, WSL2). Variables exported
before `run.sh` are inherited by every job step, exactly like GitHub's own runner images.

Each entry fixes a measured cache miss (el-j/run-zero#76):
- `RUNNER_TOOL_CACHE`/`AGENT_TOOLSDIRECTORY`: without them `actions/setup-node`/`setup-go`
  install into the throwaway `_work/_tool` instead of the mounted `/opt/hostedtoolcache`.
- `pnpm_config_*`: pnpm 11 ignores every `npm_config_*` variable, so Verdaccio and the
  mounted store were bypassed; pnpm <=10 reads only `npm_config_*`, so both are set.
- `PLAYWRIGHT_BROWSERS_PATH`: points browser downloads at the mounted per-arch cache.
- `RUNZERO`/`RUNZERO_CACHES`: lets a workflow skip `actions/cache` steps that only
  duplicate (slowly) what the host already caches, e.g. `if: env.RUNZERO != '1'`.
"""

import shlex

TOOL_CACHE = "/opt/hostedtoolcache"
PNPM_STORE = "/home/runner/.local/share/pnpm/store"
PLAYWRIGHT_BROWSERS = "/home/runner/.cache/ms-playwright"

# Advertised in RUNZERO_CACHES when host cache mounts are active.
MOUNTED_CACHES = ("toolcache", "npm", "pnpm", "yarn", "pip", "uv", "go", "dotnet", "cargo", "playwright")


def _rehome(path: str, home: str) -> str:
    """Move a /home/runner path under `home` (Multipass' guest user is `ubuntu`)."""
    return home + path[len("/home/runner") :] if path.startswith("/home/runner") else path


def cache_env(caches_mounted: bool, home: str = "/home/runner") -> dict[str, str]:
    """Variables pointing job tooling at the cache locations (and the RUNZERO marker).

    The tool cache variables are always set: `/opt/hostedtoolcache` exists in every runner,
    and is host-backed whenever caching is enabled. Store and browser paths are only set
    when the host caches are mounted, so a cache-less runner keeps tool defaults.
    """
    env = {"RUNZERO": "1", "RUNNER_TOOL_CACHE": TOOL_CACHE, "AGENT_TOOLSDIRECTORY": TOOL_CACHE}
    if caches_mounted:
        store = _rehome(PNPM_STORE, home)
        env.update(
            {
                "RUNZERO_CACHES": ",".join(MOUNTED_CACHES),
                "pnpm_config_store_dir": store,
                "npm_config_store_dir": store,
                "PLAYWRIGHT_BROWSERS_PATH": _rehome(PLAYWRIGHT_BROWSERS, home),
            }
        )
    return env


def registry_env(npm_registry: str) -> dict[str, str]:
    """Point npm, pnpm (<=10 and 11+), and Yarn classic/berry at the Verdaccio proxy `npm_registry`."""
    return {
        "npm_config_registry": npm_registry,
        "NPM_CONFIG_REGISTRY": npm_registry,
        "pnpm_config_registry": npm_registry,
        "YARN_REGISTRY": npm_registry,
        "YARN_NPM_REGISTRY_SERVER": npm_registry,
    }


def export_block(env: dict[str, str], expand: bool = False) -> str:
    """Render `env` as shell `export` lines.

    Values are shell-quoted. With `expand=True` they are double-quoted instead so guest-side
    references like `${HOST_IP}` expand; only pass trusted, driver-defined values then.
    """
    if expand:
        return "\n".join(f'export {k}="{v}"' for k, v in env.items())
    return "\n".join(f"export {k}={shlex.quote(v)}" for k, v in env.items())


def docker_env_args(env: dict[str, str]) -> list[str]:
    """Render `env` as `docker run` `-e K=V` arguments."""
    args: list[str] = []
    for k, v in env.items():
        args.extend(["-e", f"{k}={v}"])
    return args
