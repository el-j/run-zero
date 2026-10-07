import "./styles/theme.css";
import {
  client,
  type CompletedJob,
  type FleetState,
  type QueuedJob,
  type RunnerInfo,
  type CacheStats,
  type SystemSettings,
} from "./api/client";

// Global DOM elements
const connectionBadge = document.getElementById("connection-status-badge")!;
const connectionText = document.getElementById("connection-status-text")!;
const statRateLimit = document.getElementById("stat-rate-limit")!;
const statRateLimitBar = document.getElementById("stat-rate-limit-bar")!;
const statRateMeta = document.getElementById("stat-rate-meta")!;
const statUptime = document.getElementById("stat-uptime")!;
const statEngine = document.getElementById("stat-default-engine")!;
const statVersion = document.getElementById("stat-version")!;

const kpiActiveRunners = document.getElementById("kpi-active-runners")!;
const kpiMaxRunners = document.getElementById("kpi-max-runners")!;
const kpiRunnersBar = document.getElementById("kpi-runners-bar")!;
const kpiMinRunnersText = document.getElementById("kpi-min-runners-text")!;
const kpiRunnerSizing = document.getElementById("kpi-runner-sizing")!;
const kpiQueuedJobs = document.getElementById("kpi-queued-jobs")!;
const kpiQueueBar = document.getElementById("kpi-queue-bar")!;
const kpiReposMonitored = document.getElementById("kpi-repos-monitored")!;
const kpiVmRatio = document.getElementById("kpi-vm-ratio")!;
const kpiRoutingBar = document.getElementById("kpi-routing-bar")!;
const kpiRoutingSub = document.getElementById("kpi-routing-sub")!;
const kpiCacheSize = document.getElementById("kpi-cache-size")!;
const kpiCacheBar = document.getElementById("kpi-cache-bar")!;

// Unified Fleet Control Tabs
const tabBtnRunners = document.getElementById("tab-btn-runners");
const tabBtnQueue = document.getElementById("tab-btn-queue");
const tabBtnJobs = document.getElementById("tab-btn-jobs");
const tabBtnRepos = document.getElementById("tab-btn-repos");
const tabRunnersCount = document.getElementById("tab-runners-count");
const tabQueueCount = document.getElementById("tab-queue-count");
const tabJobsCount = document.getElementById("tab-jobs-count");
const tabReposCount = document.getElementById("tab-repos-count");
const tabContentRunners = document.getElementById("tab-content-runners");
const tabContentQueue = document.getElementById("tab-content-queue");
const tabContentJobs = document.getElementById("tab-content-jobs");
const tabContentRepos = document.getElementById("tab-content-repos");
const tabActionsRunners = document.getElementById("tab-actions-runners");
const tabActionsQueue = document.getElementById("tab-actions-queue");
const tabActionsJobs = document.getElementById("tab-actions-jobs");
const tabActionsRepos = document.getElementById("tab-actions-repos");

// View Mode Toggle
const viewModeCards = document.getElementById("view-mode-cards");
const viewModeTable = document.getElementById("view-mode-table");
const selectViewModeSetting = document.getElementById("select-view-mode-setting") as HTMLSelectElement | null;
const runnersCardsView = document.getElementById("runners-cards-view");
const runnersTableView = document.getElementById("runners-table-view");
const runnersTableBody = document.getElementById("runners-table-body");
const runnersTableEmpty = document.getElementById("runners-table-empty");

const queueCardsView = document.getElementById("queue-cards-view");
const queueTableView = document.getElementById("queue-table-view");
const queueTableBody = document.getElementById("queue-table-body");
const queueTableEmpty = document.getElementById("queue-table-empty");

const reposCardsView = document.getElementById("repos-cards-view");
const reposTableView = document.getElementById("repos-table-view");
const reposTableBody = document.getElementById("repos-table-body");

const runnersGrid = document.getElementById("runners-grid");
const runnersEmptyState = document.getElementById("runners-empty-state");
const runnersCountBadge = document.getElementById("runners-count-badge");
const btnStartRunner = document.getElementById("btn-start-runner");
const btnPruneRunners = document.getElementById("btn-prune-runners");

const queueSlotsBadge = document.getElementById("queue-slots-badge");
const queueBusySlots = document.getElementById("queue-busy-slots");
const queueMaxSlots = document.getElementById("queue-max-slots");
const queueFreeSlots = document.getElementById("queue-free-slots");
const queueTotalJobs = document.getElementById("queue-total-jobs");
const reposCountBadge = document.getElementById("repos-count-badge");
const repoSearchInput = document.getElementById("repo-search-input") as HTMLInputElement | null;
const reposList = document.getElementById("repos-list");
const queueJobsCountTag = document.getElementById("queue-jobs-count-tag");
const queueJobsView = document.getElementById("queue-jobs-view");
const jobsList = document.getElementById("jobs-list");

// Full-Size Bottom Terminal elements
const logTerminal = document.getElementById("log-terminal");
const autoScrollToggle = document.getElementById("auto-scroll-toggle") as HTMLInputElement | null;
const btnClearLogs = document.getElementById("btn-clear-logs");
const btnToggleTerminalExpand = document.getElementById("btn-toggle-terminal-expand");
const btnTerminalExpandIcon = document.getElementById("btn-terminal-expand-icon");
const btnTerminalExpandText = document.getElementById("btn-terminal-expand-text");
const terminalBodyWrapper = document.getElementById("terminal-body-wrapper");
const terminalLineCount = document.getElementById("terminal-line-count");

const barDockerJobs = document.getElementById("bar-docker-jobs");
const barVmJobs = document.getElementById("bar-vm-jobs");
const cntDockerJobs = document.getElementById("cnt-docker-jobs");
const cntVmJobs = document.getElementById("cnt-vm-jobs");

const actionsScope = document.getElementById("actions-scope");
const actionsIncluded = document.getElementById("actions-included");
const actionsTotalUsed = document.getElementById("actions-total-used");
const actionsPaidUsed = document.getElementById("actions-paid-used");
const actionsRemaining = document.getElementById("actions-remaining");
const actionsUpdated = document.getElementById("actions-updated");
const actionsStatus = document.getElementById("actions-status");

const btnPurgeAllCaches = document.getElementById("btn-purge-all-caches");

// Modal elements
const spawnModal = document.getElementById("spawn-modal") as HTMLDialogElement | null;
const spawnModalClose = document.getElementById("spawn-modal-close");
const spawnModalCancel = document.getElementById("spawn-modal-cancel");
const spawnModalSubmit = document.getElementById("spawn-modal-submit");
const manualRepoInput = document.getElementById("manual-repo-input") as HTMLInputElement | null;
const manualArchSelect = document.getElementById("manual-arch-select") as HTMLSelectElement | null;

// Settings elements
const btnOpenSettings = document.getElementById("btn-open-settings");
const btnOpenSettingsPanel = document.getElementById("btn-open-settings-panel");
const settingsModal = document.getElementById("settings-modal") as HTMLDialogElement | null;
const settingsModalClose = document.getElementById("settings-modal-close");
const settingsModalCancel = document.getElementById("settings-modal-cancel");
const settingsModalSave = document.getElementById("settings-modal-save");
const settingsForm = document.getElementById("settings-form") as HTMLFormElement | null;

const cfgMaxRunners = document.getElementById("cfg-max-runners");
const cfgMinRunners = document.getElementById("cfg-min-runners");
const cfgRunnerBackend = document.getElementById("cfg-runner-backend");
const cfgAutoRouteVm = document.getElementById("cfg-auto-route-vm");
const cfgCacheEnabled = document.getElementById("cfg-cache-enabled");

