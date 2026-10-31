import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { jsonResponse, stubFetch } from "../../test/helpers";
import { queued, runner } from "../../test/factories";
import { QueueViewComponent } from "./QueueView";
import { RunnerFleetComponent } from "./RunnerFleet";

const el = () => document.body.appendChild(document.createElement("div"));

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-01-01T00:10:00Z"));
});
afterEach(() => {
  vi.useRealTimers();
});

const settle = () => vi.advanceTimersByTimeAsync(4100);

describe("QueueViewComponent", () => {
  const jobs = () => [
    queued({
      id: 1,
      name: "running",
      status: "in_progress",
      queue_position: 2,
      waiting_reason: "slot",
      head_branch: "main",
      run_attempt: 3,
      started_at: "2026-01-01T00:00:00Z",
      labels: ["self-hosted", "arm64"],
    }),
    queued({
      id: 2,
      name: "waiting",
      status: "queued",
      queue_position: undefined,
      waiting_reason: undefined,
      head_branch: undefined,
      run_attempt: 1,
      workflow_name: undefined,
      started_at: undefined,
      created_at: "2026-01-01T00:09:30Z",
      labels: undefined,
    }),
  ];

  it("renders an empty state", () => {
    const c = el();
    new QueueViewComponent(c).render();
    expect(c.textContent).toContain("Queue is Empty");
  });

  it("renders a blank duration when no timestamps exist", () => {
    const c = el();
    new QueueViewComponent(c).setJobs([queued({ id: 3, started_at: undefined, created_at: "" })]);
    expect(c.textContent).toMatch(/waiting\s*\n/);
  });

  it("renders job cards", () => {
    const c = el();
    new QueueViewComponent(c).setJobs(jobs());
    expect(c.textContent).toContain("Rank #2");
    expect(c.textContent).toContain("IN PROGRESS");
    expect(c.textContent).toContain("QUEUED");
    expect(c.textContent).toContain("Attempt 3");
    expect(c.textContent).toContain("running 10m 0s");
    expect(c.textContent).toContain("waiting 30s");
    expect(c.textContent).not.toContain("self-hosted");
  });

  it("ticks elapsed times and stops when destroyed", () => {
    const c = el();
    const q = new QueueViewComponent(c);
    q.destroy();
    q.setJobs(jobs());
    q.setJobs(jobs());
    const stray = document.createElement("span");
    stray.dataset.createdAt = "";
    c.appendChild(stray);
    const bad = document.createElement("span");
    bad.dataset.createdAt = "garbage";
    c.appendChild(bad);
    vi.advanceTimersByTime(1000);
    expect(c.textContent).toContain("running 10m 1s");
    expect(bad.textContent).toBe("waiting ");
    q.destroy();
    vi.advanceTimersByTime(5000);
    expect(c.textContent).toContain("running 10m 1s");
  });

  it("handles actions: decline, success, default message and failure", async () => {
    const c = el();
    const q = new QueueViewComponent(c);
    q.setJobs(jobs());
    const confirmSpy = vi.spyOn(window, "confirm");
    const click = (action: string) =>
      c.querySelector<HTMLButtonElement>(`[data-action="${action}"]`)!.click();

    confirmSpy.mockReturnValueOnce(false);
    click("cancel");
    expect(confirmSpy).toHaveBeenCalledWith("Are you sure you want to cancel workflow run #100 on o/r?");

    confirmSpy.mockReturnValue(true);
    stubFetch(() => jsonResponse({ message: "queued ok" }));
    click("rerun");
    expect(confirmSpy).toHaveBeenLastCalledWith(expect.stringContaining("re-run all jobs for"));
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✓ queued ok");
    await settle();
    expect(c.textContent).not.toContain("✓ queued ok");

    stubFetch(() => jsonResponse({}));
    click("rerun-failed");
    expect(confirmSpy).toHaveBeenLastCalledWith(expect.stringContaining("re-run failed jobs for"));
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✓ rerun-failed triggered");
    await settle();

    stubFetch(() => jsonResponse({ error: "denied" }, { ok: false }));
    click("cancel");
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✗ Action failed: denied");
    await settle();
    q.destroy();
  });
});

