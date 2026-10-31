import type {
  CacheStats,
  CompletedJob,
  QueuedJob,
  RunnerInfo,
  SystemSettings,
} from "./api/client";

/** Sort direction of a table column. */
export type SortDirection = "asc" | "desc";

/** Active sort column and direction of a table. */
export type SortState<K extends string> = { key: K; dir: SortDirection };

/** Presentation mode of the lists. */
export type ViewMode = "cards" | "table";

/** Identifier of a fleet control tab. */
export type TabName = "runners" | "queue" | "jobs" | "repos";

/** All mutable dashboard state, shared by the render and handler modules. */
export interface DashboardState {
  currentRepos: string[];
  currentRunners: RunnerInfo[];
  currentQueuedJobs: QueuedJob[];
  currentCompletedJobs: CompletedJob[];
  currentRepoPriority: string[];
  currentPausedRepos: Set<string>;
  currentConcurrency: { active: number; max: number; min: number };
  draggedRepo: string | null;
  lastUptimeSeconds: number;
  currentViewMode: ViewMode;
  currentTab: TabName;
  terminalExpanded: boolean;
  totalLogLines: number;
  latestSettings: SystemSettings | null;
  latestCacheStats: CacheStats | null;
  terminalHeightPx: number;
  currentRunnersOrigin: string;
  currentRunnersProvider: string;
  runnersSort: SortState<
    "name" | "repo" | "engine" | "status" | "workflow" | "progress" | "uptime"
  >;
  queueSort: SortState<"position" | "status" | "name" | "run" | "repo" | "progress" | "wait">;
  jobsSort: SortState<"result" | "name" | "analysis" | "duration" | "completed">;
  reposSort: SortState<"rank" | "repo" | "status" | "queued">;
}

/** localStorage keys that persist each tab's search filter. */
export const filterStorageKeys = {
  runners: "runzero_filter_runners",
  queue: "runzero_filter_queue",
  jobs: "runzero_filter_jobs",
  repos: "runzero_filter_repos",
} as const;

/** Builds the initial state, reading persisted preferences from localStorage. */
export function createState(): DashboardState {
  return {
    currentRepos: [],
    currentRunners: [],
    currentQueuedJobs: [],
    currentCompletedJobs: [],
    currentRepoPriority: [],
    currentPausedRepos: new Set<string>(),
    currentConcurrency: { active: 0, max: 3, min: 0 },
    draggedRepo: null,
    lastUptimeSeconds: 0,
    currentViewMode: (localStorage.getItem("runzero_display_mode") as ViewMode) || "cards",
    currentTab: "runners",
    terminalExpanded: false,
    totalLogLines: 0,
    latestSettings: null,
    latestCacheStats: null,
    terminalHeightPx: Number(localStorage.getItem("runzero_terminal_height_px") || "180"),
    currentRunnersOrigin: "all",
    currentRunnersProvider: "all",
    runnersSort: { key: "uptime", dir: "desc" },
    queueSort: { key: "position", dir: "asc" },
    jobsSort: { key: "completed", dir: "desc" },
    reposSort: { key: "rank", dir: "asc" },
  };
}

/** The single shared dashboard state instance. */
export const state: DashboardState = createState();

/** Resets {@link state} in place to freshly created defaults (used by tests and re-bootstraps). */
export function resetState(): void {
  Object.assign(state, createState());
}
