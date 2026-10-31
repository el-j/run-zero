import type { CompletedJob, FleetState, QueuedJob, RunnerInfo } from "../src/api/client";
import { initDom } from "../src/dom";

/** Builds a runner with sensible defaults. */
export function runner(over: Partial<RunnerInfo> = {}): RunnerInfo {
  return {
    id: "r1",
    name: "runner-1",
    status: "running",
    state: "running",
    target_repo: "o/r",
    target_arch: "amd64",
    backend: "docker",
    ...over,
  };
}

/** Builds a queued job with sensible defaults. */
export function queued(over: Partial<QueuedJob> = {}): QueuedJob {
  return {
    id: 1,
    run_id: 100,
    name: "build",
    repo: "o/r",
    html_url: "http://gh/job/1",
    status: "queued",
    labels: ["self-hosted", "linux", "arm64"],
    ...over,
  } as QueuedJob;
}

/** Builds a completed job with sensible defaults. */
export function completed(over: Partial<CompletedJob> = {}): CompletedJob {
  return {
    id: 1,
    run_id: 100,
    name: "test",
    conclusion: "success",
    labels: [],
    html_url: "http://gh/job/1",
    repo: "o/r",
    ...over,
  };
}

/** Builds a fleet snapshot with sensible defaults. */
export function fleet(over: Partial<FleetState> = {}): FleetState {
  return { ...over } as FleetState;
}

/** Empties the document and refreshes the DOM refs so every optional element is null. */
export function removeAllElements(): void {
  document.body.innerHTML = "";
  initDom();
}
