import { type RunnerInfo } from "../api/client";
import { openRunnerTerminal, stopRunner } from "../actions";
import { dom } from "../dom";
import {
  compareValues,
  escapeHtml,
  formatDuration,
  includesFilter,
  normalizeFilter,
} from "../format";
import { jobLinkHtml, progressHtml, runLinkHtml } from "./runRef";
import { state } from "../state";
import { isVmBackend } from "./backend";

/** What the counts, filters, cards, table and sort all derive from a runner. */
function describe(r: RunnerInfo) {
  const engine = (r.backend || "docker").toUpperCase();
  const origin = r.is_cloud ? "cloud" : r.origin || "local";
  return {
    isVm: isVmBackend(r.backend),
    origin,
    isLocal: origin === "local",
    engine,
    arch: (r.target_arch || "amd64").toUpperCase(),
    provider: (r.provider || "github").toLowerCase(),
  };
}

const PROVIDER_BADGE_STYLE: Record<string, string> = {
  gitlab:
    "background: rgba(252, 109, 38, 0.15); color: #fc6d26; border: 1px solid rgba(252, 109, 38, 0.3);",
  github:
    "background: rgba(88, 166, 255, 0.15); color: #58a6ff; border: 1px solid rgba(88, 166, 255, 0.3);",
};

const ORIGIN_BADGE: Record<string, [string, string]> = {
  cloud: [
    "background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3);",
    "☁️ Cloud",
  ],
  external: [
    "background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);",
    "🌐 External",
  ],
  local: [
    "background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);",
    "🖥️ Local",
  ],
};

/** The provider and origin badges; `size` is the badge's padding and font-size CSS. */
function badges(d: ReturnType<typeof describe>, size: string, providerExtra = ""): string {
  const isGitLab = d.provider === "gitlab";
  const [originStyle, originText] = ORIGIN_BADGE[d.origin];
  return `<span class="tag-provider font-mono" style="${PROVIDER_BADGE_STYLE[isGitLab ? "gitlab" : "github"]} border-radius: 4px; ${size}${providerExtra}">${isGitLab ? "GitLab" : "GitHub"}</span>
                <span class="tag-origin font-mono" style="${originStyle} border-radius: 4px; ${size}">${originText}</span>`;
}

/** Terminal and Stop buttons for a local runner; remote runners are managed elsewhere. */
function actionButtons(
  r: RunnerInfo,
  d: ReturnType<typeof describe>,
  terminalStyle: string,
): string {
  if (!d.isLocal)
    return `<span class="badge badge-neutral font-mono" style="font-size: 10px; opacity: 0.8;">Remote Managed</span>`;
  return `
            <button class="btn btn-xs btn-outline terminal-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-backend="${escapeHtml(r.backend || "")}"${terminalStyle} title="Open terminal directly connected into runner">
              &gt;_ Terminal
            </button>
            <button class="btn btn-xs btn-outline stop-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-job-id="${r.job_id || ""}">
              Stop
            </button>
          `;
}

/**
 * Renders the runner fleet as cards and table rows (with filters, sorting, GitHub links and progress) and binds the per-runner buttons.
 */
