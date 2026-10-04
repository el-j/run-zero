import type { FleetState } from "../api/client";

export class CapacityMeterComponent {
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  render(state?: FleetState) {
    const busy = state?.busy_runners ?? 0;
    const max = state?.max_runners ?? 3;
    const free = state?.free_slots ?? Math.max(0, max - busy);
    const pct = Math.min(100, Math.round((busy / Math.max(1, max)) * 100));

    this.container.innerHTML = `
      <section class="glass-panel" style="margin-bottom: 1.5rem; display: flex; flex-direction: column; gap: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.6rem;">
            <h2 style="font-size: 1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">Runner Slot Capacity</h2>
            <span class="badge mono ${free > 0 ? "badge-running" : "badge-paused"}">
              ${free} Free Slot${free === 1 ? "" : "s"}
            </span>
          </div>
          <div class="mono" style="font-size: 1rem; font-weight: 700;">
            <span style="color: ${busy >= max ? "var(--accent-redshift)" : "var(--accent-emerald)"};">${busy}</span>
            <span style="color: var(--text-dim);">/</span>
            <span>${max} Active</span>
          </div>
        </div>

        <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; position: relative;">
          <div style="height: 100%; width: ${pct}%; background: linear-gradient(90deg, var(--accent-cyan), ${pct > 80 ? "var(--accent-redshift)" : "var(--accent-emerald)"}); transition: width 0.3s ease;"></div>
        </div>
      </section>
    `;
  }
}
