import { dom } from "../dom";
import { state } from "../state";
import {
  initClearLogs,
  initFilterControls,
  initTableSortingControls,
  initTerminalControls,
  initViewControls,
} from "./controls";
import { initHeaderMenu } from "./headerMenu";
import { initMaintenanceControls, initSettingsModal, initSpawnModal } from "./modals";
import { initTelemetryDrawer } from "./telemetry";

/** Increments the uptime counter once per second and renders it as `HH:MM:SS`. */
export function startUptimeTicker(): void {
  window.setInterval(() => {
    state.lastUptimeSeconds += 1;
    const h = Math.floor(state.lastUptimeSeconds / 3600);
    const m = Math.floor((state.lastUptimeSeconds % 3600) / 60);
    const s = state.lastUptimeSeconds % 60;
    if (dom.statUptime) {
      dom.statUptime.textContent = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    }
  }, 1000);
}

/** Binds every global action and event handler of the dashboard. */
export function initHandlers(): void {
  initTableSortingControls();
  const closeDrawer = initTelemetryDrawer();
  initViewControls();
  initTerminalControls();
  initMaintenanceControls();
  initClearLogs();
  initFilterControls();
  initHeaderMenu(closeDrawer);
  initSpawnModal();
  initSettingsModal();
  startUptimeTicker();
}
