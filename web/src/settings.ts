import { client, type SystemSettings } from "./api/client";
import { loadSettings, refreshState } from "./data";
import { dom } from "./dom";
import { showToast } from "./ui";

/**
 * Loads the settings into the form inputs and opens the settings dialog.
 */
export async function openSettingsModal() {
  const { settingsModal, inputMaxRunners, inputMinRunners, inputRunnerCpus, inputRunnerMemory, selectRunnerBackend, selectRunnerArch, checkboxAutoRouteVm, selectNativeOverride, inputPollInterval, inputDiscoveryInterval, checkboxCacheEnabled, checkboxProxiesEnabled, inputCacheDir } = dom;
  if (!settingsModal) return;
  showToast("Loading configuration...");
  try {
    const s = await client.getSettings();
    if (inputMaxRunners) inputMaxRunners.value = String(s.max_runners ?? 3);
    if (inputMinRunners) inputMinRunners.value = String(s.min_runners ?? 0);
    if (inputRunnerCpus) inputRunnerCpus.value = String(s.runner_cpus ?? 2);
    if (inputRunnerMemory) inputRunnerMemory.value = s.runner_memory || "4G";
    if (selectRunnerBackend) selectRunnerBackend.value = s.runner_backend || "auto";
    if (selectRunnerArch) selectRunnerArch.value = s.runner_arch || "both";
    if (checkboxAutoRouteVm) checkboxAutoRouteVm.checked = Boolean(s.auto_route_vm);
    if (selectNativeOverride) selectNativeOverride.value = s.native_arch_override || "off";
    if (inputPollInterval) inputPollInterval.value = String(s.poll_interval ?? 10);
    if (inputDiscoveryInterval) inputDiscoveryInterval.value = String(s.discovery_interval ?? 300);
    if (checkboxCacheEnabled) checkboxCacheEnabled.checked = Boolean(s.cache_enabled);
    if (checkboxProxiesEnabled) checkboxProxiesEnabled.checked = Boolean(s.proxies_enabled);
    if (inputCacheDir) inputCacheDir.value = s.host_cache_dir || "";
    settingsModal.showModal();
  } catch (err) {
    showToast(`Failed to load settings: ${(err as Error).message}`, true);
  }
}

/**
 * Submits the settings form to the API, then refreshes settings and fleet state.
 */
export async function saveSettings() {
  const { settingsModal, inputMaxRunners, inputMinRunners, inputRunnerCpus, inputRunnerMemory, selectRunnerBackend, selectRunnerArch, checkboxAutoRouteVm, selectNativeOverride, inputPollInterval, inputDiscoveryInterval, checkboxCacheEnabled, checkboxProxiesEnabled, inputCacheDir } = dom;
  if (!settingsModal) return;
  if (!inputMaxRunners || !inputMinRunners) return;

  const payload: SystemSettings = {
    max_runners: parseInt(inputMaxRunners.value, 10),
    min_runners: parseInt(inputMinRunners.value, 10),
    runner_cpus: inputRunnerCpus ? parseInt(inputRunnerCpus.value, 10) : undefined,
    runner_memory: inputRunnerMemory ? inputRunnerMemory.value.trim() : undefined,
    runner_backend: selectRunnerBackend ? selectRunnerBackend.value : undefined,
    runner_arch: selectRunnerArch ? selectRunnerArch.value : undefined,
    auto_route_vm: checkboxAutoRouteVm ? checkboxAutoRouteVm.checked : undefined,
    native_arch_override: selectNativeOverride ? selectNativeOverride.value : undefined,
    poll_interval: inputPollInterval ? parseInt(inputPollInterval.value, 10) : undefined,
    discovery_interval: inputDiscoveryInterval
      ? parseInt(inputDiscoveryInterval.value, 10)
      : undefined,
    cache_enabled: checkboxCacheEnabled ? checkboxCacheEnabled.checked : undefined,
    proxies_enabled: checkboxProxiesEnabled ? checkboxProxiesEnabled.checked : undefined,
    host_cache_dir: inputCacheDir ? inputCacheDir.value.trim() : undefined,
  };

  showToast("Applying configuration update...");
  try {
    await client.updateSettings(payload);
    settingsModal.close();
    showToast("✓ Settings updated successfully (.env updated)");
    loadSettings();
    refreshState();
  } catch (err) {
    showToast(`Failed to save settings: ${(err as Error).message}`, true);
  }
}
