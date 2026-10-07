import type { components } from "../types/api";

export interface StepInfo {
  number: number;
  name: string;
  status: string;
  conclusion?: string;
}

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

export type FleetState = components["schemas"]["FleetState"] & {
  completed_jobs?: CompletedJob[];
};
export type QueuedJob = components["schemas"]["QueuedJob"];
export type RunnerInfo = components["schemas"]["RunnerInfo"];
export type SystemSettings = components["schemas"]["SystemSettings"];
export type CacheStats = components["schemas"]["CacheStats"];
export type SuccessResponse = components["schemas"]["SuccessResponse"];
export type ErrorResponse = components["schemas"]["ErrorResponse"];

export class RunZeroClient {
  private baseUrl: string;

  constructor(baseUrl: string = "") {
    this.baseUrl = baseUrl;
  }

  async getFleet(): Promise<FleetState> {
    const res = await fetch(`${this.baseUrl}/api/fleet`);
    if (!res.ok) {
      throw new Error(`Failed to fetch fleet state: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

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

  async triggerWorkflowAction(
    repo: string,
    runId: number,
    action: "cancel" | "rerun" | "rerun-failed"
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

  async controlRunner(
    action: "start" | "stop" | "drain" | "pause" | "resume",
    options: { runnerId?: string; repo?: string; arch?: string } = {}
  ): Promise<SuccessResponse> {
    const res = await fetch(`${this.baseUrl}/api/actions/runner`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, runner_id: options.runnerId, repo: options.repo, arch: options.arch }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async getSettings(): Promise<SystemSettings> {
    const res = await fetch(`${this.baseUrl}/api/settings`);
    if (!res.ok) {
      throw new Error(`Failed to fetch settings: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

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

  async getCacheStats(): Promise<CacheStats> {
    const res = await fetch(`${this.baseUrl}/api/cache`);
    if (!res.ok) {
      throw new Error(`Failed to fetch cache stats: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async purgeCache(options: { category?: string; repo?: string; all?: boolean } = {}): Promise<SuccessResponse> {
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

  subscribeSSE(callbacks: {
    onFleet?: (state: FleetState) => void;
    onActivity?: (msg: string) => void;
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

    source.onerror = (e) => {
      callbacks.onError?.(e);
    };

    return () => {
      source.close();
    };
  }
}

export const client = new RunZeroClient();
