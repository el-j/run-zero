import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { jsonResponse, mountDashboard, stubFetch } from "../../test/helpers";
import { BuildImagesModal } from "./BuildImagesModal";

const IDS = [
  "images-modal",
  "images-status-grid",
  "images-build-progress-panel",
  "images-build-step-text",
  "images-build-pct",
  "images-build-progress-bar",
  "images-build-log",
  "badge-images-status",
  "badge-images-icon",
  "btn-open-images",
  "images-modal-close",
  "images-modal-done",
  "btn-build-all-images",
  "btn-build-vm-images",
  "btn-build-container-images",
  "btn-cancel-image-build",
];

type Any = Record<string, unknown>;

const img = (o: Any = {}) => ({
  name: "n",
  kind: "docker",
  arch: "arm64",
  status: "ready",
  ...o,
});
const progress = (o: Any = {}) => ({
  build_id: "b",
  target: "all",
  arch: "all",
  status: "building",
  progress_pct: 40,
  current_step: "step",
  started_at: "",
  ...o,
});
const status = (o: Any = {}) => ({
  vm_images: [img({ kind: "orbstack-vm", name: "vm", version: "1.2" })],
  container_images: [img({ size_human: "10MB" })],
  all_ready: true,
  ...o,
});

const $ = (id: string) => document.getElementById(id)!;
const tick = (ms = 0) => vi.advanceTimersByTimeAsync(ms);

/** Mounts the dashboard, removes the given element ids, then constructs the modal. */
function make(remove: string[] = []) {
  document.body.innerHTML = "";
  delete document.body.dataset.shellRendered;
  mountDashboard();
  for (const id of remove) document.getElementById(id)?.remove();
  return new BuildImagesModal();
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.spyOn(window, "alert").mockImplementation(() => {});
});
afterEach(() => {
  vi.useRealTimers();
});

describe("BuildImagesModal construction and dialog", () => {
  it("opens and closes the dialog", async () => {
    const f = stubFetch(() => jsonResponse(status()));
    const m = make();
    await tick();
    const dialog = $("images-modal") as HTMLDialogElement;
    $("btn-open-images").click();
    expect(dialog.open).toBe(true);
    const calls = f.mock.calls.length;
    m.open();
    expect(f.mock.calls.length).toBe(calls);
    $("images-modal-close").click();
    expect(dialog.open).toBe(false);
    m.close();
    $("btn-open-images").click();
    $("images-modal-done").click();
    expect(dialog.open).toBe(false);
  });

  it("tolerates a missing DOM", async () => {
    stubFetch(() => jsonResponse(status()));
    const m = make(IDS);
    await tick();
    m.open();
    m.close();
    await m.refresh();
    m.handleProgressEvent(progress({ status: "failed" }) as never);
    await m.refresh();
    await tick(2000);
  });
});

describe("BuildImagesModal.refresh", () => {
  it("renders status cards and badge", async () => {
    stubFetch(() => jsonResponse(status({ vm_images: [img({ kind: "orbstack-vm", name: "vm" }), img({ name: "c", status: "stale", size_human: undefined }), img({ name: "d", status: "missing" })] })));
    make();
    await tick();
    const grid = $("images-status-grid").innerHTML;
    expect(grid).toContain("Ubuntu Noble base");
    expect(grid).toContain("Static runner image");
    expect(grid).toContain("Size: 10MB");
    expect(grid).toContain("tag-amber");
    expect(grid).toContain("tag-crimson");
    expect($("badge-images-status").textContent).toBe("2/4");
    expect($("badge-images-icon").textContent).toBe("✓");
  });

  it("shows the ready badge and OrbStack version", async () => {
    stubFetch(() => jsonResponse(status()));
    make();
    await tick();
    expect($("badge-images-icon").textContent).toBe("✓");
    expect($("images-status-grid").innerHTML).toContain("Runner v1.2");
  });

  it("handles missing icon, grid, badge and image lists", async () => {
    stubFetch(() => jsonResponse({ all_ready: true }));
    make(["badge-images-icon"]);
    await tick();
    expect($("badge-images-status").textContent).toBe("0/0");

    stubFetch(() => jsonResponse({ all_ready: false }));
    make(["badge-images-icon"]);
    await tick();

    stubFetch(() => jsonResponse(status()));
    make(["badge-images-status"]);
    await tick();
    expect($("images-status-grid").innerHTML).toContain("vm");

    make(["images-status-grid"]);
    await tick();
  });

  it("ignores failed and throwing fetches", async () => {
    stubFetch(() => jsonResponse({}, { ok: false }));
    const m = make();
    await tick();
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("down")));
    await m.refresh();
    expect(warn).toHaveBeenCalled();
  });

  it("starts polling an active build, then completes it", async () => {
    let n = 0;
    stubFetch((url) => {
      if (url === "/api/images/build/active") {
        n++;
        return jsonResponse(progress({ status: "success", progress_pct: 100 }));
      }
      return jsonResponse(status({ active_build: progress({ log_lines: ["a", "b"] }) }));
    });
    const m = make();
    await tick();
    expect($("images-build-log").textContent).toBe("a\nb");
    expect($("images-build-step-text").textContent).toBe("step");
    expect($("images-build-pct").textContent).toBe("40%");
    expect($("images-build-progress-bar").style.width).toBe("40%");
    await m.refresh();
    await tick(1500);
    expect(n).toBeGreaterThanOrEqual(1);
    expect($("images-build-progress-bar").style.background).toContain("accent-emerald");
  });

  it("finalises an interrupted build with or without a final status", async () => {
    const responses: Any[] = [
      status({ active_build: progress() }),
      status({ active_build: progress({ status: "failed" }) }),
    ];
    stubFetch(() => jsonResponse(responses.shift() ?? status()));
    const m = make();
    await tick();
    await m.refresh();
    expect($("images-build-progress-bar").style.background).toContain("crimson");

    stubFetch(() => jsonResponse(status({ active_build: progress() })));
    const m2 = make();
    await tick();
    stubFetch(() => jsonResponse(status()));
    await m2.refresh();
    await m2.refresh();
  });
});