const inputMaxRunners = document.getElementById("input-max-runners") as HTMLInputElement | null;
const inputMinRunners = document.getElementById("input-min-runners") as HTMLInputElement | null;
const inputRunnerCpus = document.getElementById("input-runner-cpus") as HTMLInputElement | null;
const inputRunnerMemory = document.getElementById("input-runner-memory") as HTMLInputElement | null;
const selectRunnerBackend = document.getElementById("select-runner-backend") as HTMLSelectElement | null;
const selectRunnerArch = document.getElementById("select-runner-arch") as HTMLSelectElement | null;
const checkboxAutoRouteVm = document.getElementById("checkbox-auto-route-vm") as HTMLInputElement | null;
const selectNativeOverride = document.getElementById("select-native-override") as HTMLSelectElement | null;
const inputPollInterval = document.getElementById("input-poll-interval") as HTMLInputElement | null;
const inputDiscoveryInterval = document.getElementById("input-discovery-interval") as HTMLInputElement | null;
const checkboxCacheEnabled = document.getElementById("checkbox-cache-enabled") as HTMLInputElement | null;
const checkboxProxiesEnabled = document.getElementById("checkbox-proxies-enabled") as HTMLInputElement | null;
const inputCacheDir = document.getElementById("input-cache-dir") as HTMLInputElement | null;

// Application state
let currentRepos: string[] = [];
let currentQueuedJobs: QueuedJob[] = [];
let currentRepoPriority: string[] = [];
let currentPausedRepos = new Set<string>();
let currentConcurrency = { active: 0, max: 3, min: 0 };
let draggedRepo: string | null = null;
let lastUptimeSeconds = 0;
let currentViewMode: "cards" | "table" = (localStorage.getItem("runzero_display_mode") as "cards" | "table") || "cards";
let currentTab: "runners" | "queue" | "jobs" | "repos" = "runners";
let terminalExpanded = false;
let totalLogLines = 0;

function formatReset(resetEpoch?: number | null): string {
  if (!resetEpoch) return "--:--:--";
  const remainingSec = Math.max(0, Math.floor(resetEpoch - Date.now() / 1000));
  const h = Math.floor(remainingSec / 3600);
  const m = Math.floor((remainingSec % 3600) / 60);
  const s = remainingSec % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function formatDuration(isoTime?: string | null): string {
  if (!isoTime) return "active";
  const created = new Date(isoTime).getTime();
  if (isNaN(created)) return "active";
  const diffSec = Math.max(0, Math.floor((Date.now() - created) / 1000));
  const m = Math.floor(diffSec / 60);
  const s = diffSec % 60;
  if (m === 0) return `${s}s`;
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}h ${m % 60}m`;
  return `${m}m ${s}s`;
}

function escapeHtml(str: string): string {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function showToast(message: string, isError = false) {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = "toast";
  if (isError) {
    toast.style.borderColor = "var(--crimson)";
  }
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function setConnectionStatus(status: "connecting" | "online" | "error", text: string) {
  if (!connectionText || !connectionBadge) return;
  connectionText.textContent = text;
  connectionBadge.className = "badge badge-pulse";
  if (status === "connecting") {
    connectionBadge.classList.add("connecting");
  } else if (status === "error") {
    connectionBadge.classList.add("error");
  }
}

// View Mode Toggle (Card Grid vs Compact Styled Table)
function setViewMode(mode: "cards" | "table") {
  currentViewMode = mode;
  localStorage.setItem("runzero_display_mode", mode);

  if (viewModeCards && viewModeTable) {
    if (mode === "cards") {
      viewModeCards.classList.add("active");
      viewModeTable.classList.remove("active");
    } else {
      viewModeTable.classList.add("active");
      viewModeCards.classList.remove("active");
    }
  }

  if (selectViewModeSetting) {
    selectViewModeSetting.value = mode;
  }

  // Toggle views
  if (runnersCardsView && runnersTableView) {
    if (mode === "cards") {
      runnersCardsView.classList.remove("hidden");
      runnersTableView.classList.add("hidden");
    } else {
      runnersCardsView.classList.add("hidden");
      runnersTableView.classList.remove("hidden");
    }
  }

  if (queueCardsView && queueTableView) {
    if (mode === "cards") {
      queueCardsView.classList.remove("hidden");
      queueTableView.classList.add("hidden");
    } else {
      queueCardsView.classList.add("hidden");
      queueTableView.classList.remove("hidden");
    }
  }

  if (reposCardsView && reposTableView) {
    if (mode === "cards") {
      reposCardsView.classList.remove("hidden");
      reposTableView.classList.add("hidden");
    } else {
      reposCardsView.classList.add("hidden");
      reposTableView.classList.remove("hidden");
    }
  }
}

// Master Tabs Switching
function setActiveTab(tab: "runners" | "queue" | "jobs" | "repos") {
  currentTab = tab;

  const tabs = [
    { name: "runners", btn: tabBtnRunners, pane: tabContentRunners, actions: tabActionsRunners },
    { name: "queue", btn: tabBtnQueue, pane: tabContentQueue, actions: tabActionsQueue },
    { name: "jobs", btn: tabBtnJobs, pane: tabContentJobs, actions: tabActionsJobs },
    { name: "repos", btn: tabBtnRepos, pane: tabContentRepos, actions: tabActionsRepos },
  ];

  tabs.forEach((t) => {
    if (t.name === tab) {
      t.btn?.classList.add("active");
      t.pane?.classList.remove("hidden");
      t.actions?.classList.remove("hidden");
    } else {
      t.btn?.classList.remove("active");
      t.pane?.classList.add("hidden");
      t.actions?.classList.add("hidden");
    }
  });
}

// Terminal Panel Expand/Collapse
function toggleTerminal() {
  terminalExpanded = !terminalExpanded;
  if (terminalBodyWrapper) {
    if (terminalExpanded) {
      terminalBodyWrapper.classList.remove("default");
      terminalBodyWrapper.classList.add("expanded");
      if (btnTerminalExpandIcon) btnTerminalExpandIcon.textContent = "▼";
      if (btnTerminalExpandText) btnTerminalExpandText.textContent = "COLLAPSE";
    } else {
      terminalBodyWrapper.classList.remove("expanded");
      terminalBodyWrapper.classList.add("default");
      if (btnTerminalExpandIcon) btnTerminalExpandIcon.textContent = "▲";
      if (btnTerminalExpandText) btnTerminalExpandText.textContent = "EXPAND";
    }
  }
}

// Format log entry with high-tech badge styling
function formatLogMessage(msg: string): string {
  let safe = escapeHtml(msg);
  safe = safe.replace(/\[(Autoscaler|Reconciler|DockerDriver|OrbStackDriver|WSL2Driver|MultipassDriver|Go Engine)\]/g,
    '<span class="log-tag tag-cyan">[$1]</span>');
  safe = safe.replace(/\[(Spawn|ScaleUp|Ready|Started)\]/gi,
    '<span class="log-tag tag-emerald">[$1]</span>');
  safe = safe.replace(/\[(ScaleDown|Prune|Terminated|Stopped)\]/gi,
    '<span class="log-tag tag-amber">[$1]</span>');
  safe = safe.replace(/\[(Error|Failed|Exception|Timeout|❌)\]/gi,
    '<span class="log-tag tag-crimson">[$1]</span>');
  safe = safe.replace(/\[(Bridge|VM|Routing|🚀)\]/gi,
    '<span class="log-tag tag-purple">[$1]</span>');
  return safe;
}

function appendLog(text: string, timestamp?: string) {
  if (!logTerminal) return;
  totalLogLines++;
  if (terminalLineCount) terminalLineCount.textContent = `${totalLogLines} lines`;
  const ts = timestamp || new Date().toLocaleTimeString();
  const lineEl = document.createElement("div");
  lineEl.className = "log-line";
  lineEl.innerHTML = `<span class="log-ts font-mono">[${escapeHtml(ts)}]</span> <span class="log-content">${formatLogMessage(text)}</span>`;
  logTerminal.appendChild(lineEl);
  if (logTerminal.children.length > 500) {
    logTerminal.removeChild(logTerminal.firstChild!);
  }
  if (autoScrollToggle && autoScrollToggle.checked) {
    logTerminal.scrollTop = logTerminal.scrollHeight;
  }
}

// Render Runners Fleet (Dual Card and Table View with GitHub Run Links & Stage Progress)
// Workflow run = whole workflow execution. Job = one job of that run. Steps = stages of the job.
type RunRef = {
  repo?: string;
  target_repo?: string;
  run_id?: number;
  job_id?: number;
  run_url?: string;
  job_url?: string;
  job_name?: string;
  current_step?: string;
  progress_pct?: number;
  stages_done?: number;
  stages_total?: number;
  steps_completed?: number;
  steps_total?: number;
  steps?: { number: number; name: string; status: string }[];
};

function runUrlOf(x: RunRef): string {
  const repo = x.target_repo || x.repo;
  return x.run_url || (x.run_id && repo ? `https://github.com/${repo}/actions/runs/${x.run_id}` : "");
}

