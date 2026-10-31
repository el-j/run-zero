import { beforeEach, describe, expect, it, vi } from "vitest";
import { completed, removeAllElements } from "../../test/factories";
import { mountDashboard } from "../../test/helpers";
import { dom, initDom } from "../dom";
import { state } from "../state";
import { renderCompletedJobs } from "./jobs";

const actions = vi.hoisted(() => ({ retryFailedJobs: vi.fn() }));
vi.mock("../actions", () => actions);

beforeEach(() => {
  mountDashboard();
});

const full = () => [
  completed({
    id: 1,
    name: "ok",
    conclusion: "success",
    completed_at: "2026-01-02T00:00:00Z",
    duration_sec: 5,
    workflow_name: "CI",
    head_branch: "main",
    run_attempt: 2,
    run_url: "http://run",
    messages: ["m1"],
  }),
  completed({
    id: 2,
    name: "bad",
    conclusion: "failure",
    completed_at: "2026-01-01T00:00:00Z",
    failure_reason: "boom",
    failed_step: "step 3",
    html_url: "",
    run_attempt: 1,
  }),
  completed({ id: 3, name: "mystery", conclusion: "", run_id: 7 }),
];

describe("renderCompletedJobs", () => {
  it("renders cards and table rows", () => {
    state.currentViewMode = "table";
    renderCompletedJobs(full());
    expect(dom.tabJobsCount!.textContent).toBe("3");
    const list = dom.jobsList!.innerHTML;
    expect(list).toContain("SUCCESS");
    expect(list).toContain("FAILURE");
    expect(list).toContain("UNKNOWN");
    expect(list).toContain("Attempt 2");
    expect(list).toContain("boom");
    expect(list).toContain("Failed step:");
    expect(list).toContain("<li>m1</li>");
    expect(list).toContain("https://github.com/o/r/actions/runs/7");
    expect(dom.jobsTableBody!.querySelectorAll("tr")).toHaveLength(3);
    expect(dom.jobsTableBody!.innerHTML).toContain("branch: main");
    expect(dom.jobsTableBody!.innerHTML).toContain("attempt 2");
    expect(dom.jobsTableEmpty!.classList.contains("hidden")).toBe(true);
    expect(dom.jobsTableEmpty!.textContent).toContain("Recent successful");
  });

  it("describes filter misses in table mode", () => {
    state.currentViewMode = "table";
    dom.jobsSearchInput!.value = "nomatch";
    renderCompletedJobs(full());
    expect(dom.jobsTableEmpty!.textContent).toContain('No completed jobs matching "nomatch"');
    expect(dom.jobsList!.innerHTML).toContain("NO HISTORY MATCHES FILTER");
  });

  it("keeps the table hint hidden in card mode", () => {
    state.currentViewMode = "cards";
    renderCompletedJobs(full());
    renderCompletedJobs([]);
    expect(dom.jobsTableEmpty!.classList.contains("hidden")).toBe(true);
    expect(dom.jobsList!.innerHTML).toContain("NO COMPLETED JOBS YET");
  });

  it("shows the empty hint in table mode", () => {
    state.currentViewMode = "table";
    renderCompletedJobs([]);
    expect(dom.jobsTableEmpty!.textContent).toContain("Recent successful and failed GitHub Actions jobs appear here.");
  });

  it("filters matching jobs and shows the filter message", () => {
    state.currentViewMode = "table";
    dom.jobsSearchInput!.value = "bad";
    renderCompletedJobs(full());
    expect(dom.jobsTableBody!.querySelectorAll("tr")).toHaveLength(1);
    expect(dom.jobsTableEmpty!.textContent).toContain('No completed jobs matching "bad"');
    expect(dom.jobsTableEmpty!.classList.contains("hidden")).toBe(true);
  });

  it.each([
    ["result", "asc"],
    ["name", "asc"],
    ["analysis", "desc"],
    ["duration", "asc"],
    ["completed", "desc"],
  ] as const)("sorts by %s %s", (key, dir) => {
    state.jobsSort = { key, dir };
    renderCompletedJobs(full());
    expect(dom.jobsTableBody!.querySelectorAll("tr")).toHaveLength(3);
  });

  it("handles optional fields in every comparison order", () => {
    const base = [
      completed({ id: 1, name: "a", completed_at: "2026-01-01T00:00:00Z", failure_reason: "r" }),
      completed({ id: 2, name: "b", conclusion: "failure", failed_step: "s" }),
      completed({ id: 3, name: "c", duration_sec: 3 }),
      completed({ id: 4, name: "d", failed_step: "t" }),
      completed({ id: 5, name: "e", conclusion: "" }),
      completed({ id: 6, name: "f", conclusion: "" }),
    ];
    for (const key of ["result", "name", "analysis", "duration", "completed"] as const) {
      state.jobsSort = { key, dir: "asc" };
      renderCompletedJobs(base);
      renderCompletedJobs([...base].reverse());
    }
    expect(dom.jobsTableBody!.querySelectorAll("tr")).toHaveLength(6);
  });

  it("binds retry buttons", () => {
    renderCompletedJobs(full());
    const btns = document.querySelectorAll<HTMLButtonElement>(".job-rerun-btn");
    expect(btns.length).toBeGreaterThan(0);
    btns[0].click();
    expect(actions.retryFailedJobs).toHaveBeenCalledWith(btns[0]);
  });

  it("tolerates missing elements", () => {
    removeAllElements();
    renderCompletedJobs(full());
    const parts = ["jobs-list", "jobs-table-body", "jobs-table-empty"];
    for (const missing of parts) {
      delete document.body.dataset.shellRendered;
      mountDashboard();
      document.getElementById(missing)!.remove();
      initDom();
      renderCompletedJobs(full());
    }
  });
});
