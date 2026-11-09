import { afterEach, expect, it, vi } from "vitest";

const fns = vi.hoisted(() => ({
  initClearLogs: vi.fn(),
  initFilterControls: vi.fn(),
  initTableSortingControls: vi.fn(),
  initTerminalControls: vi.fn(),
  initViewControls: vi.fn(),
  initHeaderMenu: vi.fn(),
  initMaintenanceControls: vi.fn(),
  initSettingsModal: vi.fn(),
  initSpawnModal: vi.fn(),
  closeDrawer: vi.fn(),
}));
vi.mock("./controls", () => fns);
vi.mock("./headerMenu", () => ({ initHeaderMenu: fns.initHeaderMenu }));
vi.mock("./modals", () => fns);
vi.mock("./telemetry", () => ({ initTelemetryDrawer: () => fns.closeDrawer }));

import { initHandlers } from "./index";

afterEach(() => vi.useRealTimers());

it("binds every handler group and starts the uptime ticker", () => {
  vi.useFakeTimers();
  const tick = vi.spyOn(window, "setInterval");
  initHandlers();
  for (const name of [
    "initClearLogs",
    "initFilterControls",
    "initTableSortingControls",
    "initTerminalControls",
    "initViewControls",
    "initMaintenanceControls",
    "initSettingsModal",
    "initSpawnModal",
  ] as const) {
    expect(fns[name], name).toHaveBeenCalledOnce();
  }
  expect(fns.initHeaderMenu).toHaveBeenCalledWith(fns.closeDrawer);
  expect(tick).toHaveBeenCalledWith(expect.any(Function), 1000);
});
