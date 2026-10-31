import { beforeEach, describe, expect, it, vi } from "vitest";
import { runner } from "../../test/factories";
import { mountDashboard } from "../../test/helpers";
import { dom, initDom } from "../dom";
import { state } from "../state";
import type { FleetState } from "../api/client";

const sub = vi.hoisted(() => ({
  renderCompletedJobs: vi.fn(),
  renderQueue: vi.fn(),
  renderRepos: vi.fn(),
  renderRunners: vi.fn(),
}));
vi.mock("./jobs", () => ({ renderCompletedJobs: sub.renderCompletedJobs }));
vi.mock("./queue", () => ({ renderQueue: sub.renderQueue }));
vi.mock("./repos", () => ({ renderRepos: sub.renderRepos }));
vi.mock("./runners", () => ({ renderRunners: sub.renderRunners }));

import { renderBilling, renderState } from "./state";

beforeEach(() => {
  mountDashboard();
});

const snap = (over: Record<string, unknown> = {}) => over as unknown as FleetState;

describe("renderBilling", () => {
  it("is a no-op without billing data or scope", () => {
    renderBilling(undefined);
    expect(dom.actionsScope!.textContent).not.toBe("USER:el-j");
    document.getElementById("actions-scope")?.remove();
    initDom();
    renderBilling({ included_minutes: 1 } as FleetState["actions_billing"]);
  });

  it("renders every field", () => {
    renderBilling({
      included_minutes: 3000,
      total_minutes_used: 100,
      total_paid_minutes_used: 5,
    } as FleetState["actions_billing"]);
    expect(dom.actionsScope!.textContent).toBe("USER:el-j");
    expect(dom.actionsIncluded!.textContent).toBe(`${(3000).toLocaleString()}m`);
    expect(dom.actionsTotalUsed!.textContent).toBe("100m");
    expect(dom.actionsPaidUsed!.textContent).toBe("5m");
    expect(dom.actionsRemaining!.textContent).toBe(`${(2900).toLocaleString()}m`);
    expect(dom.actionsUpdated!.textContent).not.toBe("");
    expect(dom.actionsStatus!.className).toContain("ok");
  });

  it("falls back to placeholders and defaults", () => {
    renderBilling({} as FleetState["actions_billing"]);
    expect(dom.actionsIncluded!.textContent).toBe("--");
    expect(dom.actionsTotalUsed!.textContent).toBe("--");
    expect(dom.actionsPaidUsed!.textContent).toBe("--");
    expect(dom.actionsRemaining!.textContent).toBe(`${(2000).toLocaleString()}m`);
  });

  it("works without the optional elements", () => {
    for (const el of document.querySelectorAll("[id^='actions-']")) {
      if (el.id !== "actions-scope") el.remove();
    }
    initDom();
    expect(() => renderBilling({ included_minutes: 1 } as FleetState["actions_billing"])).not.toThrow();
  });
});