function jobUrlOf(x: RunRef): string {
  const repo = x.target_repo || x.repo;
  if (x.job_url) return x.job_url;
  return x.run_id && x.job_id && repo ? `https://github.com/${repo}/actions/runs/${x.run_id}/job/${x.job_id}` : "";
}

function runLinkHtml(x: RunRef): string {
  const url = runUrlOf(x);
  return url
    ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="gh-link run-link" title="Open workflow run">Run #${x.run_id ?? ""} ↗</a>`
    : "";
}

function jobLinkHtml(x: RunRef): string {
  const url = jobUrlOf(x);
  if (!url) return "";
  const label = x.job_name ? escapeHtml(x.job_name) : `Job #${x.job_id ?? ""}`;
  return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="gh-link job-link" title="Open job">${label} ↗</a>`;
}

function stepIcon(status: string): string {
  if (status === "completed") return "✓";
  if (status === "in_progress") return "▶";
  return "○";
}

// Progress for a job: step-based bar, current stage and (cards only) the full step pipeline.
function progressHtml(x: RunRef, compact: boolean): string {
  const steps = x.steps || [];
  const hasData = x.progress_pct !== undefined || steps.length > 0 || !!x.current_step;
  if (!hasData) return "";
  const pct = x.progress_pct ?? 0;
  const done = x.steps_completed ?? steps.filter((s) => s.status === "completed").length;
  const total = x.steps_total ?? steps.length;
  const stepLabel = total > 0 ? `step ${Math.min(done + 1, total)}/${total}` : `${x.stages_done ?? 0}/${x.stages_total ?? 1} jobs`;
  const current = x.current_step ? `<div class="current-stage" title="Current stage">▶ ${escapeHtml(x.current_step)}</div>` : "";
  const pipeline =
    !compact && steps.length > 0
      ? `<div class="step-pipeline">${steps
          .map((s) => `<span class="step-chip ${escapeHtml(s.status)}" title="${escapeHtml(s.name)}">${stepIcon(s.status)} ${escapeHtml(s.name)}</span>`)
          .join("")}</div>`
      : "";
  return `
    <div class="mini-progress-wrap" style="margin-top: ${compact ? 0 : 6}px;">
      <div class="mini-progress-text">
        <span>${stepLabel}</span>
        <span style="color: var(--emerald); font-weight: 700;">${pct}%</span>
      </div>
      <div class="mini-progress-track"><div class="mini-progress-fill" style="width: ${pct}%;"></div></div>
      ${current}
      ${pipeline}
    </div>`;
}

function renderRunners(runners: RunnerInfo[]) {
  if (tabRunnersCount) tabRunnersCount.textContent = String(runners.length);
  if (runnersCountBadge) runnersCountBadge.textContent = `${runners.length} RUNNING`;

  const hasRunners = runners.length > 0;

  if (runnersEmptyState) {
    if (hasRunners) runnersEmptyState.classList.add("hidden");
    else runnersEmptyState.classList.remove("hidden");
  }
  if (runnersGrid) {
    if (hasRunners) runnersGrid.classList.remove("hidden");
    else runnersGrid.classList.add("hidden");
  }
  if (runnersTableEmpty) {
    if (hasRunners) runnersTableEmpty.classList.add("hidden");
    else runnersTableEmpty.classList.remove("hidden");
  }

  // 1. Render Cards View
  if (runnersGrid) {
    runnersGrid.innerHTML = runners
      .map((r) => {
        const isVm = (r.backend || "").toLowerCase().includes("vm") || (r.backend || "").toLowerCase().includes("orb");
        const engineTagClass = isVm ? "tag-vm" : "tag-docker";
        const engineName = isVm ? (r.backend || "VM").toUpperCase() : "DOCKER";
        const archName = (r.target_arch || "amd64").toUpperCase();
        const repo = r.target_repo || "Standby Pool";
        const duration = formatDuration(r.created_at);

        const runLink = runLinkHtml(r);
        const jobLink = jobLinkHtml(r);
        const progressBlock = progressHtml(r, false);

        let targetMeta = `<span>${escapeHtml(repo)}</span>`;
        if (r.workflow_name) {
          targetMeta += `<div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">Workflow: ${escapeHtml(r.workflow_name)}</div>`;
        }
        if (runLink) {
          targetMeta += `<div style="font-size: 11px; margin-top: 3px;"><span class="link-label">RUN</span> ${runLink}</div>`;
        }
        if (jobLink) {
          targetMeta += `<div style="font-size: 11px; margin-top: 3px;"><span class="link-label">JOB</span> ${jobLink}</div>`;
        }

        return `
          <div class="runner-card">
            <div class="runner-card-top">
              <div class="runner-id-wrap">
                <span class="runner-pulse"></span>
                <span class="runner-id font-mono">${escapeHtml(r.name || r.id)}</span>
              </div>
              <div class="runner-badges">
                <span class="tag-engine ${engineTagClass}">${engineName}</span>
                <span class="tag-arch font-mono">${archName}</span>
              </div>
            </div>
            <div class="runner-repo">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              </svg>
              <div>${targetMeta}</div>
            </div>
            ${progressBlock}
            <div class="runner-card-bottom" style="margin-top: 10px;">
              <span class="stat-label">STATUS: <b class="runner-status-val" style="color: var(--emerald);">${escapeHtml((r.status || "RUNNING").toUpperCase())}</b></span>
              <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span class="runner-duration font-mono">⏱️ ${duration}</span>
                <button class="btn btn-xs btn-outline stop-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-job-id="${r.job_id || ""}">
                  Stop
                </button>
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  }

  // 2. Render Table View
  if (runnersTableBody) {
    runnersTableBody.innerHTML = runners
      .map((r) => {
        const isVm = (r.backend || "").toLowerCase().includes("vm") || (r.backend || "").toLowerCase().includes("orb");
        const engineName = isVm ? (r.backend || "VM").toUpperCase() : "DOCKER";
        const archName = (r.target_arch || "amd64").toUpperCase();
        const duration = formatDuration(r.created_at);

        const runLink = runLinkHtml(r);
        const jobLink = jobLinkHtml(r);
        const progressBlock = progressHtml(r, true);
        const idle = !runLink && !jobLink;

        return `
          <tr>
            <td>
              <div style="font-weight: 700; color: var(--text-main);">${escapeHtml(r.name || r.id)}</div>
              <div style="font-size: 10px; color: var(--text-dim);">${escapeHtml(r.id)}</div>
            </td>
            <td>
              <span style="font-weight: 600;">${escapeHtml(r.target_repo || "Standby")}</span>
            </td>
            <td>
              <span class="tech-chip ${isVm ? "purple" : "cyan"} font-mono" style="font-size: 10px;">${engineName}</span>
              <span class="tech-chip solar font-mono" style="font-size: 10px;">${archName}</span>
            </td>
            <td>
              <span class="badge font-mono" style="color: var(--emerald);">${escapeHtml((r.status || "RUNNING").toUpperCase())}</span>
            </td>
            <td>
              ${idle ? `<span style="color: var(--text-dim);">Standby / Idle</span>` : `
                <div><span class="link-label">RUN</span> ${runLink}${r.workflow_name ? ` <span style="color: var(--text-muted);">${escapeHtml(r.workflow_name)}</span>` : ""}</div>
                <div><span class="link-label">JOB</span> ${jobLink || "-"}</div>`}
            </td>
            <td>${progressBlock || `<span style="color: var(--text-dim);">-</span>`}</td>
            <td>${duration}</td>
            <td style="text-align: right;">
              <button class="btn btn-xs btn-outline stop-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-job-id="${r.job_id || ""}">
                Stop
              </button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  // Attach stop handlers across both cards and table
  document.querySelectorAll<HTMLButtonElement>(".stop-runner-btn").forEach((btn) => {
    btn.onclick = async () => {
      const runnerId = btn.dataset.runnerId!;
      const runnerName = btn.dataset.runnerName!;
      const jobId = btn.dataset.jobId;
      const warning = jobId
        ? `Runner '${runnerName}' is executing Job #${jobId}. Stopping it will fail the workflow.\n\nStop runner?`
        : `Stop and delete runner '${runnerName}'?`;
      if (!confirm(warning)) return;
      try {
        await client.controlRunner("stop", { runnerId });
        showToast(`Stopped runner ${runnerName}`);
        refreshState();
      } catch (err) {
        showToast(`Failed stopping runner: ${(err as Error).message}`, true);
      }
    };
  });
}

