#!/usr/bin/env bash
# ==============================================================================
# RunZero — Host VM Bridge process supervisor
#
# The Host VM Bridge (`bin/runzero bridge`) is a native host process the
# containerized autoscaler depends on for every OrbStack/Multipass/WSL2 VM
# operation.
#
# On macOS this installs the bridge as a launchd agent: KeepAlive restarts it
# within seconds of a crash, RunAtLoad brings it back after a reboot/logout,
# and ThrottleInterval stops a crash-loop from spinning the CPU. Everywhere
# else (or if launchctl is missing) this falls back to nohup+PID-file behavior.
#
# To avoid macOS TCC restrictions on ~/Documents, the launchd job runs from
# $RUNZERO_BRIDGE_HOME (default ~/Library/Application Support/RunZero/bridge)
# where `runzero` binary is staged on every start. Every `make restart` or
# `make bridge-start` re-stages the latest compiled Go binary.
# ==============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.runzero.vmbridge"
PLIST_PATH="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_FILE="$REPO_DIR/.bridge.log"
PID_FILE="$REPO_DIR/.bridge.pid"
MODE_FILE="$REPO_DIR/.bridge.mode"
BRIDGE_HOME="${RUNZERO_BRIDGE_HOME:-$HOME/Library/Application Support/RunZero/bridge}"
LAUNCHD_LOG_FILE="$BRIDGE_HOME/bridge.log"
DOMAIN="gui/$(id -u)"
SERVICE="$DOMAIN/$LABEL"

CYAN="\033[36m"; GREEN="\033[32m"; YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"

