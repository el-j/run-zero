import { describe, expect, it } from "vitest";
import { jobLinkHtml, jobUrlOf, progressHtml, runLinkHtml, runUrlOf, stepIcon } from "./runRef";

describe("runRef", () => {
  it("runUrlOf", () => {
    expect(runUrlOf({ run_url: "http://x" })).toBe("http://x");
    expect(runUrlOf({ run_id: 5, repo: "o/r" })).toBe("https://github.com/o/r/actions/runs/5");
    expect(runUrlOf({ run_id: 5, target_repo: "t/r", repo: "o/r" })).toBe(
      "https://github.com/t/r/actions/runs/5",
    );
    expect(runUrlOf({ run_id: 5 })).toBe("");
    expect(runUrlOf({})).toBe("");
  });

  it("jobUrlOf", () => {
    expect(jobUrlOf({ job_url: "http://j" })).toBe("http://j");
    expect(jobUrlOf({ run_id: 5, job_id: 6, repo: "o/r" })).toBe(
      "https://github.com/o/r/actions/runs/5/job/6",
    );
    expect(jobUrlOf({ run_id: 5, job_id: 6 })).toBe("");
    expect(jobUrlOf({ run_id: 5, repo: "o/r" })).toBe("");
  });

  it("runLinkHtml / jobLinkHtml", () => {
    expect(runLinkHtml({})).toBe("");
    expect(runLinkHtml({ run_url: "http://x", run_id: 7 })).toContain("Run #7");
    expect(runLinkHtml({ run_url: "http://x" })).toContain("Run # ↗");
    expect(jobLinkHtml({})).toBe("");
    expect(jobLinkHtml({ job_url: "http://j", job_name: "build<" })).toContain("build&lt;");
    expect(jobLinkHtml({ job_url: "http://j", job_id: 9 })).toContain("Job #9");
    expect(jobLinkHtml({ job_url: "http://j" })).toContain("Job # ↗");
  });

  it("stepIcon", () => {
    expect(stepIcon("completed")).toBe("✓");
    expect(stepIcon("in_progress")).toBe("▶");
    expect(stepIcon("queued")).toBe("○");
  });

  it("progressHtml returns empty without data", () => {
    expect(progressHtml({}, false)).toBe("");
  });

  it("progressHtml with steps renders pipeline unless compact", () => {
    const steps = [
      { number: 1, name: "checkout", status: "completed" },
      { number: 2, name: "build", status: "in_progress" },
    ];
    const full = progressHtml({ steps, progress_pct: 50, current_step: "build" }, false);
    expect(full).toContain("step 2/2");
    expect(full).toContain("50%");
    expect(full).toContain("step-pipeline");
    expect(full).toContain("Current stage");
    expect(full).toContain("margin-top: 6px");
    const compact = progressHtml({ steps }, true);
    expect(compact).not.toContain("step-pipeline");
    expect(compact).toContain("margin-top: 0px");
    expect(compact).toContain("0%");
  });

  it("progressHtml uses explicit step counts and job-count fallback", () => {
    expect(progressHtml({ steps_completed: 9, steps_total: 4, progress_pct: 1 }, false)).toContain(
      "step 4/4",
    );
    expect(progressHtml({ progress_pct: 10, stages_done: 2, stages_total: 3 }, false)).toContain(
      "2/3 jobs",
    );
    expect(progressHtml({ progress_pct: 10 }, false)).toContain("0/1 jobs");
    expect(progressHtml({ current_step: "x" }, false)).toContain("0/1 jobs");
    expect(progressHtml({ steps: [], progress_pct: 3 }, false)).not.toContain("step-pipeline");
  });
});

describe("progressHtml output", () => {
  it("counts completed steps and renders each step chip", () => {
    const steps = [
      { number: 1, name: "Set up", status: "completed" },
      { number: 2, name: "Build <x>", status: "in_progress" },
      { number: 3, name: "Test", status: "queued" },
      { number: 4, name: "Post", status: "queued" },
    ];
    const html = progressHtml({ steps, progress_pct: 25 }, false);
    expect(html).toContain("step 2/4");
    expect(html).toMatchSnapshot();
  });
});
