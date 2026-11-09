import { type SortState, state } from "./state";

/**
 * Toggles the direction when `key` is already active, otherwise selects `key` ascending.
 */
export function toggleSort<K extends string>(sortState: SortState<K>, key: K) {
  if (sortState.key === key) {
    sortState.dir = sortState.dir === "asc" ? "desc" : "asc";
  } else {
    sortState.key = key;
    sortState.dir = "asc";
  }
}

/**
 * Syncs the `sort-asc` / `sort-desc` classes of sortable table headers with the current sort state.
 */
export function updateSortHeaderIndicators() {
  document.querySelectorAll<HTMLElement>("th.sortable-col").forEach((th) => {
    th.classList.remove("sort-asc", "sort-desc");
    const table = th.dataset.table;
    const key = th.dataset.sortKey;
    const match =
      (table === "runners" && state.runnersSort.key === key && state.runnersSort.dir) ||
      (table === "queue" && state.queueSort.key === key && state.queueSort.dir) ||
      (table === "jobs" && state.jobsSort.key === key && state.jobsSort.dir) ||
      (table === "repos" && state.reposSort.key === key && state.reposSort.dir);

    if (match) th.classList.add(match === "asc" ? "sort-asc" : "sort-desc");
  });
}
