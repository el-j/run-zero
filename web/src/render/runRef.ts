import { escapeHtml } from "../format";

/**
 * Run/job reference fields shared by runners and queued jobs.
 * A workflow run is a whole execution, a job is one job of that run, and steps are the stages of the job.
 */
export type RunRef = {
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

/**
 * Resolves the GitHub URL of the workflow run, or an empty string when it cannot be derived.
 */
export function runUrlOf(x: RunRef): string {
  const repo = x.target_repo || x.repo;
  return (
    x.run_url || (x.run_id && repo ? `https://github.com/${repo}/actions/runs/${x.run_id}` : "")
  );
}

/**
 * Resolves the GitHub URL of the job, or an empty string when it cannot be derived.
 */
export function jobUrlOf(x: RunRef): string {
  const repo = x.target_repo || x.repo;
  if (x.job_url) return x.job_url;
  return x.run_id && x.job_id && repo
    ? `https://github.com/${repo}/actions/runs/${x.run_id}/job/${x.job_id}`
    : "";
}

/**
 * Builds the workflow run anchor markup, or an empty string without a run URL.
 */
export function runLinkHtml(x: RunRef): string {
  const url = runUrlOf(x);
  return url
    ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="gh-link run-link" title="Open workflow run">Run #${x.run_id ?? ""} ↗</a>`
    : "";
}

/**
 * Builds the job anchor markup, or an empty string without a job URL.
 */
export function jobLinkHtml(x: RunRef): string {
  const url = jobUrlOf(x);
  if (!url) return "";
  const label = x.job_name ? escapeHtml(x.job_name) : `Job #${x.job_id ?? ""}`;
  return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="gh-link job-link" title="Open job">${label} ↗</a>`;
}

/**
 * Maps a step status to its pipeline glyph.
 */
export function stepIcon(status: string): string {
  if (status === "completed") return "✓";
  if (status === "in_progress") return "▶";
  return "○";
}

/**
 * Builds the progress markup for a job: step bar, current stage and, unless compact, the step pipeline.
 *
 * @param compact - Table mode: omit the step pipeline and top margin.
 * @returns An empty string when no progress data exists.
 */
export function progressHtml(x: RunRef, compact: boolean): string {
  const steps = x.steps || [];
  const hasData = x.progress_pct !== undefined || steps.length > 0 || !!x.current_step;
  if (!hasData) return "";
  const pct = x.progress_pct ?? 0;
  const done = x.steps_completed ?? steps.filter((s) => s.status === "completed").length;
  const total = x.steps_total ?? steps.length;
  const stepLabel =
    total > 0
      ? `step ${Math.min(done + 1, total)}/${total}`
      : `${x.stages_done ?? 0}/${x.stages_total ?? 1} jobs`;
  const current = x.current_step
    ? `<div class="current-stage" title="Current stage">▶ ${escapeHtml(x.current_step)}</div>`
    : "";
  const pipeline =
    !compact && steps.length > 0
      ? `<div class="step-pipeline">${steps
          .map(
            (s) =>
              `<span class="step-chip ${escapeHtml(s.status)}" title="${escapeHtml(s.name)}">${stepIcon(s.status)} ${escapeHtml(s.name)}</span>`,
          )
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
