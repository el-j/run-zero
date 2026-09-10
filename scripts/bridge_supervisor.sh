#!/usr/bin/env bash
# ==============================================================================
# RunZero — Host VM Bridge process supervisor
#
# The Host VM Bridge (src/vm_bridge.py) is a native host process the
# containerized autoscaler depends on for every OrbStack/Multipass/WSL2 VM
# operation. Until now `make bridge-start` launched it with a bare
# `nohup ... &` and a PID file -- no supervision at all. Confirmed live
# (2026-09-09/10): it crashed silently mid-clone and stayed dead for 16+
# hours, orphaning 4 VMs with nothing to reap them (see
# src/drivers/orbstack_vm_driver.py's _vm_created_at_from_ulid() for the
# related cleanup-side fix). A dead bridge is a silent, total outage for
# every non-Docker job -- it needs to come back on its own.
#
# On macOS this installs the bridge as a launchd agent: KeepAlive restarts it
# within seconds of a crash, RunAtLoad brings it back after a reboot/logout,
# and ThrottleInterval stops a crash-loop from spinning the CPU. Everywhere
# else (or if launchctl is missing) this falls back to the previous
# nohup+PID-file behavior, which has no crash recovery but at least works.
#
# launchd itself can also silently refuse to work: on macOS, any repo that
# lives under a TCC-protected folder (~/Documents, ~/Desktop, ~/Downloads)
# cannot be touched by a launchd-spawned process at all, unless the exact
# interpreter binary has been granted Full Disk Access by hand in System
# Settings -- there is no way to grant this from a script. Confirmed live:
# `launchctl bootstrap`ing this exact plist made every run of vm_bridge.py
# exit instantly with zero output (launchd reported "78: EX_CONFIG"), and a
# minimal repro (a launchd job just `cat`ing a file in this repo) failed
# with "Operation not permitted" -- the same command run from an interactive
# terminal works fine, because Terminal.app/the IDE already has that grant
# and launchd's own spawn context does not inherit it. So `launchd_start`
# always verifies the bridge actually became healthy before declaring
# success, and falls back to the plain nohup mode (with a one-time
# actionable message) if it didn't -- a silently-broken "supervised" bridge
# that never serves a request is worse than the old unsupervised one.
# ==============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.runzero.vmbridge"
PLIST_PATH="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_FILE="$REPO_DIR/.bridge.log"
PID_FILE="$REPO_DIR/.bridge.pid"
MODE_FILE="$REPO_DIR/.bridge.mode"
DOMAIN="gui/$(id -u)"
SERVICE="$DOMAIN/$LABEL"

CYAN="\033[36m"; GREEN="\033[32m"; YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"

use_launchd() {
    [ "$(uname -s)" = "Darwin" ] && command -v launchctl >/dev/null 2>&1
}

# Which backend is actually serving right now, per the marker `start` wrote
# -- NOT just "is launchd available in principle". Needed because
# launchd_start can silently fall back to nohup (see the TCC note above);
# without this, `bridge-status`/`bridge-stop` would keep asking launchd
# about a job that was deliberately torn down, and report "not running"
# even while the nohup fallback is healthy and serving requests.
active_mode() {
    if [ -f "$MODE_FILE" ]; then
        cat "$MODE_FILE"
    else
        echo "none"
    fi
}

bridge_port() {
    if [ -f "$REPO_DIR/.env" ]; then
        awk -F= '/^HOST_VM_BRIDGE_PORT=/{print $2; exit}' "$REPO_DIR/.env" | tr -d ' "'"'"''
    fi
}

wait_for_health() {
    local port="${1:-49504}" timeout="${2:-8}"
    local deadline=$((SECONDS + timeout))
    while [ "$SECONDS" -lt "$deadline" ]; do
        if curl -fsS -m 1 "http://127.0.0.1:$port/health" >/dev/null 2>&1; then
            return 0
        fi
        sleep 0.5
    done
    return 1
}

pick_python() {
    if [ -x "$REPO_DIR/.venv/bin/python3" ]; then
        echo "$REPO_DIR/.venv/bin/python3"
    else
        command -v python3
    fi
}

