import { client, type RunnerInfo } from "../api/client";

export class RunnerFleetComponent {
  private container: HTMLElement;
  private runners: RunnerInfo[] = [];
  private autoscalerStatus: string = "running";
  private showSpawnForm: boolean = false;
  private statusMessage: string = "";

  constructor(container: HTMLElement) {
    this.container = container;
  }

  setRunners(runners: RunnerInfo[], autoscalerStatus: string = "running") {
    this.runners = runners;
    this.autoscalerStatus = autoscalerStatus;
    this.render();
  }

  private async handleStopRunner(runnerId: string, name: string, jobId?: number) {
    const warning = jobId
      ? `Runner '${name}' is actively executing Job #${jobId}. Stopping it will cause the CI job to fail.\n\nAre you sure you want to stop this runner?`
      : `Are you sure you want to stop and remove runner '${name}'?`;

    if (!confirm(warning)) {
      return;
    }

    try {
      this.statusMessage = `Stopping runner ${name}...`;
      this.render();
      await client.controlRunner("stop", { runnerId });
      this.statusMessage = `✓ Stopped runner ${name}`;
    } catch (err) {
      this.statusMessage = `✗ Failed stopping runner: ${(err as Error).message}`;
    }
    this.render();
    setTimeout(() => {
      this.statusMessage = "";
      this.render();
    }, 4000);
  }

  private async handleToggleSpawning() {
    const isPaused = this.autoscalerStatus === "paused";
    const nextAction = isPaused ? "resume" : "pause";
    try {
      this.statusMessage = `${isPaused ? "Resuming" : "Pausing"} autoscaler spawning...`;
      this.render();
      await client.controlRunner(nextAction);
      this.autoscalerStatus = isPaused ? "running" : "paused";
      this.statusMessage = `✓ Autoscaler ${isPaused ? "resumed" : "paused"}`;
    } catch (err) {
      this.statusMessage = `✗ Action failed: ${(err as Error).message}`;
    }
    this.render();
    setTimeout(() => {
      this.statusMessage = "";
      this.render();
    }, 4000);
  }

  private async handleManualSpawn(repo: string, arch: string) {
    if (!repo.trim()) {
      alert("Please provide a repository (e.g. org/repo).");
      return;
    }
    try {
      this.statusMessage = `Spawning manual runner for ${repo} (${arch})...`;
      this.showSpawnForm = false;
      this.render();
      await client.controlRunner("start", { repo: repo.trim(), arch });
      this.statusMessage = `✓ Spawned runner for ${repo}`;
    } catch (err) {
      this.statusMessage = `✗ Spawn failed: ${(err as Error).message}`;
    }
    this.render();
    setTimeout(() => {
      this.statusMessage = "";
      this.render();
    }, 4000);
  }

  render() {
    const isPaused = this.autoscalerStatus === "paused";

    const spawnCard = this.showSpawnForm
      ? `
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1rem; border-left: 3px solid var(--accent-cyan); display: flex; flex-direction: column; gap: 0.75rem;">
          <h4 style="font-size: 0.95rem; font-weight: 700;">Manual Runner Dispatch</h4>
          <p style="font-size: 0.85rem; color: var(--text-muted);">Launch an ephemeral runner immediately for a target repository, bypassing the queue scan.</p>
          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center;">
            <input type="text" id="manual-repo-input" placeholder="Repository (e.g. owner/repo)" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle); flex: 1; min-width: 220px;" />
            <select id="manual-arch-select" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);">
              <option value="arm64">arm64 (Apple Silicon / ARM)</option>
              <option value="amd64">amd64 (Intel / x86_64)</option>
            </select>
            <button id="manual-spawn-submit" class="btn btn-primary" style="padding: 0.5rem 1.25rem;">Launch Runner</button>
            <button id="manual-spawn-cancel" class="btn btn-secondary" style="padding: 0.5rem 0.75rem;">Cancel</button>
          </div>
        </div>
      `
      : "";

    const runnerCards = this.runners.length === 0
      ? `<div class="glass-panel" style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No active ephemeral runners.</div>`
      : this.runners
          .map((runner) => {
            const isVM = runner.backend.includes("vm") || runner.backend.includes("orb");
            return `
              <div class="glass-panel" style="padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; border-left: 3px solid ${isVM ? "var(--accent-cyan)" : "var(--accent-emerald)"};">
                <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                  <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
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
                <button class="btn btn-secondary stop-runner-btn" data-runner-id="${runner.id}" data-runner-name="${runner.name}" data-job-id="${runner.job_id || ""}" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; border-color: rgba(244,63,94,0.4); color: var(--accent-rose);">
                  ⏹ Stop Runner
                </button>
              </div>
            `;
          })
          .join("");

    this.container.innerHTML = `
      <section style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <h2 style="font-size: 1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">
              Active Runner Fleet (${this.runners.length})
            </h2>
            ${this.statusMessage ? `<span class="mono" style="font-size: 0.85rem; font-weight: 600; color: var(--accent-cyan);">${this.statusMessage}</span>` : ""}
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <button id="toggle-spawning-btn" class="btn btn-secondary" style="font-size: 0.8rem; padding: 0.35rem 0.8rem; border-color: ${isPaused ? "var(--accent-emerald)" : "var(--accent-amber)"}; color: ${isPaused ? "var(--accent-emerald)" : "var(--accent-amber)"};">
              ${isPaused ? "▶ Resume Spawning" : "⏸ Pause Spawning"}
            </button>
            <button id="open-spawn-form-btn" class="btn btn-primary" style="font-size: 0.8rem; padding: 0.35rem 0.8rem;">
              + Start Runner Now
            </button>
          </div>
        </div>
        ${spawnCard}
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          ${runnerCards}
        </div>
      </section>
    `;

    const toggleBtn = this.container.querySelector<HTMLButtonElement>("#toggle-spawning-btn");
    if (toggleBtn) {
      toggleBtn.onclick = () => this.handleToggleSpawning();
    }

    const openSpawnBtn = this.container.querySelector<HTMLButtonElement>("#open-spawn-form-btn");
    if (openSpawnBtn) {
      openSpawnBtn.onclick = () => {
        this.showSpawnForm = !this.showSpawnForm;
        this.render();
      };
    }

    const cancelSpawnBtn = this.container.querySelector<HTMLButtonElement>("#manual-spawn-cancel");
    if (cancelSpawnBtn) {
      cancelSpawnBtn.onclick = () => {
        this.showSpawnForm = false;
        this.render();
      };
    }

    const submitSpawnBtn = this.container.querySelector<HTMLButtonElement>("#manual-spawn-submit");
    if (submitSpawnBtn) {
      submitSpawnBtn.onclick = () => {
        const repoInput = this.container.querySelector<HTMLInputElement>("#manual-repo-input");
        const archSelect = this.container.querySelector<HTMLSelectElement>("#manual-arch-select");
        if (repoInput && archSelect) {
          this.handleManualSpawn(repoInput.value, archSelect.value);
        }
      };
    }

    this.container.querySelectorAll<HTMLButtonElement>(".stop-runner-btn").forEach((btn) => {
      btn.onclick = () => {
        const id = btn.dataset.runnerId!;
        const name = btn.dataset.runnerName!;
        const jobId = btn.dataset.jobId ? parseInt(btn.dataset.jobId, 10) : undefined;
        this.handleStopRunner(id, name, jobId);
      };
    });
  }
}