export function renderRunners(runners: RunnerInfo[]) {
  const {
    tabRunnersCount,
    runnersTableBody,
    runnersTableEmpty,
    runnersGrid,
    runnersEmptyState,
    runnersCountBadge,
    runnersSearchInput,
    runnersOriginFilterGroup,
  } = dom;
  if (tabRunnersCount) tabRunnersCount.textContent = String(runners.length);
  if (runnersCountBadge) runnersCountBadge.textContent = `${runners.length} RUNNING`;

  const allCount = runners.length;
  const countOrigin = (origin: string) =>
    runners.filter((r) => describe(r).origin === origin).length;
  const localCount = countOrigin("local");
  const cloudCount = countOrigin("cloud");
  const extCount = countOrigin("external");

  if (runnersOriginFilterGroup) {
    const allBtn = runnersOriginFilterGroup.querySelector<HTMLButtonElement>('[data-origin="all"]');
    if (allBtn) allBtn.textContent = `All (${allCount})`;
    const localBtn =
      runnersOriginFilterGroup.querySelector<HTMLButtonElement>('[data-origin="local"]');
    if (localBtn) localBtn.textContent = `🖥️ Local (${localCount})`;
    const cloudBtn =
      runnersOriginFilterGroup.querySelector<HTMLButtonElement>('[data-origin="cloud"]');
    if (cloudBtn) cloudBtn.textContent = `☁️ Cloud (${cloudCount})`;
    const extBtn = runnersOriginFilterGroup.querySelector<HTMLButtonElement>(
      '[data-origin="external"]',
    );
    if (extBtn) extBtn.textContent = `🌐 External (${extCount})`;
  }

  const runnersFilter = normalizeFilter(runnersSearchInput?.value || "");
  const filteredRunners = runners.filter((r) => {
    const matchesText = includesFilter(
      [
        r.name,
        r.id,
        r.target_repo,
        r.backend,
        r.target_arch,
        r.status,
        r.workflow_name,
        r.job_name,
        r.job_id,
        r.run_id,
        r.provider,
        r.provider_instance,
      ],
      runnersFilter,
    );
    const { origin, provider } = describe(r);
    return (
      matchesText &&
      (state.currentRunnersOrigin === "all" || origin === state.currentRunnersOrigin) &&
      (state.currentRunnersProvider === "all" || provider === state.currentRunnersProvider)
    );
  });
  const hasFilteredRunners = filteredRunners.length > 0;
  const hasFilter =
    !!runnersFilter ||
    state.currentRunnersOrigin !== "all" ||
    state.currentRunnersProvider !== "all";

  if (runnersEmptyState) {
    runnersEmptyState.classList.toggle("hidden", hasFilteredRunners);
    const title = runnersEmptyState.querySelector<HTMLElement>(".empty-title");
    const desc = runnersEmptyState.querySelector<HTMLElement>(".empty-desc");
    if (title)
      title.textContent = hasFilter ? "No runners match this filter" : "Fleet is on Standby";
    if (desc) {
      desc.textContent = hasFilter
        ? `Try a different filter. Current query: "${runnersFilter}".`
        : "Zero active runner containers or VMs right now. As soon as a workflow queues, the autoscaler will spawn an ephemeral runner instantaneously.";
    }
  }

  // 1. Render Cards View
  if (runnersGrid) {
    runnersGrid.classList.toggle("hidden", !hasFilteredRunners);
    runnersGrid.innerHTML = filteredRunners
      .map((r) => {
        const d = describe(r);
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
              <div class="runner-badges" style="display: flex; gap: 4px; align-items: center; flex-wrap: wrap;">
                ${badges(d, "padding: 1px 6px; font-size: 10px;")}
                <span class="tag-engine ${d.isVm ? "tag-vm" : "tag-docker"}">${d.engine}</span>
                <span class="tag-arch font-mono">${d.arch}</span>
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
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="runner-duration font-mono">⏱️ ${duration}</span>
                ${actionButtons(r, d, "")}
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  }

  // 2. Render Table View
  const filteredRunnersForTable = [...filteredRunners].sort((a, b) => {
    const da = describe(a);
    const db = describe(b);
    const uptime = (r: RunnerInfo) => (r.created_at ? new Date(r.created_at).getTime() : 0);
    // Each key compares these pairs in turn until one differs.
    const keys: Record<typeof state.runnersSort.key, Array<[string | number, string | number]>> = {
      name: [[a.name || a.id, b.name || b.id]],
      repo: [[a.target_repo || "Standby", b.target_repo || "Standby"]],
      engine: [
        [da.engine, db.engine],
        [da.arch, db.arch],
      ],
      status: [[a.status || "", b.status || ""]],
      workflow: [[a.workflow_name || "", b.workflow_name || ""]],
      progress: [[a.progress_pct ?? 0, b.progress_pct ?? 0]],
      uptime: [[uptime(a), uptime(b)]],
    };
    const diff = keys[state.runnersSort.key].reduce(
      (acc, [av, bv]) => acc || compareValues(av, bv),
      0,
    );
    return state.runnersSort.dir === "asc" ? diff : -diff;
  });

  if (runnersTableEmpty) {
    runnersTableEmpty.classList.toggle("hidden", hasFilteredRunners);
    runnersTableEmpty.textContent = hasFilter
      ? `No runners matching "${runnersFilter}".`
      : "No active runners running.";
  }

  if (runnersTableBody) {
    runnersTableBody.innerHTML = filteredRunnersForTable
      .map((r) => {
        const d = describe(r);
        const duration = formatDuration(r.created_at);

        const runLink = runLinkHtml(r);
        const jobLink = jobLinkHtml(r);
        const progressBlock = progressHtml(r, true);
        const idle = !runLink && !jobLink;

        return `
          <tr>
            <td>
              <div style="display: flex; align-items: center; gap: 4px;">
                ${badges(d, "padding: 1px 4px; font-size: 9px;", " margin-right: 4px;")}
                <span style="font-weight: 700; color: var(--text-main); margin-left: 2px;">${escapeHtml(r.name || r.id)}</span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">${escapeHtml(r.id)}</div>
            </td>
            <td>
              <span style="font-weight: 600;">${escapeHtml(r.target_repo || "Standby")}</span>
            </td>
            <td>
              <span class="tech-chip ${d.isVm ? "purple" : "cyan"} font-mono" style="font-size: 10px;">${d.engine}</span>
              <span class="tech-chip solar font-mono" style="font-size: 10px;">${d.arch}</span>
            </td>
            <td>
              <span class="badge font-mono" style="color: var(--emerald);">${escapeHtml((r.status || "RUNNING").toUpperCase())}</span>
            </td>
            <td>
              ${
                idle
                  ? `<span style="color: var(--text-dim);">Standby / Idle</span>`
                  : `
                <div><span class="link-label">RUN</span> ${runLink}${r.workflow_name ? ` <span style="color: var(--text-muted);">${escapeHtml(r.workflow_name)}</span>` : ""}</div>
                <div><span class="link-label">JOB</span> ${jobLink || "-"}</div>`
              }
            </td>
            <td>${progressBlock || `<span style="color: var(--text-dim);">-</span>`}</td>
            <td>${duration}</td>
            <td style="text-align: right; white-space: nowrap;">
              ${actionButtons(r, d, ' style="margin-right: 4px;"')}
            </td>
          </tr>
        `;
      })
      .join("");
  }

  // Attach stop handlers across both cards and table
  document.querySelectorAll<HTMLButtonElement>(".stop-runner-btn").forEach((btn) => {
    btn.onclick = () => stopRunner(btn);
  });

  // Attach terminal connect handlers across both cards and table
  document.querySelectorAll<HTMLButtonElement>(".terminal-runner-btn").forEach((btn) => {
    btn.onclick = () => openRunnerTerminal(btn);
  });
}
