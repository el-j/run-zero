import { client, type SystemSettings } from "../api/client";

export class SettingsPanelComponent {
  private container: HTMLElement;
  private settings?: SystemSettings;
  private loading = false;
  private statusMessage = "";

  constructor(container: HTMLElement) {
    this.container = container;
  }

  async load() {
    this.loading = true;
    this.render();
    try {
      this.settings = await client.getSettings();
    } catch (err) {
      this.statusMessage = `Failed to load settings: ${(err as Error).message}`;
    } finally {
      this.loading = false;
      this.render();
    }
  }

  private async save(formData: FormData) {
    const payload: SystemSettings = {
      max_runners: parseInt(formData.get("max_runners") as string, 10),
      min_runners: parseInt(formData.get("min_runners") as string, 10),
      runner_cpus: parseInt(formData.get("runner_cpus") as string, 10),
      runner_memory: formData.get("runner_memory") as string,
      runner_backend: formData.get("runner_backend") as string,
      auto_route_vm: formData.get("auto_route_vm") === "on",
      runner_arch: formData.get("runner_arch") as string,
      native_arch_override: formData.get("native_arch_override") as string,
      poll_interval: parseInt(formData.get("poll_interval") as string, 10),
      discovery_interval: parseInt(formData.get("discovery_interval") as string, 10),
      cache_enabled: formData.get("cache_enabled") === "on",
      proxies_enabled: formData.get("proxies_enabled") === "on",
      host_cache_dir: formData.get("host_cache_dir") as string,
    };

    const token = formData.get("access_token") as string;
    if (token && token.trim()) {
      payload.access_token = token.trim();
    }

    try {
      this.statusMessage = "Applying settings live...";
      this.render();
      await client.updateSettings(payload);
      this.statusMessage = "✓ Settings applied live (and persisted to .env)";
      await this.load();
    } catch (err) {
      this.statusMessage = `✗ Error saving settings: ${(err as Error).message}`;
      this.render();
    }
  }

  render() {
    if (this.loading) {
      this.container.innerHTML = `
        <div class="glass-panel" style="padding: 2rem; text-align: center;">
          <p style="color: var(--text-muted);">Loading runtime settings...</p>
        </div>
      `;
      return;
    }

    const s = this.settings || {};

    this.container.innerHTML = `
      <section class="glass-panel" style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <div>
            <h2 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 0.25rem;">Live Runtime Configuration</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Modify daemon settings dynamically without restarting the autoscaler.</p>
          </div>
          ${this.statusMessage ? `<span class="mono" style="font-size: 0.85rem; font-weight: 600; color: ${this.statusMessage.startsWith("✓") ? "var(--accent-emerald)" : "var(--accent-amber)"};">${this.statusMessage}</span>` : ""}
        </div>

        <form id="settings-form" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem;">
          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">MAX RUNNERS</label>
            <input type="number" name="max_runners" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.max_runners ?? 3}" min="1" max="64" required />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">STANDBY RUNNERS (MIN)</label>
            <input type="number" name="min_runners" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.min_runners ?? 0}" min="0" max="16" required />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">CPUS PER RUNNER</label>
            <input type="number" name="runner_cpus" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.runner_cpus ?? 3}" min="1" max="32" required />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">MEMORY PER RUNNER</label>
            <input type="text" name="runner_memory" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.runner_memory || "4G"}" required />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">RUNNER BACKEND</label>
            <select name="runner_backend" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);">
              <option value="auto" ${s.runner_backend === "auto" ? "selected" : ""}>auto (Docker + Hybrid VM)</option>
              <option value="docker" ${s.runner_backend === "docker" ? "selected" : ""}>docker (Containers only)</option>
              <option value="orbstack-vm" ${s.runner_backend === "orbstack-vm" ? "selected" : ""}>orbstack-vm (Native macOS Linux VM)</option>
              <option value="wsl2" ${s.runner_backend === "wsl2" ? "selected" : ""}>wsl2 (Windows WSL2 VM)</option>
              <option value="multipass" ${s.runner_backend === "multipass" ? "selected" : ""}>multipass (Canonical Multipass VM)</option>
            </select>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">TARGET ARCHITECTURE</label>
            <select name="runner_arch" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);">
              <option value="both" ${s.runner_arch === "both" ? "selected" : ""}>both (arm64 & amd64)</option>
              <option value="arm64" ${s.runner_arch === "arm64" ? "selected" : ""}>arm64 (Native Apple Silicon)</option>
              <option value="amd64" ${s.runner_arch === "amd64" ? "selected" : ""}>amd64 (Intel/AMD)</option>
            </select>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">NATIVE ARCH OVERRIDE</label>
            <input type="text" name="native_arch_override" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.native_arch_override || "off"}" />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">POLL INTERVAL (SECONDS)</label>
            <input type="number" name="poll_interval" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.poll_interval ?? 10}" min="2" max="300" required />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">DISCOVERY INTERVAL (SECONDS)</label>
            <input type="number" name="discovery_interval" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.discovery_interval ?? 900}" min="30" max="7200" required />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">HOST CACHE DIR</label>
            <input type="text" name="host_cache_dir" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" value="${s.host_cache_dir || ""}" />
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">GITHUB PAT (ROTATE SECRET)</label>
            <input type="password" name="access_token" placeholder="Leave blank to keep current token" class="glass-panel mono" style="padding: 0.5rem; background: var(--bg-surface-elevated); color: var(--text-main); border: 1px solid var(--border-subtle);" />
          </div>

          <div style="display: flex; align-items: center; gap: 1.5rem; padding-top: 1rem;">
            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
              <input type="checkbox" name="auto_route_vm" ${s.auto_route_vm ? "checked" : ""} />
              <span>Hybrid Auto-Route VM</span>
            </label>
            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
              <input type="checkbox" name="cache_enabled" ${s.cache_enabled ? "checked" : ""} />
              <span>Persistent Caching</span>
            </label>
            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
              <input type="checkbox" name="proxies_enabled" ${s.proxies_enabled ? "checked" : ""} />
              <span>Local Registry Proxies</span>
            </label>
          </div>

          <div style="grid-column: 1 / -1; display: flex; justify-content: flex-end; margin-top: 1rem;">
            <button type="submit" class="btn btn-primary" style="padding: 0.6rem 1.5rem; font-size: 0.9rem;">Save & Apply Settings Live</button>
          </div>
        </form>
      </section>
    `;

    const form = this.container.querySelector<HTMLFormElement>("#settings-form");
    if (form) {
      form.onsubmit = (e) => {
        e.preventDefault();
        this.save(new FormData(form));
      };
    }
  }
}
