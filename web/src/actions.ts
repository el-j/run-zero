import { client } from "./api/client";
import { dom } from "./dom";
import { hooks } from "./hooks";
import { showToast } from "./ui";

/**
 * Stops a runner after confirmation. Warns when the runner is executing a job.
 *
 * @param btn - Button carrying `data-runner-id`, `data-runner-name` and optional `data-job-id`.
 */
export async function stopRunner(btn: HTMLButtonElement): Promise<void> {
  const runnerId = btn.dataset.runnerId!;
  const runnerName = btn.dataset.runnerName!;
  const jobId = btn.dataset.jobId;
  const warning = jobId
    ? `Runner '${runnerName}' is executing Job #${jobId}. Stopping it will fail the workflow.\n\nStop runner?`
    : `Stop and delete runner '${runnerName}'?`;
  if (!confirm(warning)) return;
  try {
    await client.controlRunner("stop", { runnerId });
    showToast(`Stopped runner ${runnerName}`);
    hooks.refreshState();
  } catch (err) {
    showToast(`Failed stopping runner: ${(err as Error).message}`, true);
  }
}

/**
 * Opens a terminal into a runner, copying the attach command to the clipboard when available.
 * The button is disabled while the request is in flight.
 *
 * @param btn - Button carrying `data-runner-id`, `data-runner-name` and `data-backend`.
 */
export async function openRunnerTerminal(btn: HTMLButtonElement): Promise<void> {
  const runnerId = btn.dataset.runnerId!;
  const runnerName = btn.dataset.runnerName!;
  const backend = btn.dataset.backend!;
  const origText = btn.innerHTML;
  btn.innerHTML = `Launching...`;
  btn.disabled = true;

  try {
    const res = await client.controlRunner("open-terminal", {
      runnerId,
      backend,
    });
    if (res.command) {
      try {
        await navigator.clipboard.writeText(res.command);
      } catch {}
    }
    showToast(
      res.terminal_launched ? `Terminal opened for ${runnerName}!` : `Command copied: ${res.command}`,
    );
  } catch (err) {
    showToast(`Failed opening terminal: ${(err as Error).message}`, true);
  } finally {
    btn.innerHTML = origText;
    btn.disabled = false;
  }
}

/**
 * Retries the failed jobs of a completed run after confirmation.
 *
 * @param btn - Button carrying `data-repo` and `data-run-id`.
 */
export async function retryFailedJobs(btn: HTMLButtonElement): Promise<void> {
  const repo = btn.dataset.repo!;
  const runId = Number(btn.dataset.runId);
  if (!repo || Number.isNaN(runId)) return;
  if (!confirm(`Retry failed jobs for ${repo} run #${runId}?`)) return;
  try {
    const res = await client.triggerWorkflowAction(repo, runId, "rerun-failed");
    showToast(res.message || `Retry queued for ${repo} run #${runId}`);
  } catch (err) {
    showToast(`Failed to retry jobs: ${(err as Error).message}`, true);
  }
}

/**
 * Cancels or re-runs a queued workflow run after confirmation.
 *
 * @param btn - Button carrying `data-repo`, `data-run-id` and `data-action`.
 */
export async function triggerQueueAction(btn: HTMLButtonElement): Promise<void> {
  const repo = btn.dataset.repo!;
  const runId = parseInt(btn.dataset.runId!, 10);
  const action = btn.dataset.action as "cancel" | "rerun" | "rerun-failed";
  if (!confirm(`Are you sure you want to ${action} run #${runId} on ${repo}?`)) return;
  try {
    await client.triggerWorkflowAction(repo, runId, action);
    showToast(`Workflow ${action} triggered`);
    hooks.refreshState();
  } catch (err) {
    showToast(`Action failed: ${(err as Error).message}`, true);
  }
}

/** Asks the daemon to prune idle fleet runners. */
export async function pruneFleet(): Promise<void> {
  try {
    await fetch("/api/actions/prune", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    showToast("Triggered fleet runner prune");
    hooks.refreshState();
  } catch (err) {
    showToast(`Prune failed: ${(err as Error).message}`, true);
  }
}

/** Clears every host package cache after confirmation. */
export async function purgeAllCaches(): Promise<void> {
  if (!confirm("Are you sure you want to clear all host package caches?")) return;
  try {
    await client.purgeCache({ all: true });
    showToast("✓ Cleared all host caches");
    hooks.loadCacheStats();
  } catch (err) {
    showToast(`Purge failed: ${(err as Error).message}`, true);
  }
}

/**
 * Clears a single cache category after confirmation.
 *
 * @param btn - Button carrying `data-purge-category`.
 */
export async function purgeCacheCategory(btn: HTMLButtonElement): Promise<void> {
  const cat = btn.dataset.purgeCategory!;
  if (!confirm(`Purge cache category '${cat}'?`)) return;
  try {
    await client.purgeCache({ category: cat });
    showToast(`✓ Purged ${cat} cache`);
    hooks.loadCacheStats();
  } catch (err) {
    showToast(`Purge error: ${(err as Error).message}`, true);
  }
}

/**
 * Closes the spawn dialog and launches a runner for the entered repository.
 *
 * @param spawnModal - The spawn dialog to close.
 */
export async function launchRunner(spawnModal: HTMLDialogElement): Promise<void> {
  const { manualRepoInput, manualArchSelect } = dom;
  const repo = manualRepoInput ? manualRepoInput.value.trim() : "";
  const arch = manualArchSelect ? manualArchSelect.value : "amd64";
  if (!repo) {
    alert("Please enter a target repository.");
    return;
  }
  spawnModal.close();
  showToast(`Launching runner for ${repo} (${arch})...`);
  try {
    await client.controlRunner("start", { repo, arch });
    showToast(`✓ Runner launched for ${repo}`);
    hooks.refreshState();
  } catch (err) {
    showToast(`Launch failed: ${(err as Error).message}`, true);
  }
}
