import { launchRunner, pruneFleet, purgeAllCaches, purgeCacheCategory } from "../actions";
import { dom } from "../dom";
import { openSettingsModal, saveSettings } from "../settings";
import { state } from "../state";

/** Wires the prune-fleet and cache purge buttons (global and per category). */
export function initMaintenanceControls(): void {
  const { btnPruneRunners, btnPurgeAllCaches } = dom;
  if (btnPruneRunners) {
    btnPruneRunners.onclick = pruneFleet;
  }
  if (btnPurgeAllCaches) {
    btnPurgeAllCaches.onclick = purgeAllCaches;
  }
  document.querySelectorAll<HTMLButtonElement>("[data-purge-category]").forEach((btn) => {
    btn.onclick = () => purgeCacheCategory(btn);
  });
}

/** Wires the spawn-runner dialog: open (prefilled with the top repository), close/cancel and submit. */
export function initSpawnModal(): void {
  const {
    btnStartRunner,
    spawnModal,
    spawnModalClose,
    spawnModalCancel,
    spawnModalSubmit,
    manualRepoInput,
  } = dom;
  if (btnStartRunner && spawnModal) {
    btnStartRunner.onclick = () => {
      if (manualRepoInput && state.currentRepos.length > 0) {
        manualRepoInput.value = state.currentRepos[0];
      }
      spawnModal.showModal();
    };
  }
  if (spawnModalClose && spawnModal) {
    spawnModalClose.onclick = () => spawnModal.close();
  }
  if (spawnModalCancel && spawnModal) {
    spawnModalCancel.onclick = () => spawnModal.close();
  }
  if (spawnModalSubmit && spawnModal) {
    spawnModalSubmit.onclick = () => launchRunner(spawnModal);
  }
}

/** Wires the settings dialog: open buttons, close/cancel, save button and form submit. */
export function initSettingsModal(): void {
  const {
    btnOpenSettings,
    btnOpenSettingsPanel,
    settingsModal,
    settingsModalClose,
    settingsModalCancel,
    settingsModalSave,
    settingsForm,
  } = dom;
  if (btnOpenSettings) {
    btnOpenSettings.onclick = (e) => {
      e.preventDefault();
      openSettingsModal();
    };
  }
  if (btnOpenSettingsPanel) {
    btnOpenSettingsPanel.onclick = (e) => {
      e.preventDefault();
      openSettingsModal();
    };
  }
  if (settingsModalClose && settingsModal) {
    settingsModalClose.onclick = () => settingsModal.close();
  }
  if (settingsModalCancel && settingsModal) {
    settingsModalCancel.onclick = () => settingsModal.close();
  }
  if (settingsModalSave) {
    settingsModalSave.onclick = (e) => {
      e.preventDefault();
      saveSettings();
    };
  }
  if (settingsForm) {
    settingsForm.onsubmit = (e) => {
      e.preventDefault();
      saveSettings();
    };
  }
}
