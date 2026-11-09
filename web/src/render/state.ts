import { type CompletedJob, type FleetState } from "../api/client";
import { dom } from "../dom";
import { formatReset } from "../format";
import { renderCompletedJobs } from "./jobs";
import { renderQueue } from "./queue";
import { renderRepos } from "./repos";
import { isVmBackend } from "./backend";
import { renderRunners } from "./runners";
import { state } from "../state";

/**
 * Renders the GitHub Actions billing sidebar panel; no-op without billing data.
 */
export function renderBilling(billing?: FleetState["actions_billing"]) {
  const {
    actionsScope,
    actionsIncluded,
    actionsTotalUsed,
    actionsPaidUsed,
    actionsRemaining,
    actionsUpdated,
    actionsStatus,
  } = dom;
  if (!actionsScope || !billing) return;
  const { org, owner } = state.latestSettings ?? {};
  actionsScope.textContent = org ? `ORG:${org}` : owner ? `USER:${owner}` : "--";
  if (actionsIncluded)
    actionsIncluded.textContent = billing.included_minutes
      ? `${billing.included_minutes.toLocaleString()}m`
      : "--";
  if (actionsTotalUsed)
    actionsTotalUsed.textContent =
      billing.total_minutes_used !== undefined
        ? `${billing.total_minutes_used.toLocaleString()}m`
        : "--";
  if (actionsPaidUsed)
    actionsPaidUsed.textContent =
      billing.total_paid_minutes_used !== undefined
        ? `${billing.total_paid_minutes_used.toLocaleString()}m`
        : "--";
  if (actionsRemaining) {
    const rem = (billing.included_minutes || 2000) - (billing.total_minutes_used || 0);
    actionsRemaining.textContent = `${Math.max(0, rem).toLocaleString()}m`;
  }
  if (actionsUpdated) actionsUpdated.textContent = new Date().toLocaleTimeString();
  if (actionsStatus) {
    actionsStatus.textContent = "Live billing synced from GitHub API.";
    actionsStatus.className = "billing-status font-mono ok";
  }
}

/**
 * Renders a full fleet snapshot: stat badges, KPI cards, routing ratio and all sub-views.
 */
