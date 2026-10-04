import type { FleetState } from "../api/client";

export class HeaderComponent {
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  render(state?: FleetState, connected: boolean = true) {
    const quotaUsed = state?.rate_limit_limit && state?.rate_limit_remaining !== undefined
      ? `${state.rate_limit_remaining}/${state.rate_limit_limit}`
      : "—";

    const billingMinutes = state?.actions_billing?.total_minutes_used !== undefined
      ? `${state.actions_billing.total_minutes_used}m`
      : "—";

    this.container.innerHTML = `
      <header class="header glass-panel" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 1rem;">
          <div style="display: flex; align-items: center; gap: 0.6rem;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: ${connected ? "var(--accent-emerald)" : "var(--accent-amber)"}; box-shadow: 0 0 10px ${connected ? "rgba(0,230,118,0.5)" : "rgba(255,179,0,0.5)"};"></div>
            <span style="font-weight: 800; font-size: 1.35rem; letter-spacing: -0.02em; background: linear-gradient(135deg, #fff 40%, var(--accent-redshift) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">RUNZERO</span>
            <span class="badge mono" style="font-size: 0.65rem; background: rgba(255,255,255,0.06); color: var(--text-muted); border: 1px solid var(--border-subtle);">CONTROL PLANE</span>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 1.25rem;">
          <div style="display: flex; gap: 1rem; font-size: 0.85rem;">
            <div title="GitHub REST API Rate Limit">
              <span style="color: var(--text-muted);">API Quota:</span>
              <strong class="mono" style="color: var(--accent-cyan); margin-left: 0.3rem;">${quotaUsed}</strong>
            </div>
            <div title="Actions Billing Minutes Used This Month">
              <span style="color: var(--text-muted);">Billing:</span>
              <strong class="mono" style="color: var(--text-main); margin-left: 0.3rem;">${billingMinutes}</strong>
            </div>
          </div>

          <div style="display: flex; gap: 0.5rem;">
            <button id="nav-fleet" class="btn btn-primary" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">Fleet & Queue</button>
            <button id="nav-settings" class="btn" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">Settings</button>
            <button id="nav-cache" class="btn" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">Cache</button>
          </div>
        </div>
      </header>
    `;
  }
}