describe("BuildImagesModal.handleProgressEvent", () => {
  it("polls while building and refreshes when done", async () => {
    const f = stubFetch((url) =>
      url === "/api/images/build/active"
        ? jsonResponse({}, { ok: false })
        : jsonResponse(status()),
    );
    const m = make();
    await tick();
    m.handleProgressEvent(progress({ current_step: "", log_lines: [] }) as never);
    expect($("images-build-step-text").textContent).toBe("Building...");
    m.handleProgressEvent(progress({ log_lines: undefined }) as never);
    await tick(1500);
    const before = f.mock.calls.length;
    m.handleProgressEvent(progress({ status: "idle" }) as never);
    await tick();
    expect(f.mock.calls.length).toBeGreaterThan(before);
  });

  it("copes with elements missing during an update", () => {
    stubFetch(() => jsonResponse(status()));
    for (const id of [
      "images-build-step-text",
      "images-build-pct",
      "images-build-progress-bar",
      "images-build-log",
    ]) {
      const m = make([id]);
      m.handleProgressEvent(progress({ log_lines: ["x"] }) as never);
      m.handleProgressEvent(progress({ status: "success" }) as never);
      m.handleProgressEvent(progress({ status: "failed" }) as never);
      m.handleProgressEvent(progress({ status: "idle" }) as never);
    }
  });

  it("keeps the progress bar untouched for idle builds", () => {
    stubFetch(() => jsonResponse(status()));
    const m = make();
    $("images-build-progress-bar").style.background = "red";
    m.handleProgressEvent(progress({ status: "idle" }) as never);
    expect($("images-build-progress-bar").style.background).toBe("red");
  });
});

describe("BuildImagesModal polling", () => {
  it("survives poll failures and stays quiet while building", async () => {
    let mode = "throw";
    stubFetch((url) => {
      if (url !== "/api/images/build/active") return jsonResponse(status());
      if (mode === "throw") throw new Error("x");
      return jsonResponse(progress());
    });
    const m = make();
    await tick();
    m.handleProgressEvent(progress() as never);
    await tick(1500);
    mode = "building";
    await tick(1500);
    expect($("images-build-pct").textContent).toBe("40%");
  });
});

describe("BuildImagesModal builds", () => {
  const bodyOf = (f: ReturnType<typeof stubFetch>, i: number) =>
    JSON.parse(f.mock.calls[i][1]!.body as string);

  it("triggers all, vm and container builds", async () => {
    const f = stubFetch((url) =>
      url === "/api/actions/build-image" ? jsonResponse(progress()) : jsonResponse(status()),
    );
    make();
    await tick();
    f.mockClear();
    $("btn-build-all-images").click();
    await tick();
    expect($("images-build-log").textContent).toBe("[BUILD] Initializing build request...\n");
    expect(bodyOf(f, 0)).toEqual({ target: "all", arch: "all" });
    $("btn-build-vm-images").click();
    $("btn-build-container-images").click();
    await tick();
    expect(bodyOf(f, 1).target).toBe("vm");
    expect(bodyOf(f, 2).target).toBe("container");
  });

  it("alerts on rejected and failed requests", async () => {
    stubFetch((url) =>
      url === "/api/actions/build-image" ? jsonResponse({ error: "busy" }, { ok: false }) : jsonResponse(status()),
    );
    make();
    await tick();
    $("btn-build-all-images").click();
    await tick();
    expect(window.alert).toHaveBeenCalledWith("Build failed to start: busy");

    stubFetch((url) =>
      url === "/api/actions/build-image"
        ? jsonResponse({}, { ok: false, statusText: "Bad" })
        : jsonResponse(status()),
    );
    $("btn-build-all-images").click();
    await tick();
    expect(window.alert).toHaveBeenCalledWith("Build failed to start: Bad");

    stubFetch((url) => {
      if (url === "/api/actions/build-image") throw new Error("net");
      return jsonResponse(status());
    });
    $("btn-build-all-images").click();
    await tick();
    expect(window.alert).toHaveBeenCalledWith(expect.stringContaining("Network error triggering build"));
  });

  it("works without progress panel and log", async () => {
    stubFetch(() => jsonResponse(progress()));
    make(["images-build-progress-panel", "images-build-log"]);
    await tick();
    $("btn-build-all-images").click();
    await tick();
  });

  it("cancels builds", async () => {
    const f = stubFetch(() => jsonResponse(status()));
    make();
    await tick();
    $("btn-cancel-image-build").click();
    await tick();
    expect(f.mock.calls.at(-1)![0]).toBe("/api/actions/build-image/cancel");
    expect($("images-build-step-text").textContent).toBe("Cancelling build...");

    make(["images-build-step-text"]);
    await tick();
    $("btn-cancel-image-build").click();
    await tick();

    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("x")));
    $("btn-cancel-image-build").click();
    await tick();
    expect(warn).toHaveBeenCalled();
  });
});