// Render Repositories Priority (Dual Card and Table View)
function renderRepos(
  repos: string[],
  queuedJobs: QueuedJob[],
  repoPriority: string[],
  pausedRepos: Set<string>
) {
  if (tabReposCount) tabReposCount.textContent = String(repos.length);
  if (reposCountBadge) reposCountBadge.textContent = `${repos.length} REPOSITORIES`;
  if (!reposList) return;

  const query = repoSearchInput ? repoSearchInput.value.trim().toLowerCase() : "";
  const ordered = repoPriority.length > 0 ? repoPriority : repos;
  const filtered = ordered.filter((r) => r.toLowerCase().includes(query));

  if (repos.length === 0) {
    reposList.innerHTML = '<div class="empty-substate">Discovering active repositories...</div>';
    if (reposTableBody) reposTableBody.innerHTML = '<tr><td colspan="5" class="empty-substate">Discovering active repositories...</td></tr>';
    return;
  }
  if (filtered.length === 0) {
    reposList.innerHTML = `<div class="empty-substate">No repositories matching "${escapeHtml(query)}"</div>`;
    if (reposTableBody) reposTableBody.innerHTML = `<tr><td colspan="5" class="empty-substate">No repositories matching "${escapeHtml(query)}"</td></tr>`;
    return;
  }

  const queuedByRepo: Record<string, number> = {};
  queuedJobs.forEach((j) => {
    if (j.repo) queuedByRepo[j.repo] = (queuedByRepo[j.repo] || 0) + 1;
  });

  // 1. Render Cards / List View
  reposList.innerHTML = filtered
    .map((repo, idx) => {
      const qCount = queuedByRepo[repo] || 0;
      const isPaused = pausedRepos.has(repo);

      let badge = '<span class="repo-queue-badge queue-idle">idle</span>';
      if (isPaused) {
        badge = '<span class="repo-queue-badge queue-paused">PAUSED</span>';
      } else if (qCount > 0) {
        badge = `<span class="repo-queue-badge queue-active">${qCount} queued</span>`;
      }

      return `
        <div class="repo-row ${isPaused ? "repo-row-paused" : ""}" draggable="true" data-repo="${escapeHtml(repo)}" data-index="${idx}">
          <div class="repo-prio-left">
            <span class="drag-handle" title="Drag to reorder priority">⠿</span>
            <span class="priority-rank-badge font-mono" title="Priority #${idx + 1}">#${idx + 1}</span>
            <div class="repo-main">
              <span class="repo-name font-mono">${escapeHtml(repo)}</span>
            </div>
          </div>
          <div class="repo-prio-right">
            ${badge}
            <button class="btn btn-xs ${isPaused ? "btn-resume-repo" : "btn-pause-repo"}" data-action="toggle-pause" data-repo="${escapeHtml(repo)}">
              ${isPaused ? "RESUME" : "PAUSE"}
            </button>
            <div class="prio-move-btns">
              <button class="btn btn-xs btn-move" data-action="move-up" data-repo="${escapeHtml(repo)}" ${idx === 0 ? "disabled" : ""}>▲</button>
              <button class="btn btn-xs btn-move" data-action="move-down" data-repo="${escapeHtml(repo)}" ${idx === filtered.length - 1 ? "disabled" : ""}>▼</button>
            </div>
          </div>
        </div>
      `;
    })
    .join("");

  // 2. Render Table View
  if (reposTableBody) {
    reposTableBody.innerHTML = filtered
      .map((repo, idx) => {
        const qCount = queuedByRepo[repo] || 0;
        const isPaused = pausedRepos.has(repo);

        return `
          <tr>
            <td>
              <span class="priority-rank-badge font-mono">#${idx + 1}</span>
            </td>
            <td>
              <span class="repo-name font-mono" style="font-weight: 700;">${escapeHtml(repo)}</span>
            </td>
            <td>
              <span class="badge ${isPaused ? "badge-danger" : "badge-live"} font-mono" style="font-size: 10px;">
                ${isPaused ? "PAUSED" : "ACTIVE"}
              </span>
            </td>
            <td>
              <span class="font-mono" style="color: ${qCount > 0 ? "var(--solar)" : "var(--text-muted)"};">
                ${qCount > 0 ? `${qCount} queued` : "idle"}
              </span>
            </td>
            <td style="text-align: right; white-space: nowrap;">
              <button class="btn btn-xs ${isPaused ? "btn-resume-repo" : "btn-pause-repo"}" data-action="toggle-pause" data-repo="${escapeHtml(repo)}">
                ${isPaused ? "RESUME" : "PAUSE"}
              </button>
              <button class="btn btn-xs btn-move" data-action="move-up" data-repo="${escapeHtml(repo)}" ${idx === 0 ? "disabled" : ""}>▲</button>
              <button class="btn btn-xs btn-move" data-action="move-down" data-repo="${escapeHtml(repo)}" ${idx === filtered.length - 1 ? "disabled" : ""}>▼</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  // Attach priority handlers across both list and table
  document.querySelectorAll<HTMLButtonElement>("button[data-action]").forEach((btn) => {
    const action = btn.dataset.action;
    if (action !== "toggle-pause" && action !== "move-up" && action !== "move-down") return;

    btn.onclick = async (e) => {
      e.stopPropagation();
      const repo = btn.dataset.repo!;
      const newPrio = [...ordered];
      const newPaused = new Set(pausedRepos);

      if (action === "toggle-pause") {
        if (newPaused.has(repo)) newPaused.delete(repo);
        else newPaused.add(repo);
      } else if (action === "move-up") {
        const i = newPrio.indexOf(repo);
        if (i > 0) {
          const tmp = newPrio[i - 1];
          newPrio[i - 1] = newPrio[i];
          newPrio[i] = tmp;
        }
      } else if (action === "move-down") {
        const i = newPrio.indexOf(repo);
        if (i >= 0 && i < newPrio.length - 1) {
          const tmp = newPrio[i + 1];
          newPrio[i + 1] = newPrio[i];
          newPrio[i] = tmp;
        }
      }

      currentRepoPriority = newPrio;
      currentPausedRepos = newPaused;
      renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
      try {
        await client.updateRepoPriority(newPrio, Array.from(newPaused));
        showToast("Priority updated");
      } catch (err) {
        showToast(`Failed updating priority: ${(err as Error).message}`, true);
      }
    };
  });

  // Drag and drop support
  reposList.querySelectorAll<HTMLElement>(".repo-row").forEach((row) => {
    row.ondragstart = () => {
      draggedRepo = row.dataset.repo || null;
      row.classList.add("repo-row-dragging");
    };
    row.ondragend = () => {
      draggedRepo = null;
      reposList.querySelectorAll(".repo-row").forEach((r) => r.classList.remove("repo-row-dragging", "repo-row-drag-over"));
    };
    row.ondragover = (e) => {
      e.preventDefault();
      row.classList.add("repo-row-drag-over");
    };
    row.ondragleave = () => {
      row.classList.remove("repo-row-drag-over");
    };
    row.ondrop = async (e) => {
      e.preventDefault();
      row.classList.remove("repo-row-drag-over");
      const targetRepo = row.dataset.repo;
      if (!draggedRepo || draggedRepo === targetRepo) return;
      const newPrio = [...ordered];
      const fromIdx = newPrio.indexOf(draggedRepo);
      const toIdx = newPrio.indexOf(targetRepo!);
      if (fromIdx >= 0 && toIdx >= 0) {
        newPrio.splice(fromIdx, 1);
        newPrio.splice(toIdx, 0, draggedRepo);
        currentRepoPriority = newPrio;
        renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
        try {
          await client.updateRepoPriority(newPrio, Array.from(currentPausedRepos));
          showToast("Priority reordered");
        } catch (err) {
          showToast(`Error saving priority: ${(err as Error).message}`, true);
        }
      }
    };
  });
}

function renderCompletedJobs(jobs: CompletedJob[]) {
  if (tabJobsCount) tabJobsCount.textContent = String(jobs.length);

  if (!jobsList) return;

  if (jobs.length === 0) {
    jobsList.innerHTML = `
      <div class="empty-substate empty-queue-clean">
        <div class="clean-check-icon">✓</div>
        <div class="clean-text font-mono">NO COMPLETED JOBS YET</div>
        <div class="clean-subtext">Recent successful and failed GitHub Actions jobs appear here with a quick retry path.</div>
      </div>
    `;
    return;
  }

  const sorted = [...jobs].sort((a, b) => {
    const av = a.completed_at ? new Date(a.completed_at).getTime() : 0;
    const bv = b.completed_at ? new Date(b.completed_at).getTime() : 0;
    return bv - av;
  });

  jobsList.innerHTML = sorted
    .map((job) => {
      const conclusion = (job.conclusion || "unknown").toLowerCase();
      const isSuccess = conclusion === "success";
      const headerKind = isSuccess ? "badge-live" : "badge-danger";
      const statusText = isSuccess ? "SUCCESS" : conclusion.toUpperCase() || "FAILED";
      const reason = job.failure_reason || job.failed_step || "No failure reason captured.";
      const messages = (job.messages || []).map((msg: string) => `<li>${escapeHtml(msg)}</li>`).join("");
      const runUrl = job.run_url || `https://github.com/${job.repo}/actions/runs/${job.run_id}`;
      const retryBtn = !isSuccess
        ? `<button class="btn btn-xs btn-outline job-rerun-btn font-mono" data-repo="${escapeHtml(job.repo)}" data-run-id="${job.run_id}">↻ Retry failed jobs</button>`
        : "";

      return `
        <article class="glass-panel" style="padding: 1rem 1.1rem; display: flex; flex-direction: column; gap: 0.7rem; border-left: 3px solid ${isSuccess ? "var(--emerald)" : "var(--crimson)"};">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap;">
            <div style="display: flex; flex-direction: column; gap: 0.2rem; min-width: 0;">
              <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <span class="badge ${headerKind} font-mono" style="font-size: 10px;">${statusText}</span>
                <a href="${escapeHtml(runUrl)}" target="_blank" rel="noopener noreferrer" style="font-weight: 700; color: var(--text-main); text-decoration: none;">
                  ${escapeHtml(job.name)}
                </a>
              </div>
              <div style="font-size: 0.82rem; color: var(--text-muted); display: flex; flex-wrap: wrap; gap: 0.5rem;">
                <span class="font-mono">${escapeHtml(job.repo)}</span>
                ${job.workflow_name ? `<span>•</span><span>${escapeHtml(job.workflow_name)}</span>` : ""}
                ${job.run_attempt && job.run_attempt > 1 ? `<span>•</span><span class="badge mono" style="font-size: 0.65rem;">Attempt ${job.run_attempt}</span>` : ""}
                ${job.head_branch ? `<span>•</span><span class="font-mono">${escapeHtml(job.head_branch)}</span>` : ""}
              </div>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted); text-align: right;">
              <div class="font-mono">${job.completed_at ? new Date(job.completed_at).toLocaleString() : "—"}</div>
              ${job.duration_sec !== undefined ? `<div class="font-mono">${job.duration_sec}s</div>` : ""}
            </div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.35rem;">
            <div style="font-size: 0.8rem; color: var(--text-main); font-weight: 600;">Why it failed</div>
            <div style="font-size: 0.82rem; color: ${isSuccess ? "var(--emerald)" : "var(--solar)"}; line-height: 1.5;">
              ${escapeHtml(reason)}
            </div>
            ${job.failed_step ? `<div style="font-size: 0.75rem; color: var(--text-muted);">Failed step: <span class="font-mono">${escapeHtml(job.failed_step)}</span></div>` : ""}
            ${messages ? `<ul style="margin: 0.2rem 0 0 1.25rem; color: var(--text-muted); font-size: 0.78rem; line-height: 1.5;">${messages}</ul>` : ""}
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
            <a href="${escapeHtml(job.html_url || runUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-xs btn-outline font-mono">Open in GitHub</a>
            ${retryBtn}
          </div>
        </article>
      `;
    })
    .join("");

  jobsList.querySelectorAll<HTMLButtonElement>(".job-rerun-btn").forEach((btn) => {
    btn.onclick = async () => {
      const repo = btn.dataset.repo!;
      const runId = Number(btn.dataset.runId);
      if (!repo || Number.isNaN(runId)) return;
      if (!confirm(`Retry failed jobs for ${repo} run #${runId}?`)) return;
      try {
        const res = await client.triggerWorkflowAction(repo, runId, "rerun-failed");
        showToast(res.message || `Retry queued for ${repo} run #${runId}`);
      } catch (err) {
        showToast(`Failed to retry jobs: ${(err as Error).message}`, true);
      }
    };
  });
}

// Render Queued Workflow Jobs View (Dual Card and Table View with GitHub Run Link and Progress)
function renderQueue(queuedJobs: QueuedJob[], concurrency: { active: number; max: number }) {
  if (tabQueueCount) tabQueueCount.textContent = String(queuedJobs.length);
  const activeRunners = concurrency.active;
  const maxRunners = concurrency.max;
  const freeSlots = Math.max(0, maxRunners - activeRunners);

  if (queueBusySlots) queueBusySlots.textContent = String(activeRunners);
  if (queueMaxSlots) queueMaxSlots.textContent = String(maxRunners);
  if (queueFreeSlots) queueFreeSlots.textContent = String(freeSlots);
  if (queueTotalJobs) queueTotalJobs.textContent = String(queuedJobs.length);

  if (queueSlotsBadge) {
    queueSlotsBadge.textContent = `${activeRunners}/${maxRunners} SLOTS`;
  }
  if (queueJobsCountTag) {
    queueJobsCountTag.textContent = `${queuedJobs.length} JOBS`;
  }

  const hasJobs = queuedJobs.length > 0;
  if (queueTableEmpty) {
    if (hasJobs) queueTableEmpty.classList.add("hidden");
    else queueTableEmpty.classList.remove("hidden");
  }

  if (!hasJobs) {
    if (queueJobsView) {
      queueJobsView.innerHTML = `
        <div class="empty-substate empty-queue-clean">
          <div class="clean-check-icon">✓</div>
          <div class="clean-text font-mono">ALL WORKFLOW QUEUES ARE CLEAR</div>
          <div class="clean-subtext">Waiting jobs will appear here in real-time as GitHub Actions workflows trigger.</div>
        </div>
      `;
    }
    if (queueTableBody) {
      queueTableBody.innerHTML = "";
    }
    return;
  }

  // 1. Render Cards View
  if (queueJobsView) {
    queueJobsView.innerHTML = queuedJobs
      .map((j) => {
        const isRunning = j.status === "in_progress";
        const posTag = j.queue_position ? `<span class="priority-rank-badge font-mono" style="margin-right: 0.5rem;">Rank #${j.queue_position}</span>` : "";
        const statusBadge = isRunning
          ? '<span class="badge badge-pulse" style="font-size: 11px;">RUNNING</span>'
          : '<span class="badge badge-queued font-mono" style="font-size: 11px;">QUEUED</span>';

        const runUrl = j.run_url || `https://github.com/${j.repo}/actions/runs/${j.run_id}`;
        const runLink = `<a href="${escapeHtml(runUrl)}" target="_blank" rel="noopener noreferrer" style="color: var(--solar); text-decoration: none; font-weight: 700;">Run #${j.run_id} ↗</a>`;

        const labels = (j.labels || [])
          .filter((l) => l !== "self-hosted")
          .map((l) => `<span class="tech-chip ${l === "arm64" ? "solar" : "cyan"} font-mono" style="font-size: 10px;">${escapeHtml(l.toUpperCase())}</span>`)
          .join(" ");

        let progressBlock = "";
        if (j.progress_pct !== undefined || (j.stages_total && j.stages_total > 0)) {
          const pct = j.progress_pct ?? 0;
          progressBlock = `
            <div class="mini-progress-wrap" style="margin-top: 6px;">
              <div class="mini-progress-text">
                <span>Stage ${j.stages_done ?? 0}/${j.stages_total ?? 1} done</span>
                <span style="color: var(--emerald); font-weight: 700;">${pct}%</span>
              </div>
              <div class="mini-progress-track">
                <div class="mini-progress-fill" style="width: ${pct}%;"></div>
              </div>
              ${j.current_step ? `<span style="font-size: 10px; color: var(--cyan); margin-top: 2px;">Step: ${escapeHtml(j.current_step)}</span>` : ""}
            </div>
          `;
        }

        const waitingReason = j.waiting_reason
          ? `<div style="font-size: 11px; color: var(--solar); margin-top: 4px; font-family: var(--font-mono);">⏱ ${escapeHtml(j.waiting_reason)}</div>`
          : "";

        const duration = formatDuration(j.started_at || j.created_at);

        return `
          <div class="job-queue-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 12px 16px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
              <div style="display: flex; flex-direction: column; gap: 4px;">
                <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                  ${posTag}
                  ${statusBadge}
                  <a href="${escapeHtml(j.html_url)}" target="_blank" rel="noopener noreferrer" style="font-weight: 700; font-size: 14px; color: var(--text-main); text-decoration: none;">
                    ${escapeHtml(j.name)} ↗
                  </a>
                </div>
                <div style="font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <span class="font-mono" style="color: var(--text-main); font-weight: 600;">${escapeHtml(j.repo)}</span>
                  <span>•</span>
                  <span>${escapeHtml(j.workflow_name || "Workflow")}</span>
                  <span>•</span>
                  ${runLink}
                  ${j.head_branch ? `<span>•</span><span class="font-mono" style="color: var(--cyan);">${escapeHtml(j.head_branch)}</span>` : ""}
                </div>
                ${progressBlock}
                ${waitingReason}
              </div>
              <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                <span class="font-mono" style="font-size: 12px; color: ${isRunning ? "var(--emerald)" : "var(--text-muted)"};">
                  ${isRunning ? "running" : "waiting"} ${duration}
                </span>
                <div style="display: flex; gap: 4px;">${labels}</div>
              </div>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.04);">
              <button class="btn btn-xs btn-outline action-btn" data-action="cancel" data-repo="${escapeHtml(j.repo)}" data-run-id="${j.run_id}">✕ Cancel Run</button>
              <button class="btn btn-xs btn-outline action-btn" data-action="rerun" data-repo="${escapeHtml(j.repo)}" data-run-id="${j.run_id}">↺ Re-run All</button>
              <button class="btn btn-xs btn-outline action-btn" data-action="rerun-failed" data-repo="${escapeHtml(j.repo)}" data-run-id="${j.run_id}">↻ Re-run Failed</button>
            </div>
          </div>
        `;
      })
      .join("");
  }

  // 2. Render Table View
  if (queueTableBody) {
    queueTableBody.innerHTML = queuedJobs
      .map((j) => {
        const isRunning = j.status === "in_progress";
        const runUrl = j.run_url || `https://github.com/${j.repo}/actions/runs/${j.run_id}`;
        const duration = formatDuration(j.started_at || j.created_at);
        const pct = j.progress_pct ?? 0;

        return `
          <tr>
            <td>
              <span class="priority-rank-badge font-mono">#${j.queue_position || 1}</span>
            </td>
            <td>
              <span class="badge ${isRunning ? "badge-pulse" : "badge-queued"} font-mono" style="font-size: 10px;">
                ${isRunning ? "RUNNING" : "QUEUED"}
              </span>
            </td>
            <td>
              <a href="${escapeHtml(j.html_url)}" target="_blank" rel="noopener noreferrer" style="font-weight: 700;">
                ${escapeHtml(j.name)} ↗
              </a>
              <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(j.workflow_name || "Workflow")}</div>
            </td>
            <td>
              <a href="${escapeHtml(runUrl)}" target="_blank" rel="noopener noreferrer" style="color: var(--solar); font-weight: 700;">
                Run #${j.run_id} ↗
              </a>
            </td>
            <td>
              <div class="font-mono" style="font-weight: 600;">${escapeHtml(j.repo)}</div>
              ${j.head_branch ? `<div class="font-mono" style="font-size: 10px; color: var(--cyan);">${escapeHtml(j.head_branch)}</div>` : ""}
            </td>
            <td>
              <div class="mini-progress-wrap">
                <div class="mini-progress-text">
                  <span>${j.stages_done ?? 0}/${j.stages_total ?? 1}</span>
                  <span style="color: var(--emerald); font-weight: 700;">${pct}%</span>
                </div>
                <div class="mini-progress-track">
                  <div class="mini-progress-fill" style="width: ${pct}%;"></div>
                </div>
              </div>
            </td>
            <td>
              <span class="font-mono" style="font-size: 11px;">${duration}</span>
            </td>
            <td style="text-align: right; white-space: nowrap;">
              <button class="btn btn-xs btn-outline action-btn" data-action="cancel" data-repo="${escapeHtml(j.repo)}" data-run-id="${j.run_id}" title="Cancel Run">✕</button>
              <button class="btn btn-xs btn-outline action-btn" data-action="rerun" data-repo="${escapeHtml(j.repo)}" data-run-id="${j.run_id}" title="Re-run All">↺</button>
              <button class="btn btn-xs btn-outline action-btn" data-action="rerun-failed" data-repo="${escapeHtml(j.repo)}" data-run-id="${j.run_id}" title="Re-run Failed">↻</button>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  // Attach workflow control handlers across both card and table buttons
  document.querySelectorAll<HTMLButtonElement>(".action-btn").forEach((btn) => {
    btn.onclick = async () => {
      const repo = btn.dataset.repo!;
      const runId = parseInt(btn.dataset.runId!, 10);
      const action = btn.dataset.action as "cancel" | "rerun" | "rerun-failed";
      if (!confirm(`Are you sure you want to ${action} run #${runId} on ${repo}?`)) return;
      try {
        await client.triggerWorkflowAction(repo, runId, action);
        showToast(`Workflow ${action} triggered`);
        refreshState();
      } catch (err) {
        showToast(`Action failed: ${(err as Error).message}`, true);
      }
    };
  });
}

// Render Actions Billing
function renderBilling(billing?: FleetState["actions_billing"]) {
  if (!actionsScope || !billing) return;
  actionsScope.textContent = "USER:el-j";
  if (actionsIncluded) actionsIncluded.textContent = billing.included_minutes ? `${billing.included_minutes.toLocaleString()}m` : "--";
  if (actionsTotalUsed) actionsTotalUsed.textContent = billing.total_minutes_used !== undefined ? `${billing.total_minutes_used.toLocaleString()}m` : "--";
  if (actionsPaidUsed) actionsPaidUsed.textContent = billing.total_paid_minutes_used !== undefined ? `${billing.total_paid_minutes_used.toLocaleString()}m` : "--";
  if (actionsRemaining) {
    const rem = (billing.included_minutes || 2000) - (billing.total_minutes_used || 0);
    actionsRemaining.textContent = `${Math.max(0, rem).toLocaleString()}m`;
  }
  if (actionsUpdated) actionsUpdated.textContent = new Date().toLocaleTimeString();
  if (actionsStatus) {
    actionsStatus.textContent = "Live billing synced from GitHub API.";
    actionsStatus.className = "billing-status font-mono ok";
  }
}

// Render Cache Stats in Right Sidebar Panel
async function loadCacheStats() {
  try {
    const data: CacheStats = await client.getCacheStats();
    if (kpiCacheSize) kpiCacheSize.textContent = data.total_human || "0 B";

    const maxBytes = Math.max(1, ...data.categories.map((c) => c.bytes));
    data.categories.forEach((cat) => {
      const idKey = cat.category.toLowerCase().replace(/[^a-z0-9]/g, "-");
      const sizeEl = document.getElementById(`sz-${idKey}`);
      const barEl = document.getElementById(`bar-cache-${idKey}`);
      if (sizeEl) sizeEl.textContent = cat.human_readable;
      if (barEl) {
        const pct = Math.max(5, Math.min(100, Math.round((cat.bytes / maxBytes) * 100)));
        barEl.style.width = `${pct}%`;
      }
    });
  } catch (err) {
    console.warn("Could not refresh cache stats:", err);
  }
}

// Live Settings Management
async function loadSettings() {
  try {
    const s = await client.getSettings();
    if (cfgMaxRunners) cfgMaxRunners.textContent = String(s.max_runners ?? 3);
    if (cfgMinRunners) cfgMinRunners.textContent = String(s.min_runners ?? 0);
    if (cfgRunnerBackend) cfgRunnerBackend.textContent = s.runner_backend ?? "auto";
    if (cfgAutoRouteVm) cfgAutoRouteVm.textContent = s.auto_route_vm ? "enabled" : "disabled";
    if (cfgCacheEnabled) cfgCacheEnabled.textContent = s.cache_enabled ? "active" : "disabled";
    return s;
  } catch (err) {
    console.warn("Could not load settings:", err);
    return null;
  }
}

async function openSettingsModal() {
  if (!settingsModal) return;
  showToast("Loading configuration...");
  try {
    const s = await client.getSettings();
    if (inputMaxRunners) inputMaxRunners.value = String(s.max_runners ?? 3);
    if (inputMinRunners) inputMinRunners.value = String(s.min_runners ?? 0);
    if (inputRunnerCpus) inputRunnerCpus.value = String(s.runner_cpus ?? 2);
    if (inputRunnerMemory) inputRunnerMemory.value = s.runner_memory || "4G";
    if (selectRunnerBackend) selectRunnerBackend.value = s.runner_backend || "auto";
    if (selectRunnerArch) selectRunnerArch.value = s.runner_arch || "both";
    if (checkboxAutoRouteVm) checkboxAutoRouteVm.checked = Boolean(s.auto_route_vm);
    if (selectNativeOverride) selectNativeOverride.value = s.native_arch_override || "off";
    if (inputPollInterval) inputPollInterval.value = String(s.poll_interval ?? 10);
    if (inputDiscoveryInterval) inputDiscoveryInterval.value = String(s.discovery_interval ?? 300);
    if (checkboxCacheEnabled) checkboxCacheEnabled.checked = Boolean(s.cache_enabled);
    if (checkboxProxiesEnabled) checkboxProxiesEnabled.checked = Boolean(s.proxies_enabled);
    if (inputCacheDir) inputCacheDir.value = s.host_cache_dir || "";
    settingsModal.showModal();
  } catch (err) {
    showToast(`Failed to load settings: ${(err as Error).message}`, true);
  }
}

async function saveSettings() {
  if (!settingsModal) return;
  if (!inputMaxRunners || !inputMinRunners) return;

  const payload: SystemSettings = {
    max_runners: parseInt(inputMaxRunners.value, 10),
    min_runners: parseInt(inputMinRunners.value, 10),
    runner_cpus: inputRunnerCpus ? parseInt(inputRunnerCpus.value, 10) : undefined,
    runner_memory: inputRunnerMemory ? inputRunnerMemory.value.trim() : undefined,
    runner_backend: selectRunnerBackend ? selectRunnerBackend.value : undefined,
    runner_arch: selectRunnerArch ? selectRunnerArch.value : undefined,
    auto_route_vm: checkboxAutoRouteVm ? checkboxAutoRouteVm.checked : undefined,
    native_arch_override: selectNativeOverride ? selectNativeOverride.value : undefined,
    poll_interval: inputPollInterval ? parseInt(inputPollInterval.value, 10) : undefined,
    discovery_interval: inputDiscoveryInterval ? parseInt(inputDiscoveryInterval.value, 10) : undefined,
    cache_enabled: checkboxCacheEnabled ? checkboxCacheEnabled.checked : undefined,
    proxies_enabled: checkboxProxiesEnabled ? checkboxProxiesEnabled.checked : undefined,
    host_cache_dir: inputCacheDir ? inputCacheDir.value.trim() : undefined,
  };

  showToast("Applying configuration update...");
  try {
    await client.updateSettings(payload);
    settingsModal.close();
    showToast("✓ Settings updated successfully (.env updated)");
    loadSettings();
    refreshState();
  } catch (err) {
    showToast(`Failed to save settings: ${(err as Error).message}`, true);
  }
}

// Master Render from Fleet State Snapshot
function renderState(state: FleetState) {
  if (!state) return;

  statVersion.textContent = (state as any).version ? `v${(state as any).version}` : "v1.0.0";
  statEngine.textContent = "DOCKER";

  // Rate limits
  const rem = state.rate_limit_remaining ?? null;
  const tot = state.rate_limit_limit ?? null;
  statRateLimit.textContent = rem !== null && tot !== null ? `${rem}/${tot}` : "--/--";
  const ratePct = rem !== null && tot ? Math.min(100, Math.max(0, (rem / tot) * 100)) : 0;
  statRateLimitBar.style.width = `${ratePct}%`;
  if (ratePct < 20) statRateLimitBar.style.backgroundColor = "var(--crimson)";
  else if (ratePct < 50) statRateLimitBar.style.backgroundColor = "var(--solar)";
  else statRateLimitBar.style.backgroundColor = "var(--emerald)";

  if (statRateMeta && rem !== null && tot) {
    statRateMeta.textContent = `used ${tot - rem} • reset ${formatReset((state as any).rate_limit_reset)} • REST Core`;
  }

  const completedJobs = (state as FleetState & { completed_jobs?: CompletedJob[] }).completed_jobs || [];
  renderCompletedJobs(completedJobs);

  // Active concurrency
  const activeCount = state.busy_runners ?? 0;
  const maxCount = state.max_runners ?? 3;
  currentConcurrency = { active: activeCount, max: maxCount, min: 0 };
  kpiActiveRunners.textContent = String(activeCount);
  kpiMaxRunners.textContent = `/ ${maxCount} max`;
  kpiMinRunnersText.textContent = `// 0 standby pool`;
  if (kpiRunnerSizing) kpiRunnerSizing.textContent = `// 3 CPU · 4.0 GiB each`;

  const runnersPct = Math.min(100, Math.round((activeCount / Math.max(1, maxCount)) * 100));
  kpiRunnersBar.style.width = `${runnersPct}%`;

  // Queued jobs
  const jobs = state.queued_jobs || [];
  currentQueuedJobs = jobs;
  kpiQueuedJobs.textContent = String(jobs.length);
  const queuePct = Math.min(100, jobs.length * 25);
  kpiQueueBar.style.width = `${queuePct}%`;

  // Monitored repos
  currentRepos = state.repo_priority || [];
  kpiReposMonitored.textContent = `// Across ${currentRepos.length} tracked repo(s)`;
  currentRepoPriority = state.repo_priority || [];
  currentPausedRepos = new Set(state.paused_repos || []);

  // Hybrid routing ratio
  const totalJobs = jobs.length + activeCount;
  const vmJobs = (state.runners || []).filter((r) => r.backend === "orbstack").length;
  const dockerJobs = (state.runners || []).filter((r) => r.backend !== "orbstack").length;
  const vmRatio = totalJobs > 0 ? Math.round((vmJobs / Math.max(1, totalJobs)) * 100) : 0;
  kpiVmRatio.textContent = `${vmRatio}%`;
  kpiRoutingBar.style.width = `${vmRatio}%`;
  if (kpiRoutingSub) {
    const routeSummary = vmJobs > 0 || dockerJobs > 0 ? `${vmJobs} VM / ${dockerJobs} container` : "Auto-detect DIND & Services";
    kpiRoutingSub.textContent = `// ${routeSummary}`;
  }
  if (cntDockerJobs) cntDockerJobs.textContent = String(dockerJobs);
  if (cntVmJobs) cntVmJobs.textContent = String(vmJobs);
  if (barDockerJobs) barDockerJobs.style.width = `${100 - vmRatio}%`;
  if (barVmJobs) barVmJobs.style.width = `${vmRatio}%`;

  if (kpiCacheBar && state.actions_billing) {
    const cacheFill = Math.min(100, Math.max(10, (state.actions_billing.total_minutes_used || 0) % 100));
    kpiCacheBar.style.width = `${cacheFill}%`;
  }

  // Render subcomponents
  renderRunners(state.runners || []);
  renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
  renderQueue(currentQueuedJobs, currentConcurrency);
  renderBilling(state.actions_billing);
}

// Fetch State from Server
async function refreshState() {
  try {
    const st = await client.getFleet();
    setConnectionStatus("online", "LIVE OBSERVABILITY");
    renderState(st);
  } catch (err) {
    setConnectionStatus("error", "RECONNECTING...");
    console.warn("Poll state warning:", err);
  }
}

// Bind Global Actions & Event Handlers
function initHandlers() {
  // Telemetry drawer + clickable KPI cards
  const drawer = document.getElementById("telemetry-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  const openDrawer = (section?: string) => {
    drawer?.classList.add("open");
    backdrop?.classList.add("open");
    if (section) {
      const map: Record<string, string> = { routing: "panel-routing-telemetry", cache: "panel-cache-analytics" };
      const el = document.getElementById(map[section] || "");
      if (el) setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 120);
    }
  };
  const closeDrawer = () => {
    drawer?.classList.remove("open");
    backdrop?.classList.remove("open");
  };
  document.getElementById("btn-open-drawer")?.addEventListener("click", () => openDrawer());
  document.getElementById("btn-close-drawer")?.addEventListener("click", closeDrawer);
  backdrop?.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });
  document.querySelectorAll<HTMLElement>("[data-kpi-target]").forEach((card) => {
    card.addEventListener("click", () => {
      const target = card.dataset.kpiTarget!;
      if (target === "runners" || target === "queue") setActiveTab(target);
      else openDrawer(target);
    });
  });
  // Master tabs switching
  if (tabBtnRunners) tabBtnRunners.onclick = () => setActiveTab("runners");
  if (tabBtnQueue) tabBtnQueue.onclick = () => setActiveTab("queue");
  if (tabBtnJobs) tabBtnJobs.onclick = () => setActiveTab("jobs");
  if (tabBtnRepos) tabBtnRepos.onclick = () => setActiveTab("repos");

  // View mode switcher
  if (viewModeCards) viewModeCards.onclick = () => setViewMode("cards");
  if (viewModeTable) viewModeTable.onclick = () => setViewMode("table");
  if (selectViewModeSetting) {
    selectViewModeSetting.onchange = () => {
      setViewMode(selectViewModeSetting.value as "cards" | "table");
    };
  }

  // Full bottom terminal toggle
  if (btnToggleTerminalExpand) {
    btnToggleTerminalExpand.onclick = toggleTerminal;
  }

  // Prune fleet
  if (btnPruneRunners) {
    btnPruneRunners.onclick = async () => {
      try {
        await fetch("/api/actions/prune", { method: "POST", headers: { "Content-Type": "application/json" } });
        showToast("Triggered fleet runner prune");
        refreshState();
      } catch (err) {
        showToast(`Prune failed: ${(err as Error).message}`, true);
      }
    };
  }

  // Clear logs
  if (btnClearLogs) {
    btnClearLogs.onclick = () => {
      if (logTerminal) logTerminal.innerHTML = "";
    };
  }

  // Purge all caches
  if (btnPurgeAllCaches) {
    btnPurgeAllCaches.onclick = async () => {
      if (!confirm("Are you sure you want to clear all host package caches?")) return;
      try {
        await client.purgeCache({ all: true });
        showToast("✓ Cleared all host caches");
        loadCacheStats();
      } catch (err) {
        showToast(`Purge failed: ${(err as Error).message}`, true);
      }
    };
  }

  // Clear individual category
  document.querySelectorAll<HTMLButtonElement>("[data-purge-category]").forEach((btn) => {
    btn.onclick = async () => {
      const cat = btn.dataset.purgeCategory!;
      if (!confirm(`Purge cache category '${cat}'?`)) return;
      try {
        await client.purgeCache({ category: cat });
        showToast(`✓ Purged ${cat} cache`);
        loadCacheStats();
      } catch (err) {
        showToast(`Purge error: ${(err as Error).message}`, true);
      }
    };
  });

  // Search input filter
  if (repoSearchInput) {
    repoSearchInput.oninput = () => {
      renderRepos(currentRepos, currentQueuedJobs, currentRepoPriority, currentPausedRepos);
    };
  }

  // Spawn Modal Controls
  if (btnStartRunner && spawnModal) {
    btnStartRunner.onclick = () => {
      if (manualRepoInput && currentRepos.length > 0) {
        manualRepoInput.value = currentRepos[0];
      }
      spawnModal.showModal();
    };
  }
  if (spawnModalClose && spawnModal) {
    spawnModalClose.onclick = () => spawnModal.close();
  }
  if (spawnModalCancel && spawnModal) {
    spawnModalCancel.onclick = () => spawnModal.close();
  }
  if (spawnModalSubmit && spawnModal) {
    spawnModalSubmit.onclick = async () => {
      const repo = manualRepoInput ? manualRepoInput.value.trim() : "";
      const arch = manualArchSelect ? manualArchSelect.value : "amd64";
      if (!repo) {
        alert("Please enter a target repository.");
        return;
      }
      spawnModal.close();
      showToast(`Launching runner for ${repo} (${arch})...`);
      try {
        await client.controlRunner("start", { repo, arch });
        showToast(`✓ Runner launched for ${repo}`);
        refreshState();
      } catch (err) {
        showToast(`Launch failed: ${(err as Error).message}`, true);
      }
    };
  }

  // Settings Modal Controls
  if (btnOpenSettings) {
    btnOpenSettings.onclick = (e) => {
      e.preventDefault();
      openSettingsModal();
    };
  }
  if (btnOpenSettingsPanel) {
    btnOpenSettingsPanel.onclick = (e) => {
      e.preventDefault();
      openSettingsModal();
    };
  }
  if (settingsModalClose && settingsModal) {
    settingsModalClose.onclick = () => settingsModal.close();
  }
  if (settingsModalCancel && settingsModal) {
    settingsModalCancel.onclick = () => settingsModal.close();
  }
  if (settingsModalSave) {
    settingsModalSave.onclick = (e) => {
      e.preventDefault();
      saveSettings();
    };
  }
  if (settingsForm) {
    settingsForm.onsubmit = (e) => {
      e.preventDefault();
      saveSettings();
    };
  }

  // Real-time ticking for wait times & uptime
  window.setInterval(() => {
    lastUptimeSeconds += 1;
    const h = Math.floor(lastUptimeSeconds / 3600);
    const m = Math.floor((lastUptimeSeconds % 3600) / 60);
    const s = lastUptimeSeconds % 60;
    if (statUptime) {
      statUptime.textContent = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    }
  }, 1000);
}

// Bootstrap Application
async function startApp() {
  initHandlers();
  setViewMode(currentViewMode);
  setActiveTab(currentTab);
  setConnectionStatus("connecting", "CONNECTING...");

  // Initial loads
  await refreshState();
  loadSettings();
  loadCacheStats();

  // Load initial logs
  try {
    const res = await fetch("/api/logs");
    if (res.ok) {
      const data = await res.json();
      if (data.logs && Array.isArray(data.logs)) {
        data.logs.forEach((l: { message: string; timestamp?: string }) => appendLog(l.message, l.timestamp));
      }
    }
  } catch (err) {
    console.warn("Could not load initial logs:", err);
  }

  // Subscribe to real-time SSE stream
  client.subscribeSSE({
    onFleet: (newState) => {
      setConnectionStatus("online", "LIVE OBSERVABILITY");
      renderState(newState);
    },
    onActivity: (msg) => {
      appendLog(msg);
    },
    onError: () => {
      setConnectionStatus("error", "RECONNECTING...");
    },
  });

  // Background refresh every 10s for state, 20s for cache
  window.setInterval(refreshState, 10000);
  window.setInterval(loadCacheStats, 20000);
}

startApp();
