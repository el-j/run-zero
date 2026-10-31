import { dom } from "./dom";
import { updateSortHeaderIndicators } from "./sorting";
import { filterStorageKeys, state } from "./state";

/**
 * Restores each tab's persisted search filter into its input.
 */
export function restoreTabFilters() {
  const { runnersSearchInput, queueSearchInput, jobsSearchInput, repoSearchInput } = dom;
  if (runnersSearchInput)
    runnersSearchInput.value = localStorage.getItem(filterStorageKeys.runners) || "";
  if (queueSearchInput)
    queueSearchInput.value = localStorage.getItem(filterStorageKeys.queue) || "";
  if (jobsSearchInput) jobsSearchInput.value = localStorage.getItem(filterStorageKeys.jobs) || "";
  if (repoSearchInput) repoSearchInput.value = localStorage.getItem(filterStorageKeys.repos) || "";
}

/**
 * Switches between the card and table presentation, persisting the choice and toggling every list's views.
 */
export function setViewMode(mode: "cards" | "table") {
  const { viewModeCards, viewModeTable, selectViewModeSetting, runnersCardsView, runnersTableView, queueCardsView, queueTableView, reposCardsView, reposTableView, jobsCardsView, jobsTableView } = dom;
  state.currentViewMode = mode;
  localStorage.setItem("runzero_display_mode", mode);
  const dashboard = document.querySelector<HTMLElement>(".dashboard-container");
  dashboard?.classList.toggle("view-mode-cards", mode === "cards");
  dashboard?.classList.toggle("view-mode-table", mode === "table");

  if (viewModeCards && viewModeTable) {
    if (mode === "cards") {
      viewModeCards.classList.add("active");
      viewModeTable.classList.remove("active");
    } else {
      viewModeTable.classList.add("active");
      viewModeCards.classList.remove("active");
    }
  }

  if (selectViewModeSetting) {
    selectViewModeSetting.value = mode;
  }

  // Toggle views
  if (runnersCardsView && runnersTableView) {
    if (mode === "cards") {
      runnersCardsView.classList.remove("hidden");
      runnersTableView.classList.add("hidden");
    } else {
      runnersCardsView.classList.add("hidden");
      runnersTableView.classList.remove("hidden");
    }
  }

  if (queueCardsView && queueTableView) {
    if (mode === "cards") {
      queueCardsView.classList.remove("hidden");
      queueTableView.classList.add("hidden");
    } else {
      queueCardsView.classList.add("hidden");
      queueTableView.classList.remove("hidden");
    }
  }

  if (reposCardsView && reposTableView) {
    if (mode === "cards") {
      reposCardsView.classList.remove("hidden");
      reposTableView.classList.add("hidden");
    } else {
      reposCardsView.classList.add("hidden");
      reposTableView.classList.remove("hidden");
    }
  }

  if (jobsCardsView && jobsTableView) {
    if (mode === "cards") {
      jobsCardsView.classList.remove("hidden");
      jobsTableView.classList.add("hidden");
    } else {
      jobsCardsView.classList.add("hidden");
      jobsTableView.classList.remove("hidden");
    }
  }
  updateSortHeaderIndicators();
}

/**
 * Activates one of the fleet control tabs and hides the others.
 */
export function setActiveTab(tab: "runners" | "queue" | "jobs" | "repos") {
  const { tabBtnRunners, tabBtnQueue, tabBtnJobs, tabBtnRepos, tabContentRunners, tabContentQueue, tabContentJobs, tabContentRepos, tabActionsRunners, tabActionsQueue, tabActionsJobs, tabActionsRepos } = dom;
  state.currentTab = tab;

  const tabs = [
    { name: "runners", btn: tabBtnRunners, pane: tabContentRunners, actions: tabActionsRunners },
    { name: "queue", btn: tabBtnQueue, pane: tabContentQueue, actions: tabActionsQueue },
    { name: "jobs", btn: tabBtnJobs, pane: tabContentJobs, actions: tabActionsJobs },
    { name: "repos", btn: tabBtnRepos, pane: tabContentRepos, actions: tabActionsRepos },
  ];

  tabs.forEach((t) => {
    if (t.name === tab) {
      t.btn?.classList.add("active");
      t.pane?.classList.remove("hidden");
      t.actions?.classList.remove("hidden");
    } else {
      t.btn?.classList.remove("active");
      t.pane?.classList.add("hidden");
      t.actions?.classList.add("hidden");
    }
  });
}
