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
    await expect(client.getFleet()).rejects.toThrow(
      "Failed to fetch fleet state: 500 Server Error",
    );
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
    expect(err).toHaveBeenNthCalledWith(
      1,
      "Failed to parse fleet SSE data",
      expect.any(SyntaxError),
    );
    expect(err).toHaveBeenNthCalledWith(
      2,
      "Failed to parse build_progress SSE data",
      expect.any(SyntaxError),
    );
    es.emit("fleet", "{}");
    es.emit("activity", "x");
    es.emit("build_progress", "{}");
    es.onerror?.(new Event("error"));
    expect(err).toHaveBeenCalledTimes(2); // valid events without a callback are simply dropped
  });
});

describe("RunZeroClient POST requests", () => {
  it.each([
    [
      "updateRepoPriority",
      (c: RunZeroClient) => c.updateRepoPriority(["o/a"], ["o/b"]),
      "/api/actions/repo-priority",
      { priority: ["o/a"], paused: ["o/b"] },
    ],
    [
      "triggerWorkflowAction",
      (c: RunZeroClient) => c.triggerWorkflowAction("o/a", 7, "rerun"),
      "/api/actions/workflow",
      { repo: "o/a", run_id: 7, action: "rerun" },
    ],
    [
      "controlRunner",
      (c: RunZeroClient) =>
        c.controlRunner("open-terminal", {
          runnerId: "r1",
          repo: "o/a",
          arch: "arm64",
          backend: "docker",
        }),
      "/api/actions/runner",
      { action: "open-terminal", runner_id: "r1", repo: "o/a", arch: "arm64", backend: "docker" },
    ],
    [
      "updateSettings",
      (c: RunZeroClient) => c.updateSettings({ max_runners: 2 }),
      "/api/settings",
      { max_runners: 2 },
    ],
    [
      "purgeCache",
      (c: RunZeroClient) => c.purgeCache({ all: true }),
      "/api/cache/purge",
      { all: true },
    ],
    ["pruneRunners", (c: RunZeroClient) => c.pruneRunners(), "/api/actions/prune", {}],
  ] as const)("%s posts JSON to its endpoint", async (_name, call, path, body) => {
    const f = stubFetch(() => jsonResponse({ success: true }));
    await call(new RunZeroClient("http://x"));
    const [url, init] = f.mock.calls[0];
    expect(url).toBe(`http://x${path}`);
    expect(init).toEqual({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  });
});
