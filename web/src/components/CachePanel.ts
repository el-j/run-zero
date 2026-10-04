import { client, type CacheStats } from "../api/client";

export class CachePanelComponent {
  private container: HTMLElement;
  private stats?: CacheStats;
  private loading = false;
  private statusMessage = "";

  constructor(container: HTMLElement) {
    this.container = container;
  }

  async load() {
    this.loading = true;
    this.render();
    try {
      this.stats = await client.getCacheStats();
    } catch (err) {
      this.statusMessage = `Failed to load cache stats: ${(err as Error).message}`;
    } finally {
      this.loading = false;
      this.render();
    }
  }

  private async purge(category?: string, all?: boolean) {
    const label = all ? "entire host cache" : `category '${category}'`;
    if (!confirm(`Are you sure you want to purge the ${label}?`)) return;

    try {
      this.statusMessage = "Purging cache...";
      this.render();
      await client.purgeCache({ category, all });
      this.statusMessage = `✓ Purged ${label}`;
      await this.load();
    } catch (err) {
      this.statusMessage = `✗ Error purging: ${(err as Error).message}`;
      this.render();
    }
  }

  render() {
    if (this.loading) {
      this.container.innerHTML = `
        <div class="glass-panel" style="padding: 2rem; text-align: center;">
          <p style="color: var(--text-muted);">Loading cache usage statistics...</p>
        </div>
      `;
      return;
    }

    const categories = this.stats?.categories || [
      { category: "hostedtoolcache", bytes: 0, human_readable: "0 MB" },
      { category: "pnpm", bytes: 0, human_readable: "0 MB" },
      { category: "go-build", bytes: 0, human_readable: "0 MB" },
      { category: "playwright", bytes: 0, human_readable: "0 MB" },
      { category: "apt", bytes: 0, human_readable: "0 MB" },
    ];

    const total = this.stats?.total_human || "0 MB";

    const rows = categories
      .map((cat) => `
        <div class="glass-panel" style="padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <strong class="mono" style="font-size: 0.95rem;">${cat.category}</strong>
            <span class="badge mono badge-arch">${cat.human_readable}</span>
          </div>
          <button class="btn btn-danger" style="padding: 0.3rem 0.75rem; font-size: 0.75rem;" data-purge-category="${cat.category}">
            Purge
          </button>
        </div>
      `)
      .join("");

    this.container.innerHTML = `
      <section class="glass-panel" style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <div>
            <h2 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 0.25rem;">Fullstack Multi-Tier Cache Control Plane</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Total Host Cache Usage: <strong class="mono" style="color: var(--accent-cyan);">${total}</strong></p>
          </div>
          <div style="display: flex; align-items: center; gap: 1rem;">
            ${this.statusMessage ? `<span class="mono" style="font-size: 0.85rem; font-weight: 600; color: ${this.statusMessage.startsWith("✓") ? "var(--accent-emerald)" : "var(--accent-amber)"};">${this.statusMessage}</span>` : ""}
            <button class="btn btn-danger" id="purge-all-btn" style="padding: 0.45rem 1rem;">Purge Entire Cache</button>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 0.6rem;">
          ${rows}
        </div>
      </section>
    `;

    this.container.querySelectorAll<HTMLButtonElement>("[data-purge-category]").forEach((btn) => {
      btn.onclick = () => {
        const cat = btn.dataset.purgeCategory;
        if (cat) this.purge(cat, false);
      };
    });

    const purgeAll = this.container.querySelector<HTMLButtonElement>("#purge-all-btn");
    if (purgeAll) {
      purgeAll.onclick = () => this.purge(undefined, true);
    }
  }
}
