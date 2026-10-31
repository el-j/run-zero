import { describe, expect, it, vi } from "vitest";

const m = vi.hoisted(() => ({
  order: [] as string[],
}));
const track = (name: string) => vi.fn(() => void m.order.push(name));

vi.mock("./layout/renderDashboardShell", () => ({ renderDashboardShell: track("shell") }));
vi.mock("./dom", () => ({ initDom: track("dom"), dom: {} }));
vi.mock("./view", () => ({
  restoreTabFilters: track("filters"),
  setViewMode: track("viewMode"),
  setActiveTab: track("tab"),
}));
vi.mock("./handlers", () => ({ initHandlers: track("handlers") }));
vi.mock("./ui", () => ({ setConnectionStatus: track("status") }));
vi.mock("./data", () => ({
  refreshState: track("refresh"),
  loadSettings: track("settings"),
  loadCacheStats: track("cache"),
}));
vi.mock("./stream", () => ({
  loadInitialLogs: vi.fn(async () => void m.order.push("logs")),
  startStreams: track("streams"),
}));
vi.mock("./components/BuildImagesModal", () => ({
  BuildImagesModal: class {
    constructor() {
      m.order.push("modal");
    }
  },
}));
vi.mock("./styles/theme.css", () => ({}));

import { hooks } from "./hooks";

describe("startApp", () => {
  it("bootstraps the dashboard in order and binds hooks", async () => {
    const { startApp } = await import("./app");
    await startApp();
    expect(m.order[0]).toBe("shell");
    expect(m.order).toContain("streams");
    expect(m.order.indexOf("logs")).toBeLessThan(m.order.indexOf("modal"));
    hooks.refreshState();
    hooks.loadCacheStats();
    expect(m.order.filter((x) => x === "refresh").length).toBeGreaterThan(1);
  });

  it("is invoked by main", async () => {
    m.order.length = 0;
    await import("./main");
    await vi.waitFor(() => expect(m.order).toContain("streams"));
  });
});
