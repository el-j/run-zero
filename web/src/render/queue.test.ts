import { beforeEach, describe, expect, it, vi } from "vitest";
import { queued, removeAllElements } from "../../test/factories";
import { mountDashboard } from "../../test/helpers";
import { dom, initDom } from "../dom";
import { state } from "../state";
import { renderQueue } from "./queue";

const actions = vi.hoisted(() => ({ triggerQueueAction: vi.fn() }));
vi.mock("../actions", () => actions);

beforeEach(() => {
  mountDashboard();
});

const conc = { active: 2, max: 5 };

/** Jobs that exercise both sides of every optional field. */
const varied = () => [
  queued({
    id: 1,
    name: "full",
    workflow_name: "CI",
    repo: "o/a",
    head_branch: "main",
    status: "in_progress",
    queue_position: 1,
    run_url: "http://run",
    progress_pct: 50,
    stages_done: 1,
    stages_total: 4,
    current_step: "compile",
    waiting_reason: "no slot",
    started_at: "2026-01-01T00:00:00Z",
    labels: ["self-hosted", "arm64", "linux"],
  }),
  queued({
    id: 2,
    name: "bare",
    workflow_name: undefined,
    head_branch: undefined,
    status: "queued",
    queue_position: undefined,
    run_url: undefined,
    progress_pct: undefined,
    stages_done: undefined,
    stages_total: undefined,
    current_step: undefined,
    waiting_reason: undefined,
    started_at: undefined,
    created_at: "2026-01-02T00:00:00Z",
    labels: undefined,
  }),
  queued({
    id: 3,
    name: "staged",
    status: "queued",
    stages_total: 2,
    progress_pct: undefined,
    created_at: undefined,
    started_at: undefined,
  }),
  queued({
    id: 5,
    name: "pct-only",
    progress_pct: 10,
    stages_done: undefined,
    stages_total: undefined,
  }),
  queued({
    id: 4,
    name: "",
    workflow_name: "",
    repo: "",
    status: "",
    run_id: undefined as unknown as number,
    created_at: "2026-01-03T00:00:00Z",
  }),
];

describe("renderQueue", () => {
  it("renders cards, table and counters", () => {
    state.currentViewMode = "table";
    renderQueue(varied(), conc);
    expect(dom.tabQueueCount!.textContent).toBe("5");
    expect(dom.queueBusySlots!.textContent).toBe("2");
    expect(dom.queueMaxSlots!.textContent).toBe("5");
    expect(dom.queueFreeSlots!.textContent).toBe("3");
    expect(dom.queueTotalJobs!.textContent).toBe("5");
    expect(dom.queueSlotsBadge!.textContent).toBe("2/5 SLOTS");
    expect(dom.queueJobsCountTag!.textContent).toBe("5 JOBS");
    const cards = dom.queueJobsView!.innerHTML;
    expect(cards).toContain("Rank #1");
    expect(cards).toContain("RUNNING");
    expect(cards).toContain("QUEUED");
    expect(cards).toContain("compile");
    expect(cards).toContain("no slot");
    expect(cards).toContain("ARM64");
    expect(cards).not.toContain("SELF-HOSTED");
    expect(cards).toContain("Stage 0/2 done");
    expect(dom.queueTableBody!.querySelectorAll("tr")).toHaveLength(5);
    expect(dom.queueTableEmpty!.classList.contains("hidden")).toBe(true);
    expect(dom.queueTableEmpty!.textContent).toContain("Queue is clear");
  });

  it("never reports negative free slots", () => {
    renderQueue(varied(), { active: 9, max: 5 });
    expect(dom.queueFreeSlots!.textContent).toBe("0");
  });

  it("describes filter state in the table", () => {
    state.currentViewMode = "table";
    dom.queueSearchInput!.value = "full";
    renderQueue(varied(), conc);
    expect(dom.queueTableBody!.querySelectorAll("tr")).toHaveLength(1);
    expect(dom.queueTableEmpty!.textContent).toContain('No queued jobs matching "full"');
  });

  it("shows empty states", () => {
    state.currentViewMode = "table";
    renderQueue([], conc);
    expect(dom.queueJobsView!.innerHTML).toContain("ALL WORKFLOW QUEUES ARE CLEAR");
    expect(dom.queueTableEmpty!.textContent).toContain("Queue is clear");
    expect(dom.queueTableEmpty!.classList.contains("hidden")).toBe(false);
    dom.queueSearchInput!.value = "zzz";
    renderQueue(varied(), conc);
    expect(dom.queueJobsView!.innerHTML).toContain("NO QUEUED JOBS MATCH");
    expect(dom.queueTableEmpty!.textContent).toContain('No queued jobs matching "zzz"');
    dom.queueSearchInput!.value = "";
    state.currentViewMode = "cards";
    const before = dom.queueTableEmpty!.textContent;
    renderQueue([], conc);
    expect(dom.queueTableEmpty!.textContent).toBe(before);
  });

  it("keeps the table hint untouched in card mode", () => {
    state.currentViewMode = "cards";
    const before = dom.queueTableEmpty!.textContent;
    renderQueue(varied(), conc);
    expect(dom.queueTableEmpty!.textContent).toBe(before);
  });

  it.each(["position", "status", "name", "run", "repo", "progress", "wait"] as const)(
    "sorts by %s in both directions and input orders",
    (key) => {
      for (const dir of ["asc", "desc"] as const) {
        state.queueSort = { key, dir };
        renderQueue(varied(), conc);
        renderQueue(varied().reverse(), conc);
      }
      expect(dom.queueTableBody!.querySelectorAll("tr")).toHaveLength(5);
    },
  );

  it("covers started/created combinations in wait sorting", () => {
    state.queueSort = { key: "wait", dir: "asc" };
    const jobs = [
      queued({ id: 1, started_at: "2026-01-01T00:00:00Z" }),
      queued({ id: 2, started_at: undefined, created_at: "2026-01-02T00:00:00Z" }),
      queued({ id: 3, started_at: undefined, created_at: undefined }),
      queued({ id: 4, started_at: "2026-01-04T00:00:00Z" }),
      queued({ id: 5, started_at: undefined, created_at: "2026-01-05T00:00:00Z" }),
      queued({ id: 6, started_at: undefined, created_at: undefined }),
    ];
    renderQueue(jobs, conc);
    renderQueue([...jobs].reverse(), conc);
  });

  it("binds action buttons", () => {
    renderQueue(varied(), conc);
    const btn = document.querySelector<HTMLButtonElement>(".action-btn")!;
    btn.click();
    expect(actions.triggerQueueAction).toHaveBeenCalledWith(btn);
  });

  it("tolerates missing elements", () => {
    removeAllElements();
    renderQueue(varied(), conc);
    renderQueue([], conc);
    const ids = ["queue-jobs-view", "queue-table-body", "queue-table-empty"];
    for (const missing of ids) {
      for (const jobs of [varied(), []]) {
        delete document.body.dataset.shellRendered;
        mountDashboard();
        document.getElementById(missing)?.remove();
        initDom();
        state.currentViewMode = "table";
        renderQueue(jobs, conc);
        if (dom.queueSearchInput) dom.queueSearchInput.value = "full";
        renderQueue(jobs, conc);
      }
    }
  });
});
