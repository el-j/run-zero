import { beforeEach, describe, expect, it, vi } from "vitest";
import { completed, removeAllElements } from "../../test/factories";
import { mountDashboard, pinClockAndLocale } from "../../test/helpers";
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
    messages: ["m1", "m2"],
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
    expect(list).toContain("<li>m1</li><li>m2</li>");
    expect(list).toContain("https://github.com/o/r/actions/runs/7");
    expect(dom.jobsTableBody!.querySelectorAll("tr")).toHaveLength(3);
    expect(dom.jobsTableBody!.innerHTML).toContain("branch: main");
    expect(dom.jobsTableBody!.innerHTML).toContain("attempt 2");
    expect(dom.jobsTableEmpty!.classList.contains("hidden")).toBe(true);
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
    expect(dom.jobsTableEmpty!.textContent).toContain(
      "Recent successful and failed GitHub Actions jobs appear here.",
    );
  });

  it("filters matching jobs and shows the filter message", () => {
    state.currentViewMode = "table";
    dom.jobsSearchInput!.value = "bad";
    renderCompletedJobs(full());
    expect(dom.jobsTableBody!.querySelectorAll("tr")).toHaveLength(1);
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

// Three jobs whose order differs for every sort key and direction.
const trio = () => [
  completed({
    id: 2,
    name: "bravo",
    conclusion: "failure",
    failure_reason: "boom",
    duration_sec: 10,
    completed_at: "2026-01-03T00:00:00Z",
  }),
  completed({ id: 3, name: "charlie", conclusion: "", failed_step: "lint" }),
  completed({
    id: 1,
    name: "alpha",
    conclusion: "success",
    duration_sec: 30,
    completed_at: "2026-01-02T00:00:00Z",
  }),
];

const rowNames = () =>
  [...dom.jobsTableBody!.querySelectorAll(".jobs-table-job-link")].map((a) => a.textContent);
const cardNames = () =>
  [...dom.jobsList!.querySelectorAll("article a")]
    .filter((_, i) => i % 2 === 0)
    .map((a) => a.textContent!.trim());

describe("renderCompletedJobs output", () => {
  beforeEach(() => pinClockAndLocale());

  it("renders the full history as cards and table rows", () => {
    state.currentViewMode = "table";
    renderCompletedJobs(full());
    expect(dom.jobsList!.innerHTML).toMatchSnapshot("cards");
    expect(dom.jobsTableBody!.innerHTML).toMatchSnapshot("table");
  });

  it("renders the empty history", () => {
    state.currentViewMode = "table";
    dom.jobsTableBody!.innerHTML = "<tr><td>stale</td></tr>";
    renderCompletedJobs([]);
    expect(dom.jobsList!.innerHTML).toMatchSnapshot();
    expect(dom.jobsTableBody!.innerHTML).toBe("");
    expect(dom.jobsTableEmpty!.classList.contains("hidden")).toBe(false);
  });

  it("renders a filter miss", () => {
    state.currentViewMode = "table";
    dom.jobsSearchInput!.value = "<nomatch>";
    renderCompletedJobs(full());
    expect(dom.jobsList!.innerHTML).toMatchSnapshot();
    expect(dom.jobsTableEmpty!.classList.contains("hidden")).toBe(false);
  });

  it("shows the filter miss even when there is history", () => {
    state.currentViewMode = "cards";
    dom.jobsSearchInput!.value = "nomatch";
    dom.jobsTableEmpty!.classList.remove("hidden");
    renderCompletedJobs(full());
    expect(dom.jobsList!.innerHTML).toContain("NO HISTORY MATCHES FILTER");
    expect(dom.jobsTableEmpty!.classList.contains("hidden")).toBe(true);
  });

  it("orders cards newest first, undated last", () => {
    renderCompletedJobs(trio());
    expect(cardNames()).toEqual(["bravo", "alpha", "charlie"]);
    renderCompletedJobs([...trio()].reverse());
    expect(cardNames()).toEqual(["bravo", "alpha", "charlie"]);
  });

  it("sorts the table by analysis using the fallback reason", () => {
    state.jobsSort = { key: "analysis", dir: "asc" };
    const jobs = [
      completed({ id: 1, name: "m", failure_reason: "m-reason" }),
      completed({ id: 2, name: "step", failed_step: "a-step" }),
      completed({ id: 3, name: "both", failure_reason: "z-reason", failed_step: "b-step" }),
      completed({ id: 4, name: "none" }),
    ];
    renderCompletedJobs(jobs);
    expect(rowNames()).toEqual(["step", "m", "none", "both"]);
    renderCompletedJobs([...jobs].reverse());
    expect(rowNames()).toEqual(["step", "m", "none", "both"]);
  });

  it.each([
    ["result", ["bravo", "alpha", "charlie"]],
    ["name", ["alpha", "bravo", "charlie"]],
    ["analysis", ["bravo", "charlie", "alpha"]],
    ["duration", ["charlie", "bravo", "alpha"]],
    ["completed", ["charlie", "alpha", "bravo"]],
  ] as const)("sorts the table by %s", (key, asc) => {
    state.jobsSort = { key, dir: "asc" };
    renderCompletedJobs(trio());
    expect(rowNames()).toEqual(asc);
    state.jobsSort = { key, dir: "desc" };
    renderCompletedJobs(trio());
    expect(rowNames()).toEqual([...asc].reverse());
  });

  it("sorts by name, then repo", () => {
    state.jobsSort = { key: "name", dir: "asc" };
    renderCompletedJobs([
      completed({ id: 1, name: "x", repo: "o/b" }),
      completed({ id: 2, name: "x", repo: "o/a" }),
    ]);
    expect(
      [...dom.jobsTableBody!.querySelectorAll(".jobs-table-repo")].map((d) => d.textContent),
    ).toEqual(["o/a", "o/b"]);
  });

  it("offers retry only for jobs that did not succeed", () => {
    renderCompletedJobs(trio());
    const retried = [...document.querySelectorAll<HTMLButtonElement>(".job-rerun-btn")].map(
      (b) => b.dataset.runId,
    );
    expect(retried).toHaveLength(4); // bravo and charlie, in cards and table
    expect(dom.jobsList!.querySelectorAll(".job-rerun-btn")).toHaveLength(2);
  });

  it("shows an attempt only after the first", () => {
    renderCompletedJobs([
      completed({ id: 1, run_attempt: 1 }),
      completed({ id: 2, name: "again", run_attempt: 3 }),
    ]);
    expect(dom.jobsList!.innerHTML).not.toContain("Attempt 1");
    expect(dom.jobsList!.innerHTML).toContain("Attempt 3");
    expect(dom.jobsTableBody!.innerHTML).not.toContain("attempt 1");
  });

  it("shows a zero duration", () => {
    renderCompletedJobs([completed({ duration_sec: 0 })]);
    expect(dom.jobsList!.innerHTML).toContain(">0s<");
    expect(dom.jobsTableBody!.innerHTML).toContain(">0s<");
  });
});
