import { vi } from "vitest";
import { initDom } from "../src/dom";
import { renderDashboardShell } from "../src/layout/renderDashboardShell";
import { resetState } from "../src/state";

/** Element ids the dashboard code supports but the current shell markup does not ship. */
const OPTIONAL_IDS = [
  "kpi-active-runners",
  "kpi-max-runners",
  "kpi-runners-bar",
  "kpi-min-runners-text",
  "kpi-runner-sizing",
  "kpi-queued-jobs",
  "kpi-queue-bar",
  "kpi-repos-monitored",
  "kpi-vm-ratio",
  "kpi-routing-bar",
  "kpi-routing-sub",
  "kpi-routing-health",
  "kpi-cache-size",
  "kpi-cache-bar",
  "kpi-queue-health",
  "kpi-cache-health",
  "runners-count-badge",
  "repos-count-badge",
  "queue-jobs-count-tag",
];

/** Renders the real dashboard shell (plus optional elements), resets the shared state and looks up the DOM refs. */
export function mountDashboard(): void {
  renderDashboardShell();
  for (const id of OPTIONAL_IDS) {
    if (!document.getElementById(id)) {
      const el = document.createElement("div");
      el.id = id;
      document.body.appendChild(el);
    }
  }
  resetState();
  initDom();
}

/** Builds a fetch Response-like object. */
export function jsonResponse(
  body: unknown,
  init: { ok?: boolean; status?: number; statusText?: string } = {},
): Response {
  return {
    ok: init.ok ?? true,
    status: init.status ?? 200,
    statusText: init.statusText ?? "OK",
    json: async () => body,
  } as Response;
}

/** Stubs global fetch with the given implementation and returns the spy. */
export function stubFetch(impl: (url: string, init?: RequestInit) => Response | Promise<Response>) {
  const spy = vi.fn(impl);
  vi.stubGlobal("fetch", spy);
  return spy;
}

/** Lets pending promise callbacks run. */
export async function flush(): Promise<void> {
  for (let i = 0; i < 5; i++) await Promise.resolve();
  await new Promise((r) => setTimeout(r, 0));
}

/**
 * Makes rendered output the same on every machine: fixes the clock at `now`
 * and formats dates and numbers locale-free (ISO dates, plain numbers), so
 * snapshots of rendered markup do not depend on the host's time zone or locale.
 */
export function pinClockAndLocale(now = "2026-01-05T12:00:00Z"): void {
  vi.useFakeTimers({ toFake: ["Date"], now: new Date(now) });
  vi.spyOn(Date.prototype, "toLocaleString").mockImplementation(function (this: Date) {
    return this.toISOString();
  });
  vi.spyOn(Date.prototype, "toLocaleTimeString").mockImplementation(function (this: Date) {
    return this.toISOString().slice(11, 19);
  });
  vi.spyOn(Number.prototype, "toLocaleString").mockImplementation(function (this: number) {
    return String(this);
  });
}
