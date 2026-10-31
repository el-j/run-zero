import { dom } from "../dom";
import { renderCompletedJobs } from "../render/jobs";
import { renderQueue } from "../render/queue";
import { renderRepos } from "../render/repos";
import { renderRunners } from "../render/runners";
import { updateSortHeaderIndicators, toggleSort } from "../sorting";
import { filterStorageKeys, state } from "../state";
import { initTerminalSplitter, toggleTerminal } from "../terminal";
import { setActiveTab, setViewMode } from "../view";

/** Re-renders the repositories list with the current state. */
function rerenderRepos(): void {
  renderRepos(
    state.currentRepos,
    state.currentQueuedJobs,
    state.currentRepoPriority,
    state.currentPausedRepos,
  );
}

/** Makes sortable table headers toggle their table's sort and re-render every list. */
export function initTableSortingControls(): void {
  document.querySelectorAll<HTMLTableCellElement>("th.sortable-col").forEach((th) => {
    th.addEventListener("click", () => {
      const table = th.dataset.table;
      const key = th.dataset.sortKey;
      if (!table || !key) return;

      if (table === "runners") toggleSort(state.runnersSort, key as typeof state.runnersSort.key);
      if (table === "queue") toggleSort(state.queueSort, key as typeof state.queueSort.key);
      if (table === "jobs") toggleSort(state.jobsSort, key as typeof state.jobsSort.key);
      if (table === "repos") toggleSort(state.reposSort, key as typeof state.reposSort.key);

      renderRunners(state.currentRunners);
      renderQueue(state.currentQueuedJobs, state.currentConcurrency);
      renderCompletedJobs(state.currentCompletedJobs);
      rerenderRepos();
      updateSortHeaderIndicators();
    });
  });
}

/** Wires the fleet tab buttons and the card/table view switchers. */
export function initViewControls(): void {
  const {
    tabBtnRunners,
    tabBtnQueue,
    tabBtnJobs,
    tabBtnRepos,
    viewModeCards,
    viewModeTable,
    selectViewModeSetting,
  } = dom;
  if (tabBtnRunners) tabBtnRunners.onclick = () => setActiveTab("runners");
  if (tabBtnQueue) tabBtnQueue.onclick = () => setActiveTab("queue");
  if (tabBtnJobs) tabBtnJobs.onclick = () => setActiveTab("jobs");
  if (tabBtnRepos) tabBtnRepos.onclick = () => setActiveTab("repos");

  if (viewModeCards) viewModeCards.onclick = () => setViewMode("cards");
  if (viewModeTable) viewModeTable.onclick = () => setViewMode("table");
  if (selectViewModeSetting) {
    selectViewModeSetting.onchange = () => {
      setViewMode(selectViewModeSetting.value as "cards" | "table");
    };
  }
}

/** Wires the terminal expand toggle and splitter. */
export function initTerminalControls(): void {
  const { btnToggleTerminalExpand } = dom;
  if (btnToggleTerminalExpand) {
    btnToggleTerminalExpand.onclick = toggleTerminal;
  }
  initTerminalSplitter();
}

/** Wires the clear-logs button. */
export function initClearLogs(): void {
  const { btnClearLogs, logTerminal } = dom;
  if (btnClearLogs) {
    btnClearLogs.onclick = () => {
      if (logTerminal) logTerminal.innerHTML = "";
    };
  }
}

/** Wires the per-tab search inputs and the runner origin/provider filters; inputs persist to localStorage. */
export function initFilterControls(): void {
  const {
    runnersSearchInput,
    runnersOriginFilterGroup,
    runnersProviderSelect,
    queueSearchInput,
    jobsSearchInput,
    repoSearchInput,
  } = dom;
  if (runnersSearchInput) {
    runnersSearchInput.oninput = () => {
      localStorage.setItem(filterStorageKeys.runners, runnersSearchInput.value);
      renderRunners(state.currentRunners);
    };
  }
  if (runnersOriginFilterGroup) {
    runnersOriginFilterGroup.onclick = (e) => {
      const btn = (e.target as HTMLElement).closest(
        "button[data-origin]",
      ) as HTMLButtonElement | null;
      if (!btn) return;
      runnersOriginFilterGroup
        .querySelectorAll("button")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.currentRunnersOrigin = btn.dataset.origin || "all";
      renderRunners(state.currentRunners);
    };
  }
  if (runnersProviderSelect) {
    runnersProviderSelect.onchange = () => {
      state.currentRunnersProvider = runnersProviderSelect.value;
      renderRunners(state.currentRunners);
    };
  }
  if (queueSearchInput) {
    queueSearchInput.oninput = () => {
      localStorage.setItem(filterStorageKeys.queue, queueSearchInput.value);
      renderQueue(state.currentQueuedJobs, state.currentConcurrency);
    };
  }
  if (jobsSearchInput) {
    jobsSearchInput.oninput = () => {
      localStorage.setItem(filterStorageKeys.jobs, jobsSearchInput.value);
      renderCompletedJobs(state.currentCompletedJobs);
    };
  }
  if (repoSearchInput) {
    repoSearchInput.oninput = () => {
      localStorage.setItem(filterStorageKeys.repos, repoSearchInput.value);
      rerenderRepos();
    };
  }
}