export function renderState(snapshot: FleetState) {
  const {
    statRateLimit,
    statRateLimitBar,
    statRateMeta,
    statEngine,
    statVersion,
    kpiActiveRunners,
    kpiMaxRunners,
    kpiRunnersBar,
    kpiMinRunnersText,
    kpiRunnerSizing,
    kpiQueuedJobs,
    kpiQueueBar,
    kpiReposMonitored,
    kpiVmRatio,
    kpiRoutingBar,
    kpiRoutingSub,
    kpiRoutingHealth,
    kpiQueueHealth,
    kpiCacheHealth,
    barDockerJobs,
    barVmJobs,
    cntDockerJobs,
    cntVmJobs,
  } = dom;
  if (!snapshot) return;

  statVersion.textContent = (snapshot as any).version ? `v${(snapshot as any).version}` : "v1.0.0";
  statEngine.textContent = "DOCKER";

  // Rate limits
  const rem = snapshot.rate_limit_remaining ?? null;
  const tot = snapshot.rate_limit_limit ?? null;
  statRateLimit.textContent = rem !== null && tot !== null ? `${rem}/${tot}` : "--/--";
  const ratePct = tot ? Math.min(100, Math.max(0, ((rem ?? 0) / tot) * 100)) : 0;
  statRateLimitBar.style.width = `${ratePct}%`;
  if (ratePct < 20) statRateLimitBar.style.backgroundColor = "var(--crimson)";
  else if (ratePct < 50) statRateLimitBar.style.backgroundColor = "var(--solar)";
  else statRateLimitBar.style.backgroundColor = "var(--emerald)";

  if (statRateMeta && rem !== null && tot) {
    statRateMeta.textContent = `used ${tot - rem} • reset ${formatReset((snapshot as any).rate_limit_reset)} • REST Core`;
  }

  const completedJobs =
    (snapshot as FleetState & { completed_jobs?: CompletedJob[] }).completed_jobs || [];
  state.currentCompletedJobs = completedJobs;
  renderCompletedJobs(completedJobs);

  // Active concurrency
  const activeCount = snapshot.busy_runners ?? 0;
  const maxCount = snapshot.max_runners ?? 3;
  const minCount = state.latestSettings?.min_runners ?? 0;
  state.currentConcurrency = { active: activeCount, max: maxCount, min: minCount };
  if (kpiActiveRunners) kpiActiveRunners.textContent = String(activeCount);
  if (kpiMaxRunners) kpiMaxRunners.textContent = `/ ${maxCount} max`;
  if (kpiMinRunnersText)
    kpiMinRunnersText.textContent = `// ${snapshot.free_slots ?? Math.max(0, maxCount - activeCount)} free · ${minCount} standby target`;
  if (kpiRunnerSizing) {
    const cpus = state.latestSettings?.runner_cpus ?? 3;
    const memory = state.latestSettings?.runner_memory ?? "4g";
    kpiRunnerSizing.textContent = `// ${cpus} CPU · ${memory} each`;
  }

  const runnersPct = Math.min(100, Math.round((activeCount / Math.max(1, maxCount)) * 100));
  if (kpiRunnersBar) kpiRunnersBar.style.width = `${runnersPct}%`;

  // Queued jobs
  const jobs = snapshot.queued_jobs || [];
  state.currentQueuedJobs = jobs;
  if (kpiQueuedJobs) kpiQueuedJobs.textContent = String(jobs.length);
  const queuePct = Math.min(100, jobs.length * 25);
  if (kpiQueueBar) kpiQueueBar.style.width = `${queuePct}%`;
  if (kpiQueueHealth) {
    const freeSlots = snapshot.free_slots ?? Math.max(0, maxCount - activeCount);
    if (jobs.length === 0) {
      kpiQueueHealth.textContent = "// Queue clear";
    } else if (freeSlots > 0) {
      kpiQueueHealth.textContent = `// Draining now · ${freeSlots} slot(s) free`;
    } else {
      kpiQueueHealth.textContent = "// Backlogged · waiting for runner capacity";
    }
  }

  // Monitored repos
  state.currentRepos = snapshot.repo_priority || [];
  if (kpiReposMonitored)
    kpiReposMonitored.textContent = `// Across ${state.currentRepos.length} tracked repo(s)`;
  state.currentRepoPriority = snapshot.repo_priority || [];
  state.currentPausedRepos = new Set(snapshot.paused_repos || []);

  // Hybrid routing ratio
  const totalJobs = jobs.length + activeCount;
  const runners = snapshot.runners || [];
  const vmJobs = runners.filter((r) => isVmBackend(r.backend)).length;
  const dockerJobs = runners.length - vmJobs;
  const vmRatio = Math.round((vmJobs / Math.max(1, totalJobs)) * 100);
  if (kpiVmRatio) kpiVmRatio.textContent = `${vmRatio}%`;
  if (kpiRoutingBar) kpiRoutingBar.style.width = `${vmRatio}%`;
  if (kpiRoutingSub) {
    const routeSummary =
      vmJobs > 0 || dockerJobs > 0
        ? `${vmJobs} VM / ${dockerJobs} container`
        : "Auto-detect DIND & Services";
    kpiRoutingSub.textContent = `// ${routeSummary}`;
  }
  if (kpiRoutingHealth) {
    if (vmJobs === 0 && dockerJobs === 0) {
      kpiRoutingHealth.textContent = "// No active workload yet";
    } else if (vmJobs > 0 && dockerJobs > 0) {
      kpiRoutingHealth.textContent = "// Hybrid routing active";
    } else if (vmJobs > 0) {
      kpiRoutingHealth.textContent = "// VM-heavy workload";
    } else {
      kpiRoutingHealth.textContent = "// Container-only workload";
    }
  }
  if (cntDockerJobs) cntDockerJobs.textContent = String(dockerJobs);
  if (cntVmJobs) cntVmJobs.textContent = String(vmJobs);
  if (barDockerJobs) barDockerJobs.style.width = `${100 - vmRatio}%`;
  if (barVmJobs) barVmJobs.style.width = `${vmRatio}%`;

  if (kpiCacheHealth && !state.latestCacheStats) {
    kpiCacheHealth.textContent = "// Cache stats syncing...";
  }

  // Render subcomponents
  state.currentRunners = runners;
  renderRunners(state.currentRunners);
  renderRepos(
    state.currentRepos,
    state.currentQueuedJobs,
    state.currentRepoPriority,
    state.currentPausedRepos,
  );
  renderQueue(state.currentQueuedJobs, state.currentConcurrency);
  renderBilling(snapshot.actions_billing);
}
