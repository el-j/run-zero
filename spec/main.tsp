import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;

/**
 * RunZero Autoscaler & Cloud-Native CI Control Plane API.
 * Single source of truth for the RunZero fleet management, queue dispatch,
 * workflow execution, fullstack cache control, and live dynamic settings.
 */
@service(#{
  title: "RunZero API"
})
namespace RunZero;

// =============================================================================
// Domain Models
// =============================================================================

/** Information about an ephemeral runner instance */
model RunnerInfo {
  id: string;
  name: string;
  status: string;
  state: string;
  target_repo: string;
  target_arch: string;
  backend: string;
  created_at?: string;
  job_id?: int64;
  run_id?: int64;
  job_url?: string;
  run_url?: string;
}

/** Information about a queued or running workflow job */
model QueuedJob {
  id: int64;
  run_id: int64;
  name: string;
  workflow_name?: string;
  head_branch?: string;
  run_attempt?: int32;
  status: "queued" | "in_progress" | string;
  created_at?: string;
  started_at?: string;
  labels: string[];
  html_url: string;
  repo: string;
  queue_position?: int32 | null;
  waiting_reason?: string;
}

/** GitHub Actions billing summary */
model ActionsBilling {
  included_minutes?: int32;
  total_minutes_used?: int32;
  total_paid_minutes_used?: int32;
}

/** Complete snapshot of the fleet, runner slots, and job queues */
model FleetState {
  runners: RunnerInfo[];
  queued_jobs: QueuedJob[];
  busy_runners: int32;
  max_runners: int32;
  free_slots: int32;
  repo_priority: string[];
  paused_repos: string[];
  rate_limit_remaining?: int32;
  rate_limit_limit?: int32;
  actions_billing?: ActionsBilling;
}

/** Update payload for repository priority ordering and pause states */
model RepoPriorityAction {
  priority: string[];
  paused: string[];
}

/** Workflow run action request (cancel, re-run, or re-run failed) */
model WorkflowActionRequest {
  repo: string;
  run_id: int64;
  action: "cancel" | "rerun" | "rerun-failed";
}

/** Manual runner control action */
model RunnerControlAction {
  runner_id?: string;
  action: "start" | "stop" | "drain" | "pause" | "resume";
  repo?: string;
  arch?: string;
}

/** Live runtime system configuration */
model SystemSettings {
  access_token_configured?: boolean;
  access_token?: string;
  owner?: string;
  org?: string;
  auto_discover?: boolean;
  active_days?: int32;
  runner_backend?: string;
  auto_route_vm?: boolean;
  vm_trigger_labels?: string[];
  docker_network?: string;
  runner_arch?: string;
  min_runners?: int32;
  max_runners?: int32;
  runner_cpus?: int32;
  runner_memory?: string;
  poll_interval?: int32;
  discovery_interval?: int32;
  proxies_enabled?: boolean;
  cache_enabled?: boolean;
  host_cache_dir?: string;
  native_arch_override?: string;
}

/** Storage usage for a specific cache category */
model CacheCategoryUsage {
  category: string;
  bytes: int64;
  human_readable: string;
}

/** Overall cache statistics */
model CacheStats {
  total_bytes: int64;
  total_human: string;
  categories: CacheCategoryUsage[];
}

/** Cache purge request */
model CachePurgeRequest {
  category?: string;
  repo?: string;
  all?: boolean;
}

/** Generic success response */
model SuccessResponse {
  ok: boolean;
  message?: string;
}

/** Generic error response */
@error
model ErrorResponse {
  error: string;
  details?: string;
}

// =============================================================================
// API Operations
// =============================================================================

@route("/api")
namespace Api {
  /** Get current fleet state, active runners, and queued workflow jobs */
  @get
  @route("/fleet")
  op getFleet(): FleetState | ErrorResponse;

  /** Update repository priority order and pause states */
  @post
  @route("/actions/repo-priority")
  op updateRepoPriority(@body payload: RepoPriorityAction): SuccessResponse | ErrorResponse;

  /** Cancel, re-run, or re-run failed workflow runs via GitHub API */
  @post
  @route("/actions/workflow")
  op triggerWorkflowAction(@body payload: WorkflowActionRequest): SuccessResponse | ErrorResponse;

  /** Manual runner controls: stop a runner, spawn an extra runner, or pause dispatch */
  @post
  @route("/actions/runner")
  op controlRunner(@body payload: RunnerControlAction): SuccessResponse | ErrorResponse;

  /** Get live effective system settings and origins */
  @get
  @route("/settings")
  op getSettings(): SystemSettings | ErrorResponse;

  /** Mutate system settings dynamically at runtime without requiring restart */
  @post
  @route("/settings")
  op updateSettings(@body payload: SystemSettings): SuccessResponse | ErrorResponse;

  /** Get multi-tier host and package cache usage statistics */
  @get
  @route("/cache")
  op getCacheStats(): CacheStats | ErrorResponse;

  /** Evict specific cache categories or purge entire host cache */
  @post
  @route("/cache/purge")
  op purgeCache(@body payload: CachePurgeRequest): SuccessResponse | ErrorResponse;
}