describe("RunnerFleetComponent", () => {
  const runners = () => [
    runner({ id: "1", name: "vm-one", backend: "orbstack", job_id: 5, job_url: "http://job" }),
    runner({ id: "2", name: "dock", backend: "docker", job_id: 6, job_url: undefined }),
    runner({ id: "3", name: "idle", backend: "docker", job_id: undefined }),
    runner({ id: "4", name: "nob", backend: "vm", job_id: undefined }),
  ];
  const setup = (rs = runners(), status?: string) => {
    const c = el();
    const f = new RunnerFleetComponent(c);
    f.setRunners(rs, status);
    return { c, f };
  };
  const $ = (c: HTMLElement, sel: string) => c.querySelector<HTMLButtonElement>(sel)!;

  it("renders runners, standby and empty states", () => {
    const { c } = setup();
    expect(c.textContent).toContain("Active Runner Fleet (4)");
    expect(c.textContent).toContain("Job #5");
    expect(c.textContent).toContain("Standby");
    expect(c.textContent).toContain("Pause Spawning");
    expect(c.innerHTML).toContain('href="#"');
    const e = setup([], "paused");
    expect(e.c.textContent).toContain("No active ephemeral runners.");
    expect(e.c.textContent).toContain("Resume Spawning");
  });

  it("toggles spawning and reports failures", async () => {
    const { c } = setup();
    const f = stubFetch(() => jsonResponse({ success: true }));
    $(c, "#toggle-spawning-btn").click();
    expect(c.textContent).toContain("Pausing autoscaler spawning...");
    await vi.advanceTimersByTimeAsync(0);
    expect(JSON.parse(f.mock.calls[0][1]!.body as string).action).toBe("pause");
    expect(c.textContent).toContain("✓ Autoscaler paused");
    await settle();
    $(c, "#toggle-spawning-btn").click();
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✓ Autoscaler resumed");
    await settle();
    stubFetch(() => jsonResponse({ error: "bad" }, { ok: false }));
    $(c, "#toggle-spawning-btn").click();
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✗ Action failed: bad");
    await settle();
  });

  it("opens, cancels and submits the spawn form", async () => {
    const { c } = setup();
    $(c, "#open-spawn-form-btn").click();
    expect(c.querySelector("#manual-repo-input")).toBeTruthy();
    $(c, "#manual-spawn-cancel").click();
    expect(c.querySelector("#manual-repo-input")).toBeNull();

    $(c, "#open-spawn-form-btn").click();
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
    $(c, "#manual-spawn-submit").click();
    expect(alertSpy).toHaveBeenCalled();

    const f = stubFetch(() => jsonResponse({ success: true }));
    c.querySelector<HTMLInputElement>("#manual-repo-input")!.value = " o/r ";
    c.querySelector<HTMLSelectElement>("#manual-arch-select")!.value = "amd64";
    $(c, "#manual-spawn-submit").click();
    expect(c.querySelector("#manual-repo-input")).toBeNull();
    await vi.advanceTimersByTimeAsync(0);
    expect(JSON.parse(f.mock.calls[0][1]!.body as string)).toMatchObject({ repo: "o/r", arch: "amd64" });
    expect(c.textContent).toContain("✓ Spawned runner");
    await settle();

    $(c, "#open-spawn-form-btn").click();
    c.querySelector<HTMLInputElement>("#manual-repo-input")!.value = "o/r";
    stubFetch(() => jsonResponse({ error: "full" }, { ok: false }));
    $(c, "#manual-spawn-submit").click();
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✗ Spawn failed: full");
    await settle();
  });

  it("stops runners with and without a job", async () => {
    const { c } = setup();
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValueOnce(false);
    $(c, '.stop-runner-btn[data-runner-id="1"]').click();
    expect(confirmSpy.mock.calls[0][0]).toContain("Job #5");

    confirmSpy.mockReturnValue(true);
    stubFetch(() => jsonResponse({ success: true }));
    $(c, '.stop-runner-btn[data-runner-id="3"]').click();
    expect(confirmSpy).toHaveBeenLastCalledWith("Are you sure you want to stop and remove runner 'idle'?");
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✓ Stopped runner idle");
    await settle();

    stubFetch(() => jsonResponse({ error: "x" }, { ok: false }));
    $(c, '.stop-runner-btn[data-runner-id="3"]').click();
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✗ Failed stopping runner: x");
    await settle();
  });

  it("opens terminals", async () => {
    const { c } = setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    const btn = (id: string) => $(c, `.terminal-runner-btn[data-runner-id="${id}"]`);

    stubFetch(() => jsonResponse({ command: "exec", terminal_launched: true }));
    btn("1").click();
    expect(btn("1").textContent).toContain("Launching...");
    await vi.advanceTimersByTimeAsync(0);
    expect(writeText).toHaveBeenCalledWith("exec");
    expect(c.textContent).toContain("✓ Terminal opened for vm-one");
    await settle();

    vi.stubGlobal("navigator", { clipboard: { writeText: vi.fn().mockRejectedValue(new Error("no")) } });
    stubFetch(() => jsonResponse({ command: "exec2" }));
    btn("2").click();
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✓ Command copied: exec2");
    await settle();

    stubFetch(() => jsonResponse({ terminal_launched: true }));
    btn("3").click();
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✓ Terminal opened for idle");
    await settle();

    stubFetch(() => jsonResponse({ error: "boom" }, { ok: false }));
    btn("3").click();
    await vi.advanceTimersByTimeAsync(0);
    expect(c.textContent).toContain("✗ Terminal error: boom");
    await settle();
  });

  it("falls back to an empty backend attribute", () => {
    const { c } = setup([runner({ id: "9", backend: "docker" })]);
    expect(c.querySelector('[data-backend="docker"]')).toBeTruthy();
  });
});
