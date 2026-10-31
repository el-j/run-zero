import { beforeEach, describe, expect, it, vi } from "vitest";
import { removeAllElements, runner } from "../../test/factories";
import { mountDashboard } from "../../test/helpers";
import { dom, initDom } from "../dom";
import { state } from "../state";
import { renderRunners } from "./runners";

const actions = vi.hoisted(() => ({ stopRunner: vi.fn(), openRunnerTerminal: vi.fn() }));
vi.mock("../actions", () => actions);

beforeEach(() => {
  mountDashboard();
});

const mixed = () => [
  runner({ id: "a", name: "alpha", backend: "orbstack", target_arch: "arm64", created_at: "2026-01-01T00:00:00Z", progress_pct: 40, workflow_name: "wf", status: "busy", run_id: 1, job_id: 2, target_repo: "o/a", provider: "gitlab" }),
  runner({ id: "b", name: "", backend: "", target_arch: "", status: "", provider: undefined, target_repo: "" }),
  runner({ id: "c", name: "gamma", backend: "my-vm", is_cloud: true, origin: "cloud", job_url: "http://j", job_name: "jn" }),
  runner({ id: "d", name: "delta", origin: "external", run_url: "http://r", run_id: 4, provider: "GitHub" }),
];

describe("renderRunners", () => {
  it("renders cards and table rows for a mixed fleet", () => {
    state.currentViewMode = "table";
    renderRunners(mixed());
    expect(dom.tabRunnersCount!.textContent).toBe("4");
    expect(dom.runnersCountBadge!.textContent).toBe("4 RUNNING");
    const group = dom.runnersOriginFilterGroup!;
    expect(group.querySelector('[data-origin="all"]')!.textContent).toBe("All (4)");
    expect(group.querySelector('[data-origin="local"]')!.textContent).toContain("(2)");
    expect(group.querySelector('[data-origin="cloud"]')!.textContent).toContain("(1)");
    expect(group.querySelector('[data-origin="external"]')!.textContent).toContain("(1)");

    const cards = dom.runnersGrid!.innerHTML;
    expect(cards).toContain("ORBSTACK");
    expect(cards).toContain("DOCKER");
    expect(cards).toContain("MY-VM");
    expect(cards).toContain("Standby Pool");
    expect(cards).toContain("GitLab");
    expect(cards).toContain("GitHub");
    expect(cards).toContain("Remote Managed");
    expect(cards).toContain("Workflow: wf");
    expect(cards).toContain("Run #1");
    expect(cards).toContain("jn");
    expect(cards).toContain("RUNNING");
    expect(cards).toContain("BUSY");
    expect(dom.runnersGrid!.classList.contains("hidden")).toBe(false);
    expect(dom.runnersEmptyState!.classList.contains("hidden")).toBe(true);

    const rows = dom.runnersTableBody!.querySelectorAll("tr");
    expect(rows).toHaveLength(4);
    expect(dom.runnersTableBody!.innerHTML).toContain("Standby / Idle");
    expect(dom.runnersTableBody!.innerHTML).toContain("Standby");
    expect(dom.runnersTableBody!.innerHTML).toContain("-</span>");
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(true);
  });

  it("shows the empty states with no runners", () => {
    renderRunners([]);
    expect(dom.runnersEmptyState!.classList.contains("hidden")).toBe(false);
    expect(dom.runnersEmptyState!.querySelector(".empty-title")!.textContent).toBe("Fleet is on Standby");
    expect(dom.runnersGrid!.classList.contains("hidden")).toBe(true);
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(false);
    state.currentViewMode = "table";
    renderRunners([]);
    expect(dom.runnersTableEmpty!.textContent).toBe("No active runners running.");
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(false);
  });

  it("filters by text, origin and provider", () => {
    dom.runnersSearchInput!.value = "  ALPHA ";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);
    expect(dom.runnersEmptyState!.querySelector(".empty-title")!.textContent).toBe("No runners match this filter");
    expect(dom.runnersEmptyState!.querySelector(".empty-desc")!.textContent).toContain('"alpha"');

    dom.runnersSearchInput!.value = "zzz";
    state.currentViewMode = "table";
    renderRunners(mixed());
    expect(dom.runnersGrid!.classList.contains("hidden")).toBe(true);
    expect(dom.runnersTableEmpty!.textContent).toBe('No runners matching "zzz".');
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(false);

    dom.runnersSearchInput!.value = "";
    state.currentRunnersOrigin = "cloud";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);
    state.currentRunnersOrigin = "external";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);

    state.currentRunnersOrigin = "all";
    state.currentRunnersProvider = "gitlab";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);
    state.currentRunnersProvider = "github";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(3);
  });

  it("sorts the table by every key in both directions", () => {
    state.currentViewMode = "table";
    const keys = ["name", "repo", "engine", "status", "workflow", "progress", "uptime"] as const;
    for (const key of keys) {
      for (const dir of ["asc", "desc"] as const) {
        state.runnersSort = { key, dir };
        renderRunners(mixed());
        expect(dom.runnersTableBody!.querySelectorAll("tr")).toHaveLength(4);
      }
    }
    state.runnersSort = { key: "name", dir: "asc" };
    renderRunners(mixed());
    const first = dom.runnersTableBody!.querySelector("tr td span:last-of-type")!;
    expect(first.textContent).toBe("alpha");
  });

  it("sorts pairs regardless of input order", () => {
    state.currentViewMode = "table";
    const dated = runner({ id: "d", created_at: "2026-01-01T00:00:00Z" });
    const undated = runner({ id: "u" });
    renderRunners([dated, undated]);
    renderRunners([undated, dated]);
    expect(dom.runnersTableBody!.querySelectorAll("tr")).toHaveLength(2);
  });

  it("binds stop and terminal buttons only for local runners", () => {
    renderRunners([runner({ id: "x", name: "x", job_id: 7 }), runner({ id: "y", origin: "cloud" })]);
    const stop = document.querySelectorAll<HTMLButtonElement>(".stop-runner-btn");
    const term = document.querySelectorAll<HTMLButtonElement>(".terminal-runner-btn");
    expect(stop).toHaveLength(2);
    expect(term).toHaveLength(2);
    stop[0].click();
    term[0].click();
    expect(actions.stopRunner).toHaveBeenCalledWith(stop[0]);
    expect(actions.openRunnerTerminal).toHaveBeenCalledWith(term[0]);
    expect(stop[0].dataset.jobId).toBe("7");
  });

  it("tolerates missing elements", () => {
    removeAllElements();
    expect(() => renderRunners(mixed())).not.toThrow();
    expect(() => renderRunners([])).not.toThrow();
    state.currentViewMode = "table";
    expect(() => renderRunners(mixed())).not.toThrow();
  });

  it("tolerates a bare filter group and bare empty state", () => {
    document.getElementById("runners-origin-filter-group")!.innerHTML = "";
    document.getElementById("runners-empty-state")!.innerHTML = "";
    initDom();
    expect(() => renderRunners(mixed())).not.toThrow();
    expect(() => renderRunners([])).not.toThrow();
  });
});