use_launchd() {
    [ -z "${RUNZERO_BRIDGE_NO_LAUNCHD:-}" ] && [ "$(uname -s)" = "Darwin" ] && command -v launchctl >/dev/null 2>&1
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

# "<pid> <command>" of whatever listens on TCP port $1; empty when free or lsof is missing.
port_holder() {
    command -v lsof >/dev/null 2>&1 || return 0
    local pid
    pid="$(lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -1)"
    if [ -n "$pid" ]; then echo "$pid $(ps -o command= -p "$pid" 2>/dev/null)"; fi
    return 0
}

# Waits up to $2 seconds for port $1 to be free (a just-stopped bridge takes a moment).
wait_port_free() {
    local deadline=$((SECONDS + $2))
    while [ -n "$(port_holder "$1")" ]; do
        [ "$SECONDS" -ge "$deadline" ] && return 1
        sleep 0.3
    done
    return 0
}

# Refuses to start while a process this script doesn't manage holds the port (#72). Otherwise
# launchd's bridge crash-loops on "address in use" (silently: exit 78) while the foreign one --
# e.g. a stale manual start running two-week-old code -- keeps answering /health.
refuse_foreign_holder() {
    local port="$1" holder pid
    wait_port_free "$port" 3 && return 0
    holder="$(port_holder "$port")"
    [ -z "$holder" ] && return 0
    pid="${holder%% *}"
    echo -e "${RED}Port $port is already in use by PID $pid:${RESET}"
    echo "  ${holder#* }"
    echo -e "${YELLOW}This script did not start that process (a stale manual bridge or another service)."
    echo -e "Stop it with \`kill $pid\` once you've checked it's safe, or set HOST_VM_BRIDGE_PORT in .env,"
    echo -e "then run \`make bridge-start\` again.${RESET}"
    exit 1
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

# Copies the runzero binary to $BRIDGE_HOME, replacing the previous copy.
stage_bridge() {
    mkdir -p "$BRIDGE_HOME"
    if [ ! -f "$REPO_DIR/bin/runzero" ]; then
        (cd "$REPO_DIR" && go build -o bin/runzero ./cmd/runzero)
    fi
    cp "$REPO_DIR/bin/runzero" "$BRIDGE_HOME/runzero"
    chmod +x "$BRIDGE_HOME/runzero"
}

render_plist() {
    local env_file="$REPO_DIR/.env"
    local port; port="$(bridge_port)"; port="${port:-49504}"
    local token=""
    if [ -f "$env_file" ]; then
        token="$(awk -F= '/^RUNZERO_BRIDGE_TOKEN=/{print $2; exit}' "$env_file" | tr -d ' "'"'"'')"
    fi
    cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${BRIDGE_HOME}/runzero</string>
    <string>bridge</string>
    <string>-port</string>
    <string>${port}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${BRIDGE_HOME}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>HOST_VM_BRIDGE_PORT</key>
    <string>${port}</string>
    <key>RUNZERO_BRIDGE_TOKEN</key>
    <string>${token}</string>
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
  <string>${LAUNCHD_LOG_FILE}</string>
  <key>StandardErrorPath</key>
  <string>${LAUNCHD_LOG_FILE}</string>
</dict>
</plist>
PLIST
}

nohup_start() {
    local reason="${1:-launchd unavailable}"
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo -e "${YELLOW}Host VM Bridge already running (PID $(cat "$PID_FILE")).${RESET}"
        echo "nohup" > "$MODE_FILE"
        return
    fi
    local port; port="$(bridge_port)"; refuse_foreign_holder "${port:-49504}"
    echo -e "${YELLOW}$reason -- starting Host VM Bridge without crash supervision.${RESET}"
    if [ ! -f "$REPO_DIR/bin/runzero" ]; then
        (cd "$REPO_DIR" && go build -o bin/runzero ./cmd/runzero)
    fi
    (
        cd "$REPO_DIR"
        nohup ./bin/runzero bridge > "$LOG_FILE" 2>&1 &
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

    if [ -f "$PID_FILE" ]; then
        pid="$(cat "$PID_FILE")"
        if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; sleep 0.3; fi
        rm -f "$PID_FILE"
    fi

    stage_bridge
    (umask 077 && render_plist > "$PLIST_PATH")
    chmod 600 "$PLIST_PATH"
    launchctl bootout "$SERVICE" >/dev/null 2>&1 || true
    local port; port="$(bridge_port)"; port="${port:-49504}"
    refuse_foreign_holder "$port"
    : >> "$LAUNCHD_LOG_FILE"
    ln -sfn "$LAUNCHD_LOG_FILE" "$LOG_FILE"
    launchctl bootstrap "$DOMAIN" "$PLIST_PATH"
    launchctl enable "$SERVICE" >/dev/null 2>&1 || true

    if wait_for_health "$port" 8; then
        echo "launchd" > "$MODE_FILE"
        echo -e "${GREEN}Host VM Bridge installed as a launchd agent (auto-restarts on crash, survives reboot/logout).${RESET}"
        echo -e "${CYAN}  Label: $LABEL   Plist: $PLIST_PATH${RESET}"
        echo -e "${CYAN}  Runs Host VM Bridge binary from $BRIDGE_HOME (re-staged on every start).${RESET}"
        return
    fi

    local exit_info
    exit_info="$(launchctl print "$SERVICE" 2>/dev/null | awk -F'= ' '/last exit code/{print $2; exit}')"
    launchctl bootout "$SERVICE" >/dev/null 2>&1 || true
    rm -f "$PLIST_PATH"

    echo -e "${RED}Host VM Bridge did not come up under launchd (last exit: ${exit_info:-unknown}).${RESET}"
    case "$exit_info" in
        *78*)
            echo -e "${YELLOW}This looks like macOS blocking launchd from reading the staged bridge binary:"
            echo -e "  $BRIDGE_HOME/runzero"
            echo -e "Keep it out of TCC-protected folders (Documents/Desktop/Downloads; see RUNZERO_BRIDGE_HOME),"
            echo -e "or grant the binary Full Disk Access.${RESET}"
            ;;
        *)
            echo -e "${YELLOW}See $LAUNCHD_LOG_FILE and \`launchctl print $SERVICE\` for details."
            echo -e "Falling back to a plain background process for now.${RESET}"
            ;;
    esac
    rm -f "$LOG_FILE"
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
    stage)
        stage_bridge
        echo "Staged runzero binary into $BRIDGE_HOME"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|stage}" >&2
        exit 1
        ;;
esac
