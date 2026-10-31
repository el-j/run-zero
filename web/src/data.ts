import { client, type CacheStats } from "./api/client";
import { dom } from "./dom";
import { renderState } from "./render/state";
import { state } from "./state";
import { setConnectionStatus } from "./ui";

/**
 * Fetches cache statistics and renders the KPI, health text and per-category bars.
 */
export async function loadCacheStats() {
  const { kpiCacheSize, kpiCacheBar, kpiCacheHealth } = dom;
  try {
    const data: CacheStats = await client.getCacheStats();
    state.latestCacheStats = data;
    if (kpiCacheSize) kpiCacheSize.textContent = data.total_human || "0 B";
    if (kpiCacheBar) {
      const fiftyGiB = 50 * 1024 * 1024 * 1024;
      const fill = Math.max(4, Math.min(100, Math.round((data.total_bytes / fiftyGiB) * 100)));
      kpiCacheBar.style.width = `${fill}%`;
    }
    if (kpiCacheHealth) {
      const bytes = data.total_bytes || 0;
      const oneGiB = 1024 * 1024 * 1024;
      if (bytes === 0) {
        kpiCacheHealth.textContent = "// Cache idle";
      } else if (bytes < 5 * oneGiB) {
        kpiCacheHealth.textContent = "// Cache warm · low pressure";
      } else if (bytes < 20 * oneGiB) {
        kpiCacheHealth.textContent = "// Cache active · healthy";
      } else {
        kpiCacheHealth.textContent = "// Cache heavy · consider prune";
      }
    }

    const maxBytes = Math.max(1, ...data.categories.map((c) => c.bytes));
    data.categories.forEach((cat) => {
      const idKey = cat.category.toLowerCase().replace(/[^a-z0-9]/g, "-");
      const sizeEl = document.getElementById(`sz-${idKey}`);
      const barEl = document.getElementById(`bar-cache-${idKey}`);
      if (sizeEl) sizeEl.textContent = cat.human_readable;
      if (barEl) {
        const pct = Math.max(5, Math.min(100, Math.round((cat.bytes / maxBytes) * 100)));
        barEl.style.width = `${pct}%`;
      }
    });
  } catch (err) {
    console.warn("Could not refresh cache stats:", err);
  }
}

/**
 * Loads system settings into the state and the settings summary.
 *
 * @returns The settings, or null when loading failed.
 */
export async function loadSettings() {
  const { cfgMaxRunners, cfgMinRunners, cfgRunnerBackend, cfgAutoRouteVm, cfgCacheEnabled } = dom;
  try {
    const s = await client.getSettings();
    state.latestSettings = s;
    if (cfgMaxRunners) cfgMaxRunners.textContent = String(s.max_runners ?? 3);
    if (cfgMinRunners) cfgMinRunners.textContent = String(s.min_runners ?? 0);
    if (cfgRunnerBackend) cfgRunnerBackend.textContent = s.runner_backend ?? "auto";
    if (cfgAutoRouteVm) cfgAutoRouteVm.textContent = s.auto_route_vm ? "enabled" : "disabled";
    if (cfgCacheEnabled) cfgCacheEnabled.textContent = s.cache_enabled ? "active" : "disabled";
    return s;
  } catch (err) {
    console.warn("Could not load settings:", err);
    return null;
  }
}

/**
 * Polls the fleet state, updating the connection badge and rendering the snapshot.
 */
export async function refreshState() {
  try {
    const st = await client.getFleet();
    setConnectionStatus("online", "LIVE OBSERVABILITY");
    renderState(st);
  } catch (err) {
    setConnectionStatus("error", "RECONNECTING...");
    console.warn("Poll state warning:", err);
  }
}
