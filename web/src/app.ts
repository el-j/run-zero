import { renderDashboardShell } from "./layout/renderDashboardShell";
import { BuildImagesModal } from "./components/BuildImagesModal";
import { loadCacheStats, loadSettings, refreshState } from "./data";
import { initDom } from "./dom";
import { initHandlers } from "./handlers";
import { hooks } from "./hooks";
import { state } from "./state";
import { loadInitialLogs, startStreams } from "./stream";
import { setConnectionStatus } from "./ui";
import { restoreTabFilters, setActiveTab, setViewMode } from "./view";

/** Renders the shell, binds handlers, performs the initial data loads and starts live updates. */
export async function startApp(): Promise<void> {
  renderDashboardShell();
  initDom();
  hooks.refreshState = refreshState;
  hooks.loadCacheStats = loadCacheStats;

  restoreTabFilters();
  initHandlers();
  setViewMode(state.currentViewMode);
  setActiveTab(state.currentTab);
  setConnectionStatus("connecting", "CONNECTING...");

  // Initial loads
  await refreshState();
  loadSettings();
  loadCacheStats();

  await loadInitialLogs();

  // Infrastructure Images Modal
  const imagesModal = new BuildImagesModal();
  startStreams(imagesModal);
}