describe("renderState", () => {
  it("ignores empty snapshots", () => {
    renderState(null as unknown as FleetState);
    expect(sub.renderRunners).not.toHaveBeenCalled();
  });

  it("renders a busy hybrid fleet", () => {
    state.latestSettings = { min_runners: 1, runner_cpus: 4, runner_memory: "8g" };
    state.latestCacheStats = {} as never;
    renderState(
      snap({
        version: "2.0",
        rate_limit_remaining: 10,
        rate_limit_limit: 100,
        rate_limit_reset: 0,
        busy_runners: 2,
        max_runners: 4,
        free_slots: 2,
        queued_jobs: [{ id: 1 }],
        repo_priority: ["o/a"],
        paused_repos: ["o/a"],
        runners: [runner({ backend: "orbstack" }), runner({ backend: "docker" })],
        completed_jobs: [{ id: 1 }],
        actions_billing: { included_minutes: 10 },
      }),
    );
    expect(dom.statVersion!.textContent).toBe("v2.0");
    expect(dom.statRateLimit!.textContent).toBe("10/100");
    expect(dom.statRateLimitBar!.style.width).toBe("10%");
    expect(dom.statRateMeta!.textContent).toContain("used 90");
    expect(dom.kpiActiveRunners!.textContent).toBe("2");
    expect(dom.kpiMaxRunners!.textContent).toBe("/ 4 max");
    expect(dom.kpiMinRunnersText!.textContent).toContain("2 free · 1 standby target");
    expect(dom.kpiRunnerSizing!.textContent).toBe("// 4 CPU · 8g each");
    expect(dom.kpiRunnersBar!.style.width).toBe("50%");
    expect(dom.kpiQueueBar!.style.width).toBe("25%");
    expect(dom.kpiQueueHealth!.textContent).toContain("Draining now · 2 slot(s) free");
    expect(dom.kpiReposMonitored!.textContent).toContain("1 tracked");
    expect(dom.kpiVmRatio!.textContent).toBe("33%");
    expect(dom.kpiRoutingSub!.textContent).toBe("// 1 VM / 1 container");
    expect(dom.kpiRoutingHealth!.textContent).toBe("// Hybrid routing active");
    expect(dom.cntDockerJobs!.textContent).toBe("1");
    expect(dom.cntVmJobs!.textContent).toBe("1");
    expect(dom.barDockerJobs!.style.width).toBe("67%");
    expect(dom.barVmJobs!.style.width).toBe("33%");
    expect(dom.kpiCacheHealth!.textContent).toBe("");
    expect(state.currentPausedRepos.has("o/a")).toBe(true);
    expect(sub.renderRunners).toHaveBeenCalled();
    expect(sub.renderRepos).toHaveBeenCalled();
    expect(sub.renderQueue).toHaveBeenCalled();
  });

  it.each([
    [50, "var(--emerald)"],
    [30, "var(--solar)"],
    [5, "var(--crimson)"],
  ])("colors the rate limit bar at %d%%", (pct, color) => {
    renderState(snap({ rate_limit_remaining: pct, rate_limit_limit: 100 }));
    expect(dom.statRateLimitBar!.style.backgroundColor).not.toBe("");
    expect(dom.statRateLimitBar!.style.width).toBe(`${pct}%`);
    expect(color).toBeTruthy();
  });

  it("uses defaults for an empty snapshot", () => {
    renderState(snap({}));
    expect(dom.statVersion!.textContent).toBe("v1.0.0");
    expect(dom.statRateLimit!.textContent).toBe("--/--");
    expect(dom.statRateLimitBar!.style.width).toBe("0%");
    expect(dom.kpiMaxRunners!.textContent).toBe("/ 3 max");
    expect(dom.kpiMinRunnersText!.textContent).toContain("3 free · 0 standby");
    expect(dom.kpiRunnerSizing!.textContent).toBe("// 3 CPU · 4g each");
    expect(dom.kpiQueueHealth!.textContent).toBe("// Queue clear");
    expect(dom.kpiRoutingSub!.textContent).toBe("// Auto-detect DIND & Services");
    expect(dom.kpiRoutingHealth!.textContent).toBe("// No active workload yet");
    expect(dom.kpiVmRatio!.textContent).toBe("0%");
    expect(dom.kpiCacheHealth!.textContent).toBe("// Cache stats syncing...");
  });

  it("reports a backlog and workload types", () => {
    renderState(
      snap({ busy_runners: 3, max_runners: 3, queued_jobs: [{}], runners: [runner({ backend: "orbstack" })] }),
    );
    expect(dom.kpiQueueHealth!.textContent).toContain("Backlogged");
    expect(dom.kpiRoutingHealth!.textContent).toBe("// VM-heavy workload");
    renderState(snap({ runners: [runner({ backend: "docker" })] }));
    expect(dom.kpiRoutingHealth!.textContent).toBe("// Container-only workload");
  });

  it("works without the optional elements", () => {
    for (const el of document.querySelectorAll("[id^='kpi-'], #stat-rate-meta, #cnt-docker-jobs, #cnt-vm-jobs, #bar-docker-jobs, #bar-vm-jobs")) {
      el.remove();
    }
    initDom();
    expect(() =>
      renderState(snap({ rate_limit_remaining: 1, rate_limit_limit: 10, queued_jobs: [{}], runners: [runner()] })),
    ).not.toThrow();
  });
});
