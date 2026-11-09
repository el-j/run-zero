import { type QueuedJob } from "../api/client";
import { triggerQueueAction } from "../actions";
import { dom } from "../dom";
import {
  compareValues,
  escapeHtml,
  formatDuration,
  includesFilter,
  normalizeFilter,
} from "../format";
import { state } from "../state";

/** The run's GitHub URL. */
const runUrlOf = (j: QueuedJob) =>
  j.run_url || `https://github.com/${j.repo}/actions/runs/${j.run_id}`;

/** When the job started running, or else was queued, in epoch ms (0 when unknown). */
const waitingSince = (j: QueuedJob) => {
  const since = j.started_at || j.created_at;
  return since ? new Date(since).getTime() : 0;
};

/**
 * Renders the queued workflow jobs (cards and table), slot counters and run-control buttons.
 *
 * @param concurrency - Active and maximum runner slots.
 */
export function renderQueue(queuedJobs: QueuedJob[], concurrency: { active: number; max: number }) {
  const {
    tabQueueCount,
    queueTableBody,
    queueTableEmpty,
    queueSlotsBadge,
    queueBusySlots,
    queueMaxSlots,
    queueFreeSlots,
    queueTotalJobs,
    queueSearchInput,
    queueJobsCountTag,
    queueJobsView,
  } = dom;
  if (tabQueueCount) tabQueueCount.textContent = String(queuedJobs.length);
  const queueFilter = normalizeFilter(queueSearchInput?.value || "");
  const filteredQueueJobs = queuedJobs.filter((j) =>
    includesFilter(
      [
        j.name,
        j.workflow_name,
        j.repo,
        j.head_branch,
        j.status,
        j.waiting_reason,
        j.run_id,
        j.labels?.join(" "),
      ],
      queueFilter,
    ),
  );
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

  const hasFilteredJobs = filteredQueueJobs.length > 0;
  if (queueTableEmpty) queueTableEmpty.classList.toggle("hidden", hasFilteredJobs);

  if (!hasFilteredJobs) {
    // With jobs queued, an empty result means the filter matched none of them.
    const filterMiss = queuedJobs.length > 0;
    if (queueJobsView) {
      queueJobsView.innerHTML = filterMiss
        ? `
          <div class="empty-substate empty-queue-clean">
            <div class="clean-check-icon">⌕</div>
            <div class="clean-text font-mono">NO QUEUED JOBS MATCH</div>
            <div class="clean-subtext">Try a different queue filter. Current query: "${escapeHtml(queueFilter)}".</div>
          </div>
        `
        : `
          <div class="empty-substate empty-queue-clean">
            <div class="clean-check-icon">✓</div>
            <div class="clean-text font-mono">ALL WORKFLOW QUEUES ARE CLEAR</div>
            <div class="clean-subtext">Waiting jobs will appear here in real-time as GitHub Actions workflows trigger.</div>
          </div>
        `;
    }
    if (queueTableBody) queueTableBody.innerHTML = "";
    if (queueTableEmpty) {
      queueTableEmpty.textContent = filterMiss
        ? `No queued jobs matching "${queueFilter}".`
        : "Queue is clear — no pending workflow jobs.";
    }
    return;
  }

  // 1. Render Cards View
  if (queueJobsView) {
    queueJobsView.innerHTML = filteredQueueJobs
      .map((j) => {
        const isRunning = j.status === "in_progress";
        const posTag = j.queue_position
          ? `<span class="priority-rank-badge font-mono" style="margin-right: 0.5rem;">Rank #${j.queue_position}</span>`
          : "";
        const statusBadge = isRunning
          ? '<span class="badge badge-pulse" style="font-size: 11px;">RUNNING</span>'
          : '<span class="badge badge-queued font-mono" style="font-size: 11px;">QUEUED</span>';

        const runLink = `<a href="${escapeHtml(runUrlOf(j))}" target="_blank" rel="noopener noreferrer" style="color: var(--solar); text-decoration: none; font-weight: 700;">Run #${j.run_id} ↗</a>`;

        const labels = (j.labels ?? [])
          .filter((l) => l !== "self-hosted")
          .map(
            (l) =>
              `<span class="tech-chip ${l === "arm64" ? "solar" : "cyan"} font-mono" style="font-size: 10px;">${escapeHtml(l.toUpperCase())}</span>`,
          )
          .join(" ");

        let progressBlock = "";
        if (j.progress_pct !== undefined || (j.stages_total ?? 0) > 0) {
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
  const filteredQueueForTable = [...filteredQueueJobs].sort((a, b) => {
    // Each key compares these pairs in turn until one differs.
    const keys: Record<typeof state.queueSort.key, Array<[string | number, string | number]>> = {
      position: [
        [a.queue_position ?? Number.MAX_SAFE_INTEGER, b.queue_position ?? Number.MAX_SAFE_INTEGER],
      ],
      status: [[a.status, b.status]],
      name: [
        [a.name, b.name],
        [a.workflow_name ?? "", b.workflow_name ?? ""],
      ],
      run: [[a.run_id ?? 0, b.run_id ?? 0]],
      repo: [
        [a.repo, b.repo],
        [a.head_branch ?? "", b.head_branch ?? ""],
      ],
      progress: [[a.progress_pct ?? 0, b.progress_pct ?? 0]],
      wait: [[waitingSince(a), waitingSince(b)]],
    };
    const diff = keys[state.queueSort.key].reduce(
      (acc, [av, bv]) => acc || compareValues(av, bv),
      0,
    );
    return state.queueSort.dir === "asc" ? diff : -diff;
  });

  if (queueTableBody) {
    queueTableBody.innerHTML = filteredQueueForTable
      .map((j) => {
        const isRunning = j.status === "in_progress";
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
              <a href="${escapeHtml(runUrlOf(j))}" target="_blank" rel="noopener noreferrer" style="color: var(--solar); font-weight: 700;">
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
    btn.onclick = () => triggerQueueAction(btn);
  });
}
