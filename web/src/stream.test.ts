import { beforeEach, describe, expect, it, vi } from "vitest";
import { FakeEventSource } from "../test/setup";
import { jsonResponse, mountDashboard, stubFetch } from "../test/helpers";
import { fleet } from "../test/factories";
import { dom } from "./dom";

const data = vi.hoisted(() => ({ refreshState: vi.fn(), loadCacheStats: vi.fn() }));
vi.mock("./data", () => data);
const renderState = vi.hoisted(() => vi.fn());
vi.mock("./render/state", () => ({ renderState }));

import type { BuildImagesModal } from "./components/BuildImagesModal";
import { loadInitialLogs, startStreams } from "./stream";

beforeEach(() => {
  mountDashboard();
});

describe("loadInitialLogs", () => {
  it("appends buffered logs", async () => {
    const f = stubFetch(() =>
      jsonResponse({ logs: [{ message: "one", timestamp: "t1" }, { message: "two" }] }),
    );
    await loadInitialLogs();
    expect(f).toHaveBeenCalledWith("/api/logs");
    expect(dom.logTerminal!.children).toHaveLength(2);
  });

  it("ignores failed responses and malformed bodies", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    stubFetch(() => jsonResponse({ logs: [{ message: "from an error page" }] }, { ok: false }));
    await loadInitialLogs();
    stubFetch(() => jsonResponse({}));
    await loadInitialLogs();
    stubFetch(() => jsonResponse({ logs: "nope" }));
    await loadInitialLogs();
    expect(dom.logTerminal!.children).toHaveLength(0);
    expect(warn).not.toHaveBeenCalled();
  });

  it("warns when the request throws", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    stubFetch(() => Promise.reject(new Error("offline")));
    await loadInitialLogs();
    expect(warn).toHaveBeenCalledWith("Could not load initial logs:", expect.any(Error));
  });
});

describe("startStreams", () => {
  it("wires SSE callbacks and timers", () => {
    vi.useFakeTimers();
    const modal = { handleProgressEvent: vi.fn(), refresh: vi.fn() } as unknown as BuildImagesModal;
    startStreams(modal);
    const es = FakeEventSource.instances[0];

    es.emit("fleet", JSON.stringify(fleet({})));
    expect(renderState).toHaveBeenCalled();
    expect(dom.connectionText!.textContent).toBe("LIVE OBSERVABILITY");
    expect(dom.connectionBadge!.classList.contains("online")).toBe(true);
    es.emit("activity", "hello");
    expect(dom.logTerminal!.children).toHaveLength(1);
    es.emit("build_progress", '{"x":1}');
    expect(modal.handleProgressEvent).toHaveBeenCalledWith({ x: 1 });
    es.onerror?.(new Event("error"));
    expect(dom.connectionText!.textContent).toBe("RECONNECTING...");
    expect(dom.connectionBadge!.classList.contains("error")).toBe(true);

    vi.advanceTimersByTime(20000);
    expect(data.refreshState).toHaveBeenCalledTimes(2);
    expect(data.loadCacheStats).toHaveBeenCalledTimes(1);
    expect(modal.refresh).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });
});
