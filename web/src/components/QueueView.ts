import type { QueuedJob } from "../api/client";

function formatDuration(isoTime?: string): string {
  if (!isoTime) return "";
  const created = new Date(isoTime).getTime();
  if (isNaN(created)) return "";
  const now = Date.now();
  const diffSec = Math.max(0, Math.floor((now - created) / 1000));
  const m = Math.floor(diffSec / 60);
  const s = diffSec % 60;
  if (m === 0) return `${s}s`;
  return `${m}m ${s}s`;
}

export class QueueViewComponent {
  private container: HTMLElement;
  private jobs: QueuedJob[] = [];
  private timer: number | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  setJobs(jobs: QueuedJob[]) {
    this.jobs = jobs;
    this.render();
    this.startTicker();
  }

  private startTicker() {
    if (this.timer) clearInterval(this.timer);
    this.timer = window.setInterval(() => {
      this.updateElapsedTimes();
    }, 1000);
  }

  private updateElapsedTimes() {
    const timeElements = this.container.querySelectorAll<HTMLElement>("[data-created-at]");
    timeElements.forEach((el) => {
      const createdAt = el.dataset.createdAt;
      const status = el.dataset.status;
      if (createdAt) {
        const duration = formatDuration(createdAt);
        const prefix = status === "in_progress" ? "running" : "waiting";
        el.textContent = `${prefix} ${duration}`;
      }
    });
  }

  destroy() {
    if (this.timer) clearInterval(this.timer);
  }

  render() {
    if (this.jobs.length === 0) {
      this.container.innerHTML = `
        <section class="glass-panel" style="margin-bottom: 1.5rem; text-align: center; padding: 2.5rem 1rem;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.6;">⚡</div>
          <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.25rem;">Queue is Empty</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem;">No queued or running GitHub Actions jobs across monitored repositories.</p>
        </section>
      `;
      return;
    }

    const jobCards = this.jobs
      .map((job) => {
        const isRunning = job.status === "in_progress";
        const positionBadge = job.queue_position
          ? `<span class="badge mono badge-queued" style="font-size: 0.75rem;">Rank #${job.queue_position}</span>`
          : "";

        const statusBadge = isRunning
          ? `<span class="badge mono badge-running">● IN PROGRESS</span>`
          : `<span class="badge mono badge-queued">○ QUEUED</span>`;

        const reason = job.waiting_reason
          ? `<div style="font-size: 0.8rem; color: var(--accent-amber); margin-top: 0.4rem; display: flex; align-items: center; gap: 0.35rem;">
               <span>⏱</span>
               <span>${job.waiting_reason}</span>
             </div>`
          : "";

        const labels = (job.labels || [])
          .filter((l) => l !== "self-hosted")
          .map((l) => `<span class="badge badge-arch mono" style="font-size: 0.65rem;">${l}</span>`)
          .join(" ");

        return `
          <div class="glass-panel" style="padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.6rem; border-left: 3px solid ${isRunning ? "var(--accent-emerald)" : "var(--accent-amber)"};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
              <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                  ${positionBadge}
                  ${statusBadge}
                  <a href="${job.html_url}" target="_blank" rel="noopener noreferrer" style="font-weight: 700; font-size: 1rem; color: var(--text-main); text-decoration: none; display: flex; align-items: center; gap: 0.35rem;">
                    <span>${job.name}</span>
                    <span style="font-size: 0.75rem; color: var(--text-dim);">↗</span>
                  </a>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.6rem;">
                  <strong class="mono" style="color: var(--text-main);">${job.repo}</strong>
                  <span>•</span>
                  <span>${job.workflow_name || "Workflow"}</span>
                  ${job.head_branch ? `<span>•</span><span class="mono">${job.head_branch}</span>` : ""}
                  ${job.run_attempt && job.run_attempt > 1 ? `<span>•</span><span class="badge mono" style="font-size: 0.65rem;">Attempt ${job.run_attempt}</span>` : ""}
                </div>
              </div>

              <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem;">
                <span class="mono" style="font-size: 0.85rem; font-weight: 600; color: ${isRunning ? "var(--accent-emerald)" : "var(--text-muted)"};" data-created-at="${job.started_at || job.created_at}" data-status="${job.status}">
                  ${isRunning ? "running" : "waiting"} ${formatDuration(job.started_at || job.created_at)}
                </span>
                ${labels ? `<div style="display: flex; gap: 0.3rem;">${labels}</div>` : ""}
              </div>
            </div>
            ${reason}
          </div>
        `;
      })
      .join("");

    this.container.innerHTML = `
      <section style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <h2 style="font-size: 1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">
            Active & Queued Workflow Jobs (${this.jobs.length})
          </h2>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
          ${jobCards}
        </div>
      </section>
    `;
  }
}
