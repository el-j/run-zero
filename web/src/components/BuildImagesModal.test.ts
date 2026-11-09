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
    stubFetch(() =>
      jsonResponse(
        status({
          vm_images: [
            img({ kind: "orbstack-vm", name: "vm" }),
            img({ name: "c", status: "stale", size_human: undefined }),
            img({ name: "d", status: "missing" }),
          ],
        }),
      ),
    );
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
      url === "/api/images/build/active" ? jsonResponse({}, { ok: false }) : jsonResponse(status()),
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
    expect(bodyOf(f, 1)).toEqual({ target: "vm", arch: "all" });
    expect(bodyOf(f, 2)).toEqual({ target: "container", arch: "all" });
  });

  it("alerts on rejected and failed requests", async () => {
    stubFetch((url) =>
      url === "/api/actions/build-image"
        ? jsonResponse({ error: "busy" }, { ok: false })
        : jsonResponse(status()),
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
    expect(window.alert).toHaveBeenCalledWith(
      expect.stringContaining("Network error triggering build"),
    );
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

/** A fetch stub answering per URL; `calls` lists every requested URL. */
function router(routes: Record<string, () => Response>) {
  const calls: string[] = [];
  const f = stubFetch((url) => {
    calls.push(url);
    const handler = routes[url];
    if (!handler) throw new Error(`unexpected fetch ${url}`);
    return handler();
  });
  return { f, calls, count: (url: string) => calls.filter((c) => c === url).length };
}

describe("BuildImagesModal output", () => {
  it("renders every kind of image card", async () => {
    stubFetch(() =>
      jsonResponse(
        status({
          vm_images: [
            img({ kind: "orbstack-vm", name: "vm-a", version: "2.3", status: "ready" }),
            img({ kind: "orbstack-vm", name: "vm-b", arch: "amd64", status: "stale" }),
          ],
          container_images: [img({ name: "c-a", size_human: "1 GB", status: "missing" })],
          all_ready: false,
        }),
      ),
    );
    make();
    $("badge-images-icon").textContent = "";
    await tick();
    expect($("images-status-grid").innerHTML).toMatchSnapshot();
    expect($("badge-images-status").textContent).toBe("1/3");
    expect($("badge-images-status").className).toBe("badge badge-warning font-mono");
    expect($("badge-images-status").style.color).toBe("var(--solar, #f59e0b)");
    expect($("badge-images-icon").textContent).toBe("⚡");
  });

  it("shows a ready fleet of images", async () => {
    stubFetch(() => jsonResponse(status()));
    make();
    $("badge-images-icon").textContent = "";
    await tick();
    expect($("badge-images-status").className).toBe("badge badge-success font-mono");
    expect($("badge-images-status").style.color).toBe("var(--accent-emerald, #10b981)");
    expect($("badge-images-icon").textContent).toBe("✓");
  });

  it.each(["badge-images-icon", "images-status-grid"])(
    "refreshes cleanly without #%s",
    async (id) => {
      const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
      for (const ready of [true, false]) {
        stubFetch(() => jsonResponse(status({ all_ready: ready })));
        const m = make([id]);
        await m.refresh();
      }
      expect(warn).not.toHaveBeenCalled();
    },
  );

  it("leaves the header badge alone without a status grid", async () => {
    stubFetch(() => jsonResponse(status()));
    make(["images-status-grid"]);
    $("badge-images-status").textContent = "before";
    await tick();
    expect($("badge-images-status").textContent).toBe("before");
  });

  it("renders an empty status as an empty grid", async () => {
    stubFetch(() => jsonResponse({ all_ready: true }));
    make();
    await tick();
    expect($("images-status-grid").innerHTML).toBe("");
    expect($("badge-images-status").textContent).toBe("0/0");
  });

  it("leaves the grid alone when the status request fails", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    stubFetch(() => jsonResponse({ error: "x" }, { ok: false }));
    $("images-status-grid");
    make();
    $("images-status-grid").innerHTML = "before";
    await tick();
    expect($("images-status-grid").innerHTML).toBe("before");
    stubFetch(() => Promise.reject(new Error("offline")));
    const m = make();
    await m.refresh();
    expect(warn).toHaveBeenCalledWith("Failed fetching image status:", expect.any(Error));
  });

  it("refreshes when the closed dialog opens", async () => {
    const r = router({ "/api/images": () => jsonResponse(status()) });
    const m = make();
    await tick();
    expect(r.count("/api/images")).toBe(1);
    m.open();
    await tick();
    expect(r.count("/api/images")).toBe(2);
  });

  it("does not show a finished build it never tracked", async () => {
    stubFetch(() =>
      jsonResponse(status({ active_build: progress({ status: "failed", progress_pct: 77 }) })),
    );
    make();
    await tick();
    expect($("images-build-pct").textContent).not.toBe("77%");
  });

  it("polls an active build every 1.5 s, once, until it finishes", async () => {
    let state = "building";
    const r = router({
      "/api/images": () => jsonResponse(status()),
      "/api/images/build/active": () =>
        jsonResponse(progress({ status: state, progress_pct: state === "building" ? 50 : 100 })),
    });
    const m = make();
    await tick();
    m.handleProgressEvent(progress() as never);
    m.handleProgressEvent(progress() as never); // a second event must not start a second poller
    await tick(1499);
    expect(r.count("/api/images/build/active")).toBe(0);
    await tick(1);
    expect(r.count("/api/images/build/active")).toBe(1);
    expect($("images-build-pct").textContent).toBe("50%");
    await tick(1500);
    expect(r.count("/api/images/build/active")).toBe(2);

    state = "success";
    const statusBefore = r.count("/api/images");
    await tick(1500);
    expect($("images-build-progress-bar").style.background).toBe("var(--accent-emerald, #10b981)");
    expect(r.count("/api/images")).toBe(statusBefore + 1); // refreshed once the build finished
    await tick(4500);
    expect(r.count("/api/images/build/active")).toBe(3); // and stopped polling
  });

  it("keeps the last progress when a poll is rejected", async () => {
    router({
      "/api/images": () => jsonResponse(status()),
      "/api/images/build/active": () => jsonResponse(progress({ progress_pct: 99 }), { ok: false }),
    });
    const m = make();
    await tick();
    m.handleProgressEvent(progress({ progress_pct: 10 }) as never);
    await tick(1500);
    expect($("images-build-pct").textContent).toBe("10%");
  });

  it("stops polling and refreshes when a pushed event ends the build", async () => {
    const r = router({
      "/api/images": () => jsonResponse(status()),
      "/api/images/build/active": () => jsonResponse(progress()),
    });
    const m = make();
    await tick();
    m.handleProgressEvent(progress() as never);
    const statusBefore = r.count("/api/images");
    m.handleProgressEvent(progress({ status: "failed" }) as never);
    await tick(3000);
    expect(r.count("/api/images/build/active")).toBe(0);
    expect(r.count("/api/images")).toBe(statusBefore + 1);
    expect($("images-build-progress-bar").style.background).toBe("var(--crimson, #ef4444)");
  });

  it("resumes tracking a build found on refresh and finalises it on the next refresh", async () => {
    let active: Any | undefined = progress({ progress_pct: 30 });
    const r = router({
      "/api/images": () => jsonResponse(status({ active_build: active })),
      "/api/images/build/active": () => jsonResponse(progress({ progress_pct: 30 })),
    });
    const m = make();
    await tick();
    expect($("images-build-pct").textContent).toBe("30%");
    active = progress({ status: "success", progress_pct: 100 });
    await m.refresh();
    expect($("images-build-pct").textContent).toBe("100%");
    const polls = r.count("/api/images/build/active");
    await tick(3000);
    expect(r.count("/api/images/build/active")).toBe(polls);

    // A tracked build that vanished from the status stops polling and keeps its last progress.
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    active = progress({ progress_pct: 60 });
    await m.refresh();
    active = undefined;
    await m.refresh();
    expect($("images-build-pct").textContent).toBe("60%");
    expect(warn).not.toHaveBeenCalled();
    const after = r.count("/api/images/build/active");
    await tick(3000);
    expect(r.count("/api/images/build/active")).toBe(after);
  });

  it("forgets a build once a pushed event says it ended", async () => {
    let active: Any | undefined;
    router({ "/api/images": () => jsonResponse(status({ active_build: active })) });
    const m = make();
    await tick();
    m.handleProgressEvent(progress({ status: "success", progress_pct: 100 }) as never);
    await tick();
    active = progress({ status: "failed", progress_pct: 88 });
    await m.refresh();
    expect($("images-build-pct").textContent).toBe("100%");
  });

  it("counts a build as running from the moment it is requested", async () => {
    let answer!: (r: Response) => void;
    let active: Any | undefined;
    router({
      "/api/images": () => jsonResponse(status({ active_build: active })),
      "/api/actions/build-image": () =>
        new Promise<Response>((r) => (answer = r)) as unknown as Response,
    });
    const m = make();
    await tick();
    $("btn-build-all-images").click();
    await tick();
    // The build ended before its request even answered; a refresh now shows that result.
    active = progress({ status: "failed", progress_pct: 3 });
    await m.refresh();
    expect($("images-build-pct").textContent).toBe("3%");
    answer(jsonResponse(progress({ status: "failed", progress_pct: 3 })));
    await tick();
  });

  it("starts a build without a progress panel or log", async () => {
    router({
      "/api/images": () => jsonResponse(status()),
      "/api/actions/build-image": () => jsonResponse(progress()),
    });
    make(["images-build-progress-panel", "images-build-log"]);
    await tick();
    $("btn-build-all-images").click();
    await tick();
    expect(window.alert).not.toHaveBeenCalled();
  });

  it("cancels without a step label", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    router({
      "/api/images": () => jsonResponse(status()),
      "/api/actions/build-image/cancel": () => jsonResponse({}),
    });
    make(["images-build-step-text"]);
    await tick();
    $("btn-cancel-image-build").click();
    await tick();
    expect(warn).not.toHaveBeenCalled();
  });

  it("keeps the log when a progress update has no lines", () => {
    stubFetch(() => jsonResponse(status()));
    const m = make();
    $("images-build-log").textContent = "kept";
    m.handleProgressEvent(progress({ log_lines: [] }) as never);
    expect($("images-build-log").textContent).toBe("kept");
  });

  it("posts a build request and tracks the build it starts", async () => {
    const r = router({
      "/api/images": () => jsonResponse(status()),
      "/api/actions/build-image": () => jsonResponse(progress({ progress_pct: 5 })),
      "/api/images/build/active": () => jsonResponse(progress({ progress_pct: 6 })),
    });
    make();
    await tick();
    $("images-build-progress-panel").classList.add("hidden");
    $("btn-build-vm-images").click();
    expect($("images-build-progress-panel").classList.contains("hidden")).toBe(false);
    await tick();
    const init = r.f.mock.calls.find((c) => c[0] === "/api/actions/build-image")![1]!;
    expect(init.method).toBe("POST");
    expect(init.headers).toEqual({ "Content-Type": "application/json" });
    expect(JSON.parse(init.body as string)).toEqual({ target: "vm", arch: "all" });
    expect($("images-build-pct").textContent).toBe("5%");
    await tick(1500);
    expect($("images-build-pct").textContent).toBe("6%");
  });

  it.each([
    ["rejected", () => jsonResponse({ error: "busy" }, { ok: false })],
    ["unreachable", () => Promise.reject(new Error("net")) as unknown as Response],
  ])("does not track a %s build request", async (_name, answer) => {
    let active: Any | undefined;
    router({
      "/api/images": () => jsonResponse(status({ active_build: active })),
      "/api/actions/build-image": answer,
    });
    const m = make();
    await tick();
    $("btn-build-all-images").click();
    await tick();
    active = progress({ status: "failed", progress_pct: 88 });
    await m.refresh();
    expect($("images-build-pct").textContent).not.toBe("88%");
  });

  it("cancels with a POST", async () => {
    const r = router({
      "/api/images": () => jsonResponse(status()),
      "/api/actions/build-image/cancel": () => jsonResponse({}),
    });
    make();
    await tick();
    $("btn-cancel-image-build").click();
    await tick();
    expect(r.f.mock.calls.find((c) => c[0] === "/api/actions/build-image/cancel")![1]).toEqual({
      method: "POST",
    });
  });

  it("warns when cancelling fails", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    router({
      "/api/images": () => jsonResponse(status()),
      "/api/actions/build-image/cancel": () =>
        Promise.reject(new Error("x")) as unknown as Response,
    });
    make();
    await tick();
    $("btn-cancel-image-build").click();
    await tick();
    expect(warn).toHaveBeenCalledWith("Cancel build error:", expect.any(Error));
  });
});
