import { type CompletedJob } from "../api/client";
import { retryFailedJobs } from "../actions";
import { dom } from "../dom";
import { compareValues, escapeHtml, includesFilter, normalizeFilter } from "../format";
import { state } from "../state";

/**
 * Renders the completed-job history (cards and table) with filtering, sorting and retry buttons.
 */
export function renderCompletedJobs(jobs: CompletedJob[]) {
  const { tabJobsCount, jobsSearchInput, jobsList, jobsTableBody, jobsTableEmpty } = dom;
  if (tabJobsCount) tabJobsCount.textContent = String(jobs.length);
  const jobsFilter = normalizeFilter(jobsSearchInput?.value || "");
  const filteredJobs = jobs.filter((job) =>
    includesFilter(
      [
        job.name,
        job.repo,
        job.conclusion,
        job.workflow_name,
        job.head_branch,
        job.failure_reason,
        job.failed_step,
        job.run_id,
        job.run_attempt,
      ],
      jobsFilter,
    ),
  );
  const hasFilter = !!jobsFilter;

  if (!jobsList || !jobsTableBody || !jobsTableEmpty) return;

  if (jobs.length === 0 || filteredJobs.length === 0) {
    const noHistory = jobs.length === 0;
    const emptyHtml = `
      <div class="empty-substate empty-queue-clean">
        <div class="clean-check-icon">${noHistory ? "✓" : "⌕"}</div>
        <div class="clean-text font-mono">${noHistory ? "NO COMPLETED JOBS YET" : "NO HISTORY MATCHES FILTER"}</div>
        <div class="clean-subtext">${
          noHistory
            ? "Recent successful and failed GitHub Actions jobs appear here with a quick retry path."
            : `Try a different history filter. Current query: "${escapeHtml(jobsFilter)}".`
        }</div>
      </div>
    `;
    jobsList.innerHTML = emptyHtml;
    jobsTableBody.innerHTML = "";
    if (state.currentViewMode === "table") {
      jobsTableEmpty.classList.remove("hidden");
      jobsTableEmpty.textContent = noHistory
        ? "Recent successful and failed GitHub Actions jobs appear here."
        : `No completed jobs matching "${jobsFilter}".`;
    } else {
      jobsTableEmpty.classList.add("hidden");
    }
    return;
  }
  jobsTableEmpty.classList.add("hidden");

  const sorted = [...filteredJobs].sort((a, b) => {
    const av = a.completed_at ? new Date(a.completed_at).getTime() : 0;
    const bv = b.completed_at ? new Date(b.completed_at).getTime() : 0;
    return bv - av;
  });

  jobsList.innerHTML = sorted
    .map((job) => {
      const conclusion = (job.conclusion || "unknown").toLowerCase();
      const isSuccess = conclusion === "success";
      const headerKind = isSuccess ? "badge-live" : "badge-danger";
      const statusText = isSuccess ? "SUCCESS" : conclusion.toUpperCase();
      const reason = job.failure_reason || job.failed_step || "No failure reason captured.";
      const messages = (job.messages || [])
        .map((msg: string) => `<li>${escapeHtml(msg)}</li>`)
        .join("");
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

  const sortedJobsForTable = [...filteredJobs].sort((a, b) => {
    const aConclusion = (a.conclusion || "unknown").toLowerCase();
    const bConclusion = (b.conclusion || "unknown").toLowerCase();
    const aReason = a.failure_reason || a.failed_step || "No failure reason captured.";
    const bReason = b.failure_reason || b.failed_step || "No failure reason captured.";
    const aDuration = a.duration_sec ?? 0;
    const bDuration = b.duration_sec ?? 0;
    const aCompleted = a.completed_at ? new Date(a.completed_at).getTime() : 0;
    const bCompleted = b.completed_at ? new Date(b.completed_at).getTime() : 0;
    const map: Record<typeof state.jobsSort.key, [string | number, string | number]> = {
      result: [aConclusion, bConclusion],
      name: [`${a.name} ${a.repo}`, `${b.name} ${b.repo}`],
      analysis: [aReason, bReason],
      duration: [aDuration, bDuration],
      completed: [aCompleted, bCompleted],
    };
    const [av, bv] = map[state.jobsSort.key];
    const diff = compareValues(av, bv);
    return state.jobsSort.dir === "asc" ? diff : -diff;
  });
  if (state.currentViewMode === "table") {
    jobsTableEmpty.classList.toggle("hidden", sortedJobsForTable.length > 0);
    jobsTableEmpty.textContent = hasFilter
      ? `No completed jobs matching "${jobsFilter}".`
      : "Recent successful and failed GitHub Actions jobs appear here.";
  }

  jobsTableBody.innerHTML = sortedJobsForTable
    .map((job) => {
      const conclusion = (job.conclusion || "unknown").toLowerCase();
      const isSuccess = conclusion === "success";
      const statusClass = isSuccess ? "jobs-status-success" : "jobs-status-failed";
      const statusText = isSuccess ? "SUCCESS" : conclusion.toUpperCase();
      const reason = job.failure_reason || job.failed_step || "No failure reason captured.";
      const runUrl = job.run_url || `https://github.com/${job.repo}/actions/runs/${job.run_id}`;
      const details = [
        job.workflow_name || "",
        job.head_branch ? `branch: ${job.head_branch}` : "",
        job.run_attempt && job.run_attempt > 1 ? `attempt ${job.run_attempt}` : "",
      ]
        .filter(Boolean)
        .join(" • ");

      return `
        <tr>
          <td><span class="jobs-status-pill ${statusClass} font-mono">${statusText}</span></td>
          <td>
            <div class="jobs-table-job">
              <a href="${escapeHtml(runUrl)}" target="_blank" rel="noopener noreferrer" class="jobs-table-job-link">${escapeHtml(job.name)}</a>
              <div class="jobs-table-repo font-mono">${escapeHtml(job.repo)}</div>
              ${details ? `<div class="jobs-table-meta">${escapeHtml(details)}</div>` : ""}
            </div>
          </td>
          <td>
            <div class="jobs-table-reason" title="${escapeHtml(reason)}">${escapeHtml(reason)}</div>
            ${job.failed_step ? `<div class="jobs-table-step">step: <span class="font-mono">${escapeHtml(job.failed_step)}</span></div>` : ""}
          </td>
          <td class="font-mono">${job.duration_sec !== undefined ? `${job.duration_sec}s` : "—"}</td>
          <td class="font-mono">${job.completed_at ? new Date(job.completed_at).toLocaleString() : "—"}</td>
          <td>
            <div class="jobs-table-actions">
              <a href="${escapeHtml(job.html_url || runUrl)}" target="_blank" rel="noopener noreferrer" class="btn btn-xs btn-outline font-mono jobs-action-btn">
                <span class="jobs-action-icon">↗</span><span class="jobs-action-text">GitHub</span>
              </a>
              ${
                !isSuccess
                  ? `<button class="btn btn-xs btn-outline job-rerun-btn font-mono jobs-action-btn" data-repo="${escapeHtml(job.repo)}" data-run-id="${job.run_id}">
                    <span class="jobs-action-icon">↻</span><span class="jobs-action-text">Retry failed</span>
                  </button>`
                  : ""
              }
            </div>
          </td>
        </tr>
      `;
    })
    .join("");

  document.querySelectorAll<HTMLButtonElement>(".job-rerun-btn").forEach((btn) => {
    btn.onclick = () => retryFailedJobs(btn);
  });
}
