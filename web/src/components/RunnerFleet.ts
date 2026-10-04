import type { RunnerInfo } from "../api/client";

export class RunnerFleetComponent {
  private container: HTMLElement;
  private runners: RunnerInfo[] = [];

  constructor(container: HTMLElement) {
    this.container = container;
  }

  setRunners(runners: RunnerInfo[]) {
    this.runners = runners;
    this.render();
  }

  render() {
    if (this.runners.length === 0) {
      this.container.innerHTML = "";
      return;
    }

    const cards = this.runners
      .map((runner) => {
        const isVM = runner.backend.includes("vm") || runner.backend.includes("orb");
        return `
          <div class="glass-panel" style="padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; border-left: 3px solid ${isVM ? "var(--accent-cyan)" : "var(--accent-emerald)"};">
            <div style="display: flex; flex-direction: column; gap: 0.25rem;">
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="badge mono badge-running">RUNNING</span>
                <strong class="mono" style="font-size: 0.95rem;">${runner.name}</strong>
                <span class="badge mono badge-arch">${runner.target_arch}</span>
                <span class="badge mono" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">${runner.backend}</span>
              </div>
              <div style="font-size: 0.85rem; color: var(--text-muted);">
                <span>Target: </span><strong class="mono" style="color: var(--text-main);">${runner.target_repo}</strong>
                ${runner.job_id ? ` • <a href="${runner.job_url || "#"}" target="_blank" class="mono" style="color: var(--accent-cyan); text-decoration: none;">Job #${runner.job_id} ↗</a>` : " • Standby"}
              </div>
            </div>
          </div>
        `;
      })
      .join("");

    this.container.innerHTML = `
      <section style="margin-bottom: 2rem;">
        <h2 style="font-size: 1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 0.75rem;">
          Active Runner Fleet (${this.runners.length})
        </h2>
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          ${cards}
        </div>
      </section>
    `;
  }
}
