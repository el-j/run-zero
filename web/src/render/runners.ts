import { type RunnerInfo } from "../api/client";
import { openRunnerTerminal, stopRunner } from "../actions";
import { dom } from "../dom";
import { compareValues, escapeHtml, formatDuration, includesFilter, normalizeFilter } from "../format";
import { jobLinkHtml, progressHtml, runLinkHtml } from "./runRef";
import { state } from "../state";

/**
 * Renders the runner fleet as cards and table rows (with filters, sorting, GitHub links and progress) and binds the per-runner buttons.
 */
export function renderRunners(runners: RunnerInfo[]) {
  const { tabRunnersCount, runnersTableBody, runnersTableEmpty, runnersGrid, runnersEmptyState, runnersCountBadge, runnersSearchInput, runnersOriginFilterGroup } = dom;
  if (tabRunnersCount) tabRunnersCount.textContent = String(runners.length);
  if (runnersCountBadge) runnersCountBadge.textContent = `${runners.length} RUNNING`;

  const allCount = runners.length;
  const localCount = runners.filter((r) => !r.is_cloud && (r.origin || "local") === "local").length;
  const cloudCount = runners.filter((r) => r.is_cloud || (r.origin || "") === "cloud").length;
  const extCount = runners.filter((r) => !r.is_cloud && (r.origin || "") === "external").length;

  if (runnersOriginFilterGroup) {
    const allBtn = runnersOriginFilterGroup.querySelector<HTMLButtonElement>('[data-origin="all"]');
    if (allBtn) allBtn.textContent = `All (${allCount})`;
    const localBtn = runnersOriginFilterGroup.querySelector<HTMLButtonElement>('[data-origin="local"]');
    if (localBtn) localBtn.textContent = `🖥️ Local (${localCount})`;
    const cloudBtn = runnersOriginFilterGroup.querySelector<HTMLButtonElement>('[data-origin="cloud"]');
    if (cloudBtn) cloudBtn.textContent = `☁️ Cloud (${cloudCount})`;
    const extBtn = runnersOriginFilterGroup.querySelector<HTMLButtonElement>('[data-origin="external"]');
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
    if (!matchesText) return false;

    const origin = r.is_cloud ? "cloud" : (r.origin || "local");
    if (state.currentRunnersOrigin !== "all" && origin !== state.currentRunnersOrigin) {
      return false;
    }

    const prov = (r.provider || "github").toLowerCase();
    if (state.currentRunnersProvider !== "all" && prov !== state.currentRunnersProvider) {
      return false;
    }

    return true;
  });
  const hasRunners = runners.length > 0;
  const hasFilteredRunners = filteredRunners.length > 0;
  const hasFilter = !!runnersFilter || state.currentRunnersOrigin !== "all" || state.currentRunnersProvider !== "all";

  if (runnersEmptyState) {
    if (hasFilteredRunners) runnersEmptyState.classList.add("hidden");
    else runnersEmptyState.classList.remove("hidden");
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
  if (runnersGrid) {
    if (hasFilteredRunners) runnersGrid.classList.remove("hidden");
    else runnersGrid.classList.add("hidden");
  }
  if (runnersTableEmpty) {
    if (hasRunners) runnersTableEmpty.classList.add("hidden");
    else runnersTableEmpty.classList.remove("hidden");
  }

  // 1. Render Cards View
  if (runnersGrid) {
    runnersGrid.innerHTML = filteredRunners
      .map((r) => {
        const isVm =
          (r.backend || "").toLowerCase().includes("vm") ||
          (r.backend || "").toLowerCase().includes("orb");
        const engineTagClass = isVm ? "tag-vm" : "tag-docker";
        const engineName = isVm ? r.backend.toUpperCase() : (r.backend || "DOCKER").toUpperCase();
        const archName = (r.target_arch || "amd64").toUpperCase();
        const repo = r.target_repo || "Standby Pool";
        const duration = formatDuration(r.created_at);

        const isCloud = r.is_cloud || (r.origin || "") === "cloud";
        const isExternal = !isCloud && (r.origin || "") === "external";
        const prov = (r.provider || "github").toLowerCase();
        const provBadge = prov === "gitlab"
          ? `<span class="tag-provider font-mono" style="background: rgba(252, 109, 38, 0.15); color: #fc6d26; border: 1px solid rgba(252, 109, 38, 0.3); border-radius: 4px; padding: 1px 6px; font-size: 10px;">GitLab</span>`
          : `<span class="tag-provider font-mono" style="background: rgba(88, 166, 255, 0.15); color: #58a6ff; border: 1px solid rgba(88, 166, 255, 0.3); border-radius: 4px; padding: 1px 6px; font-size: 10px;">GitHub</span>`;

        const originBadge = isCloud
          ? `<span class="tag-origin font-mono" style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 4px; padding: 1px 6px; font-size: 10px;">☁️ Cloud</span>`
          : isExternal
          ? `<span class="tag-origin font-mono" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 4px; padding: 1px 6px; font-size: 10px;">🌐 External</span>`
          : `<span class="tag-origin font-mono" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 1px 6px; font-size: 10px;">🖥️ Local</span>`;

        const isLocal = !isCloud && !isExternal;
        const actionButtons = isLocal
          ? `
            <button class="btn btn-xs btn-outline terminal-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-backend="${escapeHtml(r.backend || "")}" title="Open terminal directly connected into runner">
              &gt;_ Terminal
            </button>
            <button class="btn btn-xs btn-outline stop-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-job-id="${r.job_id || ""}">
              Stop
            </button>
          `
          : `<span class="badge badge-neutral font-mono" style="font-size: 10px; opacity: 0.8;">Remote Managed</span>`;

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
                ${provBadge}
                ${originBadge}
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
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="runner-duration font-mono">⏱️ ${duration}</span>
                ${actionButtons}
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  }

  // 2. Render Table View
  const sortedRunnersForTable = [...runners].sort((a, b) => {
    const aIsVm =
      (a.backend || "").toLowerCase().includes("vm") ||
      (a.backend || "").toLowerCase().includes("orb");
    const bIsVm =
      (b.backend || "").toLowerCase().includes("vm") ||
      (b.backend || "").toLowerCase().includes("orb");
    const aEngine = aIsVm ? a.backend.toUpperCase() : "DOCKER";
    const bEngine = bIsVm ? b.backend.toUpperCase() : "DOCKER";
    const aProgress = a.progress_pct ?? 0;
    const bProgress = b.progress_pct ?? 0;
    const aUptime = a.created_at ? new Date(a.created_at).getTime() : 0;
    const bUptime = b.created_at ? new Date(b.created_at).getTime() : 0;
    const map: Record<typeof state.runnersSort.key, [string | number, string | number]> = {
      name: [a.name || a.id, b.name || b.id],
      repo: [a.target_repo || "Standby", b.target_repo || "Standby"],
      engine: [`${aEngine}-${a.target_arch || ""}`, `${bEngine}-${b.target_arch || ""}`],
      status: [a.status || "", b.status || ""],
      workflow: [a.workflow_name || "", b.workflow_name || ""],
      progress: [aProgress, bProgress],
      uptime: [aUptime, bUptime],
    };
    const [av, bv] = map[state.runnersSort.key];
    const diff = compareValues(av, bv);
    return state.runnersSort.dir === "asc" ? diff : -diff;
  });
  const filteredRunnerIds = new Set(filteredRunners.map((r) => r.id));
  const filteredRunnersForTable = sortedRunnersForTable.filter((r) => filteredRunnerIds.has(r.id));

  if (runnersTableEmpty) {
    if (state.currentViewMode === "table") {
      runnersTableEmpty.classList.toggle("hidden", filteredRunnersForTable.length > 0);
      runnersTableEmpty.textContent = hasFilter
        ? `No runners matching "${runnersFilter}".`
        : "No active runners running.";
    } else {
      runnersTableEmpty.classList.toggle("hidden", hasFilteredRunners);
    }
  }

  if (runnersTableBody) {
    runnersTableBody.innerHTML = filteredRunnersForTable
      .map((r) => {
        const isVm =
          (r.backend || "").toLowerCase().includes("vm") ||
          (r.backend || "").toLowerCase().includes("orb");
        const engineName = isVm ? r.backend.toUpperCase() : "DOCKER";
        const archName = (r.target_arch || "amd64").toUpperCase();
        const duration = formatDuration(r.created_at);

        const runLink = runLinkHtml(r);
        const jobLink = jobLinkHtml(r);
        const progressBlock = progressHtml(r, true);
        const idle = !runLink && !jobLink;

        const isCloud = r.is_cloud || (r.origin || "") === "cloud";
        const isExternal = !isCloud && (r.origin || "") === "external";
        const isLocal = !isCloud && !isExternal;
        const prov = (r.provider || "github").toLowerCase();
        const provBadge = prov === "gitlab"
          ? `<span class="tag-provider font-mono" style="background: rgba(252, 109, 38, 0.15); color: #fc6d26; border: 1px solid rgba(252, 109, 38, 0.3); border-radius: 4px; padding: 1px 4px; font-size: 9px; margin-right: 4px;">GitLab</span>`
          : `<span class="tag-provider font-mono" style="background: rgba(88, 166, 255, 0.15); color: #58a6ff; border: 1px solid rgba(88, 166, 255, 0.3); border-radius: 4px; padding: 1px 4px; font-size: 9px; margin-right: 4px;">GitHub</span>`;

        const originBadge = isCloud
          ? `<span class="tag-origin font-mono" style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 4px; padding: 1px 4px; font-size: 9px;">☁️ Cloud</span>`
          : isExternal
          ? `<span class="tag-origin font-mono" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 4px; padding: 1px 4px; font-size: 9px;">🌐 External</span>`
          : `<span class="tag-origin font-mono" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 4px; padding: 1px 4px; font-size: 9px;">🖥️ Local</span>`;

        const tableActionButtons = isLocal
          ? `
            <button class="btn btn-xs btn-outline terminal-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-backend="${escapeHtml(r.backend || "")}" style="margin-right: 4px;" title="Open terminal directly connected into runner">
              &gt;_ Terminal
            </button>
            <button class="btn btn-xs btn-outline stop-runner-btn" data-runner-id="${escapeHtml(r.id)}" data-runner-name="${escapeHtml(r.name || r.id)}" data-job-id="${r.job_id || ""}">
              Stop
            </button>
          `
          : `<span class="badge badge-neutral font-mono" style="font-size: 10px; opacity: 0.8;">Remote Managed</span>`;

        return `
          <tr>
            <td>
              <div style="display: flex; align-items: center; gap: 4px;">
                ${provBadge}
                ${originBadge}
                <span style="font-weight: 700; color: var(--text-main); margin-left: 2px;">${escapeHtml(r.name || r.id)}</span>
              </div>
              <div style="font-size: 10px; color: var(--text-dim); margin-top: 2px;">${escapeHtml(r.id)}</div>
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
              ${tableActionButtons}
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
