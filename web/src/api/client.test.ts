import { describe, expect, it, vi } from "vitest";
import { FakeEventSource } from "../../test/setup";
import { jsonResponse, stubFetch } from "../../test/helpers";
import { client, RunZeroClient } from "./client";

const bad = (body: unknown = { error: "boom" }, status = 500) =>
  jsonResponse(body, { ok: false, status, statusText: "Server Error" });
const unparsable = () =>
  ({
    ok: false,
    status: 502,
    statusText: "Bad Gateway",
    json: async () => {
      throw new Error("not json");
    },
  }) as unknown as Response;

describe("RunZeroClient GET endpoints", () => {
  it("returns parsed bodies using the base URL", async () => {
    const fetchSpy = stubFetch(() => jsonResponse({ ok: 1 }));
    const c = new RunZeroClient("http://x");
    await c.getFleet();
    await c.getSettings();
    await c.getCacheStats();
    expect(fetchSpy.mock.calls.map((c) => c[0])).toEqual([
      "http://x/api/fleet",
      "http://x/api/settings",
      "http://x/api/cache",
    ]);
  });

  it("throws with status text on failure", async () => {
    stubFetch(() => bad());
    await expect(client.getFleet()).rejects.toThrow("Failed to fetch fleet state: 500 Server Error");
    await expect(client.getSettings()).rejects.toThrow("Failed to fetch settings");
    await expect(client.getCacheStats()).rejects.toThrow("Failed to fetch cache stats");
  });
});

describe("RunZeroClient POST endpoints", () => {
  const calls: Array<[string, () => Promise<unknown>]> = [
    ["repo-priority", () => client.updateRepoPriority(["a"], ["b"])],
    ["workflow", () => client.triggerWorkflowAction("o/r", 1, "cancel")],
    ["runner", () => client.controlRunner("start", { repo: "o/r" })],
    ["runner default options", () => client.controlRunner("stop")],
    ["settings", () => client.updateSettings({ max_runners: 1 })],
    ["purge", () => client.purgeCache({ all: true })],
    ["purge default options", () => client.purgeCache()],
  ];

  for (const [name, call] of calls) {
    it(`${name}: succeeds`, async () => {
      const fetchSpy = stubFetch(() => jsonResponse({ success: true }));
      await expect(call()).resolves.toEqual({ success: true });
      expect(fetchSpy.mock.calls[0][1]?.method).toBe("POST");
    });

    it(`${name}: surfaces the server error`, async () => {
      stubFetch(() => bad());
      await expect(call()).rejects.toThrow("boom");
    });

    it(`${name}: falls back to the status text`, async () => {
      stubFetch(() => unparsable());
      await expect(call()).rejects.toThrow("Bad Gateway");
    });

    it(`${name}: falls back to the HTTP status`, async () => {
      stubFetch(() => bad({}, 418));
      await expect(call()).rejects.toThrow("HTTP 418");
    });
  }
});

describe("subscribeSSE", () => {
  it("routes events to callbacks and closes the source", () => {
    const cb = {
      onFleet: vi.fn(),
      onActivity: vi.fn(),
      onBuildProgress: vi.fn(),
      onError: vi.fn(),
    };
    const close = new RunZeroClient("http://x").subscribeSSE(cb);
    const es = FakeEventSource.instances[0];
    expect(es.url).toBe("http://x/api/stream");
    es.emit("fleet", '{"a":1}');
    es.emit("activity", "hello");
    es.emit("build_progress", '{"p":1}');
    es.onerror?.(new Event("error"));
    expect(cb.onFleet).toHaveBeenCalledWith({ a: 1 });
    expect(cb.onActivity).toHaveBeenCalledWith("hello");
    expect(cb.onBuildProgress).toHaveBeenCalledWith({ p: 1 });
    expect(cb.onError).toHaveBeenCalled();
    close();
    expect(es.closed).toBe(true);
  });

  it("logs unparsable payloads and tolerates missing callbacks", () => {
    const err = vi.spyOn(console, "error").mockImplementation(() => {});
    client.subscribeSSE({});
    const es = FakeEventSource.instances[0];
    es.emit("fleet", "{bad");
    es.emit("build_progress", "{bad");
    expect(err).toHaveBeenCalledTimes(2);
    es.emit("fleet", "{}");
    es.emit("activity", "x");
    es.emit("build_progress", "{}");
    es.onerror?.(new Event("error"));
  });
});