# Renders the launchd plist to stdout, merging in the handful of .env
# settings the bridge's own drivers actually read via os.getenv (see
# MULTIPASS_IMAGE/DOCKER_SOCK/DOCKER_NETWORK/etc. below) alongside a sane
# fallback PATH + PYTHONPATH=src. Deliberately an *allowlist*, not a raw copy
# of .env: .env also carries ACCESS_TOKEN (a GitHub PAT) and other secrets
# that only the containerized autoscaler needs -- the bridge never touches
# GitHub's API at all (grep confirms no os.getenv("ACCESS_TOKEN") etc.
# anywhere under src/drivers or vm_bridge.py). Copying it wholesale would
# write that PAT in plaintext into a plist file under ~/Library/LaunchAgents,
# which (unlike a plain process's environment) sits on disk indefinitely --
# a real, avoidable credential-exposure regression versus the plain-process
# env the old nohup approach used.
#
# Builds the XML by hand with xml.sax.saxutils.escape rather than the stdlib
# `plistlib` module: plistlib unconditionally imports xml.parsers.expat at
# import time even for writing, and on this machine's Homebrew python@3.14
# that import is broken (a stale libexpat left behind by a brew upgrade --
# confirmed via `python3 -c "import plistlib"` raising ImportError: Symbol
# not found: _XML_SetAllocTrackerActivationThreshold). saxutils.escape has no
# such dependency, so this keeps working regardless of that unrelated
# breakage.
render_plist() {
    local python_bin="$1"
    PYTHON_BIN="$python_bin" REPO_DIR="$REPO_DIR" LABEL="$LABEL" LOG_FILE="$LOG_FILE" \
    "$python_bin" - "$REPO_DIR/.env" <<'PYEOF'
import os
import sys
from xml.sax.saxutils import escape

# Every env var any bridge-reachable driver (drivers/*.py) or vm_bridge.py
# itself reads via os.getenv -- keep in sync if either grows a new one.
ALLOWED_ENV_KEYS = {
    "MULTIPASS_IMAGE",
    "DOCKER_SOCK",
    "DOCKER_NETWORK",
    "RUNNER_IMAGE_DOCKER_DIR",
    "WSL_DISTRO_BASE",
    "RUNZERO_DEBUG",
    "HOST_VM_BRIDGE_HOST",
    "HOST_VM_BRIDGE_PORT",
}

env_file = sys.argv[1]
env = {
    "PYTHONPATH": "src",
    "PATH": "/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
}
if os.path.isfile(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in ALLOWED_ENV_KEYS:
                env[key] = value

def s(v):
    return f"<string>{escape(str(v))}</string>"

env_xml = "\n".join(f"    <key>{escape(k)}</key>\n    {s(v)}" for k, v in env.items())
args_xml = "\n".join(f"    {s(a)}" for a in (os.environ["PYTHON_BIN"], "-u", "src/vm_bridge.py"))

print(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  {s(os.environ["LABEL"])}
  <key>ProgramArguments</key>
  <array>
{args_xml}
  </array>
  <key>WorkingDirectory</key>
  {s(os.environ["REPO_DIR"])}
  <key>EnvironmentVariables</key>
  <dict>
{env_xml}
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ThrottleInterval</key>
  <integer>5</integer>
  <key>ProcessType</key>
  <string>Background</string>
  <key>StandardOutPath</key>
  {s(os.environ["LOG_FILE"])}
  <key>StandardErrorPath</key>
  {s(os.environ["LOG_FILE"])}
</dict>
</plist>
""")
PYEOF
}

nohup_start() {
    local reason="${1:-launchd unavailable}"
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo -e "${YELLOW}Host VM Bridge already running (PID $(cat "$PID_FILE")).${RESET}"
        echo "nohup" > "$MODE_FILE"
        return
    fi
    echo -e "${YELLOW}$reason -- starting Host VM Bridge without crash supervision.${RESET}"
    set -a; [ -f "$REPO_DIR/.env" ] && . "$REPO_DIR/.env"; set +a
    # Must background a plain simple command, not a `cd ... && nohup ...`
    # compound: backgrounding a `&&`-list forces bash to fork a wrapper
    # subshell to run it, and `$!` then captures THAT wrapper's PID -- which
    # exits the moment it has spawned nohup's child, not the actual
    # long-running server's PID. Confirmed live: the recorded PID_FILE
    # entry died within a second while the real python process (PID+1) kept
    # serving fine, making bridge-stop/-status silently useless (killing/
    # checking a PID that was already gone, while the real server ran on
    # untouched). `cd` as its own statement first, then background only the
    # simple `nohup python3 ...` command, keeps `$!` accurate.
    (
        cd "$REPO_DIR"
        PYTHONPATH=src nohup python3 -u src/vm_bridge.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
    )
    echo "nohup" > "$MODE_FILE"
    echo -e "${GREEN}Host VM Bridge running in background (PID $(cat "$PID_FILE")).${RESET}"
}

nohup_stop() {
    if [ -f "$PID_FILE" ]; then
        pid="$(cat "$PID_FILE")"
        if kill -0 "$pid" 2>/dev/null; then kill "$pid"; fi
        rm -f "$PID_FILE"
    fi
    rm -f "$MODE_FILE"
}

nohup_status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Running (PID $(cat "$PID_FILE"), no crash supervision)"
    else
        echo "Not running"
    fi
}

launchd_start() {
    mkdir -p "$(dirname "$PLIST_PATH")"
    local python_bin; python_bin="$(pick_python)"

    # Clear out any previous nohup-mode process first -- it would otherwise
    # either hold the port launchd's instance needs, or leave bridge-status
    # confused about which process is authoritative.
    if [ -f "$PID_FILE" ]; then
        pid="$(cat "$PID_FILE")"
        if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; sleep 0.3; fi
        rm -f "$PID_FILE"
    fi

    render_plist "$python_bin" > "$PLIST_PATH"
    chmod 600 "$PLIST_PATH"
    # Idempotent: bootout-then-bootstrap picks up plist edits (e.g. a changed
    # .env or interpreter path) instead of leaving a stale job registered.
    launchctl bootout "$SERVICE" >/dev/null 2>&1 || true
    launchctl bootstrap "$DOMAIN" "$PLIST_PATH"
    launchctl enable "$SERVICE" >/dev/null 2>&1 || true

    local port; port="$(bridge_port)"; port="${port:-49504}"
    if wait_for_health "$port" 8; then
        echo "launchd" > "$MODE_FILE"
        echo -e "${GREEN}Host VM Bridge installed as a launchd agent (auto-restarts on crash, survives reboot/logout).${RESET}"
        echo -e "${CYAN}  Label: $LABEL   Plist: $PLIST_PATH${RESET}"
        return
    fi

    # It never came up. launchctl print's "last exit code" tells us why --
    # in particular, code 78 (EX_CONFIG) is what launchd reports when it
    # can't even spawn the process, which on this machine means the TCC
    # ~/Documents restriction documented at the top of this file.
    local exit_info
    exit_info="$(launchctl print "$SERVICE" 2>/dev/null | awk -F'= ' '/last exit code/{print $2; exit}')"
    launchctl bootout "$SERVICE" >/dev/null 2>&1 || true
    rm -f "$PLIST_PATH"

    echo -e "${RED}Host VM Bridge did not come up under launchd (last exit: ${exit_info:-unknown}).${RESET}"
    case "$exit_info" in
        *78*)
            echo -e "${YELLOW}This looks like macOS blocking launchd from reading files under:"
            echo -e "  $REPO_DIR"
            echo -e "because it's inside a TCC-protected folder (Documents/Desktop/Downloads)."
            echo -e "To get real crash supervision, grant Full Disk Access to this exact interpreter:"
            echo -e "  $python_bin"
            echo -e "(System Settings > Privacy & Security > Full Disk Access, then \`make bridge-start\` again)."
            echo -e "Falling back to a plain background process for now -- it works, it just won't"
            echo -e "auto-restart if it crashes.${RESET}"
            ;;
        *)
            echo -e "${YELLOW}See $LOG_FILE and \`launchctl print $SERVICE\` for details."
            echo -e "Falling back to a plain background process for now.${RESET}"
            ;;
    esac
    nohup_start "launchd install failed"
}

launchd_stop() {
    launchctl bootout "$SERVICE" >/dev/null 2>&1 || true
    rm -f "$MODE_FILE"
}

launchd_status() {
    if launchctl print "$SERVICE" >/tmp/.runzero-bridge-status.$$ 2>/dev/null; then
        pid=$(awk -F'= ' '/pid =/{print $2; exit}' /tmp/.runzero-bridge-status.$$)
        state=$(awk -F'= ' '/state =/{print $2; exit}' /tmp/.runzero-bridge-status.$$)
        rm -f /tmp/.runzero-bridge-status.$$
        echo "Running under launchd (state: ${state:-unknown}, PID: ${pid:-n/a}) -- auto-restarts on crash"
    else
        rm -f /tmp/.runzero-bridge-status.$$
        echo "Not running (no launchd job registered)"
    fi
}

case "${1:-status}" in
    start)
        if use_launchd; then launchd_start; else nohup_start "launchd unavailable"; fi
        ;;
    stop)
        case "$(active_mode)" in
            launchd) launchd_stop ;;
            *) nohup_stop ;;
        esac
        ;;
    status)
        case "$(active_mode)" in
            launchd) launchd_status ;;
            nohup) nohup_status ;;
            *) echo "Not running" ;;
        esac
        ;;
    *)
        echo "Usage: $0 {start|stop|status}" >&2
        exit 1
        ;;
esac
