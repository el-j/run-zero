import type { components } from "../types/api";

/** One step of a workflow job. */
export interface StepInfo {
  number: number;
  name: string;
  status: string;
  conclusion?: string;
}

/** A finished workflow job with its outcome and failure details. */
export interface CompletedJob {
  id: number;
  run_id: number;
  name: string;
  workflow_name?: string;
  head_branch?: string;
  run_attempt?: number;
  conclusion: string;
  started_at?: string;
  completed_at?: string;
  duration_sec?: number;
  labels: string[];
  html_url: string;
  run_url?: string;
  repo: string;
  runner_name?: string;
  failed_step?: string;
  failure_reason?: string;
  messages?: string[];
  has_runner_log?: boolean;
  steps?: StepInfo[];
}

/** Fleet snapshot from the API, extended with recently completed jobs. */
export type FleetState = components["schemas"]["FleetState"] & {
  completed_jobs?: CompletedJob[];
};
/** A queued or running workflow job. */
export type QueuedJob = components["schemas"]["QueuedJob"];
/** An active runner. */
export type RunnerInfo = components["schemas"]["RunnerInfo"];
/** Daemon runtime settings. */
export type SystemSettings = components["schemas"]["SystemSettings"];
/** Cache usage statistics. */
export type CacheStats = components["schemas"]["CacheStats"];
/** Generic success response. */
export type SuccessResponse = components["schemas"]["SuccessResponse"];
/** Generic error response. */
export type ErrorResponse = components["schemas"]["ErrorResponse"];
/** Status of one infrastructure image. */
export type InfrastructureImageStatus = components["schemas"]["InfrastructureImageStatus"];
/** Status of all infrastructure images and any active build. */
export type ImagesStatusResponse = components["schemas"]["ImagesStatusResponse"];
/** Progress of an image build. */
export type ImageBuildProgress = components["schemas"]["ImageBuildProgress"];
/** Request body to start an image build. */
export type ImageBuildRequest = components["schemas"]["ImageBuildRequest"];

/** Thin typed wrapper over the dashboard HTTP/SSE API. */
export class RunZeroClient {
  private baseUrl: string;

  /** @param baseUrl - Prefix for all API paths (default: same origin). */
  constructor(baseUrl: string = "") {
    this.baseUrl = baseUrl;
  }

  /** Fetches the current fleet snapshot. @throws On a non-2xx response. */
  async getFleet(): Promise<FleetState> {
    const res = await fetch(`${this.baseUrl}/api/fleet`);
    if (!res.ok) {
      throw new Error(`Failed to fetch fleet state: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  /**
   * Saves repository queue priority and paused repositories.
   *
   * @param priority - Repositories in priority order.
   * @param paused - Repositories to pause.
   * @throws On a non-2xx response.
   */
  async updateRepoPriority(priority: string[], paused: string[]): Promise<SuccessResponse> {
    const res = await fetch(`${this.baseUrl}/api/actions/repo-priority`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ priority, paused }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  /**
   * Cancels or re-runs a workflow run.
   *
   * @param repo - Repository (`owner/repo`).
   * @param runId - Workflow run id.
   * @param action - Action to perform.
   * @throws On a non-2xx response.
   */
  async triggerWorkflowAction(
    repo: string,
    runId: number,
    action: "cancel" | "rerun" | "rerun-failed",
  ): Promise<SuccessResponse> {
    const res = await fetch(`${this.baseUrl}/api/actions/workflow`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo, run_id: runId, action }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  /**
   * Controls runners and the autoscaler (start, stop, drain, pause, resume, open a terminal).
   *
   * @param action - Control action.
   * @param options - Runner id, repository, architecture and backend, as the action requires.
   * @throws On a non-2xx response.
   */
  async controlRunner(
    action: "start" | "stop" | "drain" | "pause" | "resume" | "open-terminal",
    options: { runnerId?: string; repo?: string; arch?: string; backend?: string } = {},
  ): Promise<SuccessResponse & { command?: string; terminal_launched?: boolean }> {
    const res = await fetch(`${this.baseUrl}/api/actions/runner`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action,
        runner_id: options.runnerId,
        repo: options.repo,
        arch: options.arch,
        backend: options.backend,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  /** Fetches runtime settings. @throws On a non-2xx response. */
  async getSettings(): Promise<SystemSettings> {
    const res = await fetch(`${this.baseUrl}/api/settings`);
    if (!res.ok) {
      throw new Error(`Failed to fetch settings: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  /**
   * Applies runtime settings.
   *
   * @param settings - Settings to apply.
   * @throws On a non-2xx response.
   */
  async updateSettings(settings: SystemSettings): Promise<SuccessResponse> {
    const res = await fetch(`${this.baseUrl}/api/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  /** Fetches cache statistics. @throws On a non-2xx response. */
  async getCacheStats(): Promise<CacheStats> {
    const res = await fetch(`${this.baseUrl}/api/cache`);
    if (!res.ok) {
      throw new Error(`Failed to fetch cache stats: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  /**
   * Purges cache entries.
   *
   * @param options - Category, repository or `all` scope of the purge.
   * @throws On a non-2xx response.
   */
  async purgeCache(
    options: { category?: string; repo?: string; all?: boolean } = {},
  ): Promise<SuccessResponse> {
    const res = await fetch(`${this.baseUrl}/api/cache/purge`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  /**
   * Opens the server-sent event stream and dispatches its events.
   *
   * @param callbacks - Handlers for fleet, activity, build progress and error events.
   * @returns Function that closes the stream.
   */
  subscribeSSE(callbacks: {
    onFleet?: (state: FleetState) => void;
    onActivity?: (msg: string) => void;
    onBuildProgress?: (progress: any) => void;
    onError?: (err: Event) => void;
  }): () => void {
    const source = new EventSource(`${this.baseUrl}/api/stream`);

    source.addEventListener("fleet", (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data) as FleetState;
        callbacks.onFleet?.(data);
      } catch (err) {
        console.error("Failed to parse fleet SSE data", err);
      }
    });

    source.addEventListener("activity", (e: MessageEvent) => {
      callbacks.onActivity?.(e.data);
    });

    source.addEventListener("build_progress", (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data);
        callbacks.onBuildProgress?.(data);
      } catch (err) {
        console.error("Failed to parse build_progress SSE data", err);
      }
    });

    source.onerror = (e) => {
      callbacks.onError?.(e);
    };

    return () => {
      source.close();
    };
  }
}

/** Shared API client instance. */
export const client = new RunZeroClient();
