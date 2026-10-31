import { beforeEach, describe, expect, it, vi } from "vitest";
import { jsonResponse, mountDashboard, stubFetch } from "../test/helpers";
import { fleet } from "../test/factories";
import { loadCacheStats, loadSettings, refreshState } from "./data";
import { dom, initDom } from "./dom";
import { state } from "./state";

const GiB = 1024 * 1024 * 1024;
const stats = (total_bytes: number, categories: unknown[] = []) => ({
  total_bytes,
  total_human: total_bytes ? "x" : "",
  categories,
});

beforeEach(() => {
  mountDashboard();
});

describe("loadCacheStats", () => {
  it.each([
    [0, "// Cache idle"],
    [GiB, "// Cache warm · low pressure"],
    [10 * GiB, "// Cache active · healthy"],
    [30 * GiB, "// Cache heavy · consider prune"],
  ])("sets health text for %d bytes", async (bytes, text) => {
    stubFetch(() => jsonResponse(stats(bytes)));
    await loadCacheStats();
    expect(dom.kpiCacheHealth!.textContent).toBe(text);
    expect(state.latestCacheStats).toBeTruthy();
  });

  it("renders sizes and category bars", async () => {
    stubFetch(() =>
      jsonResponse(
        stats(GiB, [
          { category: "pnpm", bytes: 100, human_readable: "100 B" },
          { category: "Unknown Cat", bytes: 1, human_readable: "1 B" },
          { category: "Go Pkg", bytes: 50, human_readable: "50 B" },
        ]),
      ),
    );
    await loadCacheStats();
    expect(dom.kpiCacheSize!.textContent).toBe("x");
    expect(dom.kpiCacheBar!.style.width).toBe("4%");
    expect(document.getElementById("sz-pnpm")!.textContent).toBe("100 B");
    expect(document.getElementById("bar-cache-pnpm")!.style.width).toBe("100%");
    expect(document.getElementById("bar-cache-go-pkg")!.style.width).toBe("50%");
  });

  it("falls back to defaults for empty stats", async () => {
    stubFetch(() => jsonResponse({ total_bytes: 0, categories: [] }));
    await loadCacheStats();
    expect(dom.kpiCacheSize!.textContent).toBe("0 B");
    stubFetch(() => jsonResponse({ categories: [] }));
    await loadCacheStats();
    expect(dom.kpiCacheHealth!.textContent).toBe("// Cache idle");
  });

  it("works without any elements", async () => {
    document.body.innerHTML = "";
    initDom();
    stubFetch(() => jsonResponse(stats(GiB, [{ category: "a", bytes: 1, human_readable: "1" }])));
    await loadCacheStats();
    expect(state.latestCacheStats).toBeTruthy();
  });

  it("warns on failure", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    stubFetch(() => jsonResponse({}, { ok: false }));
    await loadCacheStats();
    expect(warn).toHaveBeenCalled();
  });
});

describe("loadSettings", () => {
  it("renders the summary", async () => {
    const s = {
      max_runners: 5,
      min_runners: 1,
      runner_backend: "vm",
      auto_route_vm: true,
      cache_enabled: true,
    };
    stubFetch(() => jsonResponse(s));
    expect(await loadSettings()).toEqual(s);
    expect(dom.cfgMaxRunners!.textContent).toBe("5");
    expect(dom.cfgMinRunners!.textContent).toBe("1");
    expect(dom.cfgRunnerBackend!.textContent).toBe("vm");
    expect(dom.cfgAutoRouteVm!.textContent).toBe("enabled");
    expect(dom.cfgCacheEnabled!.textContent).toBe("active");
    expect(state.latestSettings).toEqual(s);
  });

  it("uses defaults", async () => {
    stubFetch(() => jsonResponse({}));
    await loadSettings();
    expect(dom.cfgMaxRunners!.textContent).toBe("3");
    expect(dom.cfgMinRunners!.textContent).toBe("0");
    expect(dom.cfgRunnerBackend!.textContent).toBe("auto");
    expect(dom.cfgAutoRouteVm!.textContent).toBe("disabled");
    expect(dom.cfgCacheEnabled!.textContent).toBe("disabled");
  });

  it("works without elements", async () => {
    document.body.innerHTML = "";
    initDom();
    stubFetch(() => jsonResponse({}));
    expect(await loadSettings()).toEqual({});
  });

  it("returns null on failure", async () => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
    stubFetch(() => jsonResponse({}, { ok: false }));
    expect(await loadSettings()).toBeNull();
  });
});

describe("refreshState", () => {
  it("marks the connection online and renders", async () => {
    stubFetch(() => jsonResponse(fleet({ runners: [], queued_jobs: [] })));
    await refreshState();
    expect(dom.connectionText!.textContent).toBe("LIVE OBSERVABILITY");
  });

  it("marks the connection as errored", async () => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
    stubFetch(() => jsonResponse({}, { ok: false }));
    await refreshState();
    expect(dom.connectionText!.textContent).toBe("RECONNECTING...");
  });
});
