import { afterEach, describe, expect, it, vi } from "vitest";
import { mountDashboard } from "../test/helpers";
import { dom, initDom } from "./dom";
import { hooks } from "./hooks";
import { renderDashboardShell } from "./layout/renderDashboardShell";
import { createState, resetState, state } from "./state";
import { setConnectionStatus, showToast } from "./ui";

describe("dom", () => {
  it("looks up shell elements and tolerates re-init", () => {
    mountDashboard();
    expect(dom.connectionBadge).toBeInstanceOf(HTMLElement);
    document.getElementById("kpi-cache-bar")?.remove();
    initDom();
    expect(dom.kpiCacheBar).toBeNull();
  });
});

describe("layout", () => {
  it("renders the shell once", () => {
    renderDashboardShell();
    const html = document.body.innerHTML;
    expect(document.body.classList.contains("theme-dark")).toBe(true);
    expect(html).toContain("icon.svg");
    document.body.insertAdjacentHTML("beforeend", "<i id=marker></i>");
    renderDashboardShell();
    expect(document.getElementById("marker")).not.toBeNull();
  });
});

describe("hooks", () => {
  it("has resolvable default no-ops", async () => {
    await expect(hooks.refreshState()).resolves.toBeUndefined();
    await expect(hooks.loadCacheStats()).resolves.toBeUndefined();
  });
});

describe("state", () => {
  it("creates defaults and honors persisted preferences", () => {
    expect(createState().currentViewMode).toBe("cards");
    expect(createState().terminalHeightPx).toBe(180);
    localStorage.setItem("runzero_display_mode", "table");
    localStorage.setItem("runzero_terminal_height_px", "250");
    const s = createState();
    expect(s.currentViewMode).toBe("table");
    expect(s.terminalHeightPx).toBe(250);
  });

  it("resetState restores defaults in place", () => {
    state.currentTab = "jobs";
    resetState();
    expect(state.currentTab).toBe("runners");
  });
});

describe("ui", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("showToast adds, fades and removes a toast", () => {
    vi.useFakeTimers();
    document.body.innerHTML = '<div id="toast-container"></div>';
    showToast("hello");
    showToast("bad", true);
    const toasts = document.querySelectorAll<HTMLElement>(".toast");
    expect(toasts).toHaveLength(2);
    expect(toasts[0].style.borderColor).toBe("");
    expect(toasts[1].style.borderColor).toBe("var(--crimson)");
    vi.advanceTimersByTime(3499);
    expect(toasts[0].style.opacity).toBe("");
    vi.advanceTimersByTime(1);
    expect(toasts[0].style.opacity).toBe("0");
    expect(toasts[0].style.transform).toBe("translateY(10px)");
    expect(toasts[0].style.transition).toBe("all 0.3s ease");
    vi.advanceTimersByTime(300);
    expect(document.querySelectorAll(".toast")).toHaveLength(0);
  });

  it("showToast is a no-op without a container", () => {
    expect(() => showToast("x")).not.toThrow();
  });

  it("setConnectionStatus updates the badge", () => {
    mountDashboard();
    setConnectionStatus("connecting", "CONNECTING...");
    expect(dom.connectionText!.textContent).toBe("CONNECTING...");
    expect(dom.connectionBadge.classList.contains("connecting")).toBe(true);
    setConnectionStatus("error", "ERR");
    expect(dom.connectionBadge.classList.contains("error")).toBe(true);
    setConnectionStatus("online", "OK");
    expect(dom.connectionBadge.className).toBe("badge badge-pulse online");
  });

  it("setConnectionStatus is a no-op without elements", () => {
    mountDashboard();
    document.getElementById("connection-status-text")!.remove();
    initDom();
    expect(() => setConnectionStatus("online", "x")).not.toThrow();
  });
});
