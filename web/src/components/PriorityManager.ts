import { client } from "../api/client";

export class PriorityManagerComponent {
  private container: HTMLElement;
  private priority: string[] = [];
  private paused: Set<string> = new Set();
  private onUpdate?: () => void;

  constructor(container: HTMLElement, onUpdate?: () => void) {
    this.container = container;
    this.onUpdate = onUpdate;
  }

  setState(priority: string[], paused: string[]) {
    this.priority = [...priority];
    this.paused = new Set(paused);
    this.render();
  }

  private async move(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= this.priority.length) return;
    const temp = this.priority[index];
    this.priority[index] = this.priority[target];
    this.priority[target] = temp;
    this.render();
    await this.persist();
  }

  private async togglePause(repo: string) {
    if (this.paused.has(repo)) {
      this.paused.delete(repo);
    } else {
      this.paused.add(repo);
    }
    this.render();
    await this.persist();
  }

  private async persist() {
    try {
      await client.updateRepoPriority(this.priority, Array.from(this.paused));
      this.onUpdate?.();
    } catch (err) {
      console.error("Failed to update repo priority", err);
    }
  }

  render() {
    if (this.priority.length === 0) {
      this.container.innerHTML = "";
      return;
    }

    const rows = this.priority
      .map((repo, idx) => {
        const isPaused = this.paused.has(repo);
        return `
          <div class="glass-panel" style="padding: 0.75rem 1rem; display: flex; justify-content: space-between; align-items: center; background: ${isPaused ? "rgba(255,51,75,0.04)" : "var(--bg-glass)"}; border-left: 3px solid ${isPaused ? "var(--accent-redshift)" : "var(--accent-cyan)"};">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <span class="mono" style="font-size: 0.8rem; font-weight: 700; color: var(--text-dim); width: 20px;">#${idx + 1}</span>
              <strong class="mono" style="font-size: 0.95rem; color: ${isPaused ? "var(--text-muted)" : "var(--text-main)"};">${repo}</strong>
              ${isPaused ? `<span class="badge mono badge-paused">PAUSED</span>` : ""}
            </div>

            <div style="display: flex; align-items: center; gap: 0.4rem;">
              <button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" data-move="${idx}" data-dir="-1" ${idx === 0 ? "disabled" : ""}>▲</button>
              <button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" data-move="${idx}" data-dir="1" ${idx === this.priority.length - 1 ? "disabled" : ""}>▼</button>
              <button class="btn ${isPaused ? "btn-primary" : "btn-danger"}" style="padding: 0.25rem 0.65rem; font-size: 0.75rem;" data-toggle-pause="${repo}">
                ${isPaused ? "Resume" : "Pause"}
              </button>
            </div>
          </div>
        `;
      })
      .join("");

    this.container.innerHTML = `
      <section style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <h2 style="font-size: 1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">
            Repository Priority & Dispatch Order
          </h2>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Higher ranks receive free runner slots first</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          ${rows}
        </div>
      </section>
    `;

    // Event listeners
    this.container.querySelectorAll<HTMLButtonElement>("[data-move]").forEach((btn) => {
      btn.onclick = () => {
        const idx = parseInt(btn.dataset.move || "0", 10);
        const dir = parseInt(btn.dataset.dir || "0", 10) as -1 | 1;
        this.move(idx, dir);
      };
    });

    this.container.querySelectorAll<HTMLButtonElement>("[data-toggle-pause]").forEach((btn) => {
      btn.onclick = () => {
        const repo = btn.dataset.togglePause;
        if (repo) this.togglePause(repo);
      };
    });
  }
}
