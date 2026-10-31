import { beforeEach, describe, expect, it, vi } from "vitest";
import { mountDashboard } from "../test/helpers";
import { dom, initDom } from "./dom";
import { toggleSort, updateSortHeaderIndicators } from "./sorting";
import { filterStorageKeys, state } from "./state";
import {
  appendLog,
  applyTerminalHeight,
  clampTerminalHeight,
  initTerminalSplitter,
  toggleTerminal,
} from "./terminal";
import { restoreTabFilters, setActiveTab, setViewMode } from "./view";

beforeEach(() => {
  mountDashboard();
});

/** Removes the elements with the given ids and refreshes the DOM refs. */
function removeIds(...ids: string[]) {
  ids.forEach((id) => document.getElementById(id)?.remove());
  initDom();
}

describe("sorting", () => {
  it("toggleSort flips direction on the same key and resets on a new key", () => {
    const s = { key: "a", dir: "asc" as "asc" | "desc" };
    toggleSort(s, "a");
    expect(s).toEqual({ key: "a", dir: "desc" });
    toggleSort(s, "a");
    expect(s.dir).toBe("asc");
    s.dir = "desc";
    toggleSort(s, "b");
    expect(s).toEqual({ key: "b", dir: "asc" });
  });

  it("updateSortHeaderIndicators marks the active header of each table", () => {
    document.body.innerHTML = `
      <table>
        <th class="sortable-col sort-asc" data-table="runners" data-sort-key="uptime"></th>
        <th class="sortable-col" data-table="runners" data-sort-key="name"></th>
        <th class="sortable-col" data-table="queue" data-sort-key="position"></th>
        <th class="sortable-col" data-table="jobs" data-sort-key="completed"></th>
        <th class="sortable-col" data-table="repos" data-sort-key="rank"></th>
        <th class="sortable-col" data-table="other" data-sort-key="x"></th>
        <th class="sortable-col" data-table="runners"></th>
      </table>`;
    state.queueSort.key = "position";
    updateSortHeaderIndicators();
    const cls = [...document.querySelectorAll("th")].map((t) => t.className);
    expect(cls[0]).toBe("sortable-col sort-desc");
    expect(cls[1]).toBe("sortable-col");
    expect(cls[2]).toBe("sortable-col sort-asc");
    expect(cls[3]).toBe("sortable-col sort-desc");
    expect(cls[4]).toBe("sortable-col sort-asc");
    expect(cls[5]).toBe("sortable-col");
    expect(cls[6]).toBe("sortable-col");
  });
});

describe("view", () => {
  it("restoreTabFilters loads persisted values and defaults to empty", () => {
    localStorage.setItem(filterStorageKeys.runners, "r");
    localStorage.setItem(filterStorageKeys.queue, "q");
    localStorage.setItem(filterStorageKeys.jobs, "j");
    localStorage.setItem(filterStorageKeys.repos, "p");
    restoreTabFilters();
    expect(dom.runnersSearchInput!.value).toBe("r");
    expect(dom.queueSearchInput!.value).toBe("q");
    expect(dom.jobsSearchInput!.value).toBe("j");
    expect(dom.repoSearchInput!.value).toBe("p");
    localStorage.clear();
    restoreTabFilters();
    expect(dom.runnersSearchInput!.value).toBe("");
    expect(dom.queueSearchInput!.value).toBe("");
    expect(dom.jobsSearchInput!.value).toBe("");
    expect(dom.repoSearchInput!.value).toBe("");
  });

  it("restoreTabFilters tolerates missing inputs", () => {
    removeIds("runners-search-input", "queue-search-input", "jobs-search-input", "repo-search-input");
    expect(() => restoreTabFilters()).not.toThrow();
  });

  it("setViewMode toggles cards/table", () => {
    setViewMode("table");
    expect(localStorage.getItem("runzero_display_mode")).toBe("table");
    expect(state.currentViewMode).toBe("table");
    expect(dom.viewModeTable!.classList.contains("active")).toBe(true);
    expect(dom.runnersCardsView!.classList.contains("hidden")).toBe(true);
    expect(dom.runnersTableView!.classList.contains("hidden")).toBe(false);
    expect(dom.jobsTableView!.classList.contains("hidden")).toBe(false);
    expect(dom.selectViewModeSetting!.value).toBe("table");
    expect(document.querySelector(".dashboard-container")!.classList.contains("view-mode-table")).toBe(true);
    setViewMode("cards");
    expect(dom.viewModeCards!.classList.contains("active")).toBe(true);
    expect(dom.runnersCardsView!.classList.contains("hidden")).toBe(false);
    expect(dom.queueTableView!.classList.contains("hidden")).toBe(true);
    expect(dom.reposTableView!.classList.contains("hidden")).toBe(true);
    expect(dom.jobsCardsView!.classList.contains("hidden")).toBe(false);
  });

  it("setViewMode tolerates a missing shell", () => {
    document.body.innerHTML = "";
    initDom();
    expect(() => setViewMode("table")).not.toThrow();
  });

  it("setActiveTab shows only the chosen tab", () => {
    setActiveTab("jobs");
    expect(state.currentTab).toBe("jobs");
    expect(dom.tabBtnJobs!.classList.contains("active")).toBe(true);
    expect(dom.tabContentJobs!.classList.contains("hidden")).toBe(false);
    expect(dom.tabActionsJobs!.classList.contains("hidden")).toBe(false);
    expect(dom.tabBtnRunners!.classList.contains("active")).toBe(false);
    expect(dom.tabContentRunners!.classList.contains("hidden")).toBe(true);
    document.body.innerHTML = "";
    initDom();
    expect(() => setActiveTab("queue")).not.toThrow();
  });
});

describe("terminal", () => {
  it("clampTerminalHeight bounds by the workspace height", () => {
    const col = dom.workspaceMainColumn!;
    Object.defineProperty(col, "clientHeight", { configurable: true, value: 800 });
    expect(clampTerminalHeight(50)).toBe(96);
    expect(clampTerminalHeight(200.4)).toBe(200);
    expect(clampTerminalHeight(9999)).toBe(580);
    Object.defineProperty(col, "clientHeight", { configurable: true, value: 0 });
    expect(clampTerminalHeight(9999)).toBe(120);
    removeIds("workspace-main-column");
    expect(clampTerminalHeight(333)).toBe(333);
  });

  it("applyTerminalHeight persists and sets the CSS variable", () => {
    Object.defineProperty(dom.workspaceMainColumn!, "clientHeight", { configurable: true, value: 800 });
    applyTerminalHeight(300);
    expect(dom.workspaceMainColumn!.style.getPropertyValue("--terminal-height")).toBe("300px");
    expect(localStorage.getItem("runzero_terminal_height_px")).toBe("300");
    removeIds("workspace-main-column");
    expect(() => applyTerminalHeight(10)).not.toThrow();
  });

  it("toggleTerminal expands and collapses", () => {
    Object.defineProperty(dom.workspaceMainColumn!, "clientHeight", { configurable: true, value: 800 });
    toggleTerminal();
    expect(state.terminalExpanded).toBe(true);
    expect(dom.btnTerminalExpandText!.textContent).toBe("COLLAPSE");
    expect(dom.btnTerminalExpandIcon!.textContent).toBe("▼");
    expect(state.terminalHeightPx).toBe(320);
    toggleTerminal();
    expect(dom.btnTerminalExpandText!.textContent).toBe("EXPAND");
    expect(state.terminalHeightPx).toBe(180);
    removeIds("btn-terminal-expand-icon", "btn-terminal-expand-text");
    expect(() => toggleTerminal()).not.toThrow();
  });

  it("initTerminalSplitter supports dragging and resize", () => {
    const col = dom.workspaceMainColumn!;
    Object.defineProperty(col, "clientHeight", { configurable: true, value: 800 });
    const splitter = dom.mainTerminalSplitter!;
    vi.spyOn(dom.panelTerminal!, "getBoundingClientRect").mockReturnValue({ height: 200 } as DOMRect);
    initTerminalSplitter();
    expect(col.style.getPropertyValue("--terminal-height")).toBe("180px");

    window.dispatchEvent(new MouseEvent("mouseup"));
    splitter.dispatchEvent(new MouseEvent("mousedown", { clientY: 500, cancelable: true }));
    expect(splitter.classList.contains("dragging")).toBe(true);
    window.dispatchEvent(new MouseEvent("mousemove", { clientY: 450 }));
    expect(state.terminalHeightPx).toBe(250);
    window.dispatchEvent(new MouseEvent("mouseup"));
    expect(splitter.classList.contains("dragging")).toBe(false);
    window.dispatchEvent(new MouseEvent("mousemove", { clientY: 100 }));
    expect(state.terminalHeightPx).toBe(250);

    state.terminalHeightPx = 222;
    window.dispatchEvent(new Event("resize"));
    expect(col.style.getPropertyValue("--terminal-height")).toBe("222px");
  });

  it("initTerminalSplitter does nothing without elements", () => {
    removeIds("main-terminal-splitter");
    initTerminalSplitter();
    expect(dom.workspaceMainColumn!.style.getPropertyValue("--terminal-height")).toBe("");
  });

  it("appendLog appends, counts, trims and auto-scrolls", () => {
    appendLog("[Autoscaler] hello <x>", "12:00");
    const line = dom.logTerminal!.firstElementChild!;
    expect(line.innerHTML).toContain("[12:00]");
    expect(line.innerHTML).toContain("tag-cyan");
    expect(dom.terminalLineCount!.textContent).toBe("1 lines");
    appendLog("no timestamp");
    expect(dom.logTerminal!.lastElementChild!.querySelector(".log-ts")!.textContent).toMatch(/^\[.+\]$/);
    for (let i = 0; i < 510; i++) appendLog(`l${i}`, "t");
    expect(dom.logTerminal!.children).toHaveLength(500);

    dom.autoScrollToggle!.checked = true;
    Object.defineProperty(dom.logTerminal!, "scrollHeight", { configurable: true, value: 999 });
    appendLog("scroll", "t");
    expect(dom.logTerminal!.scrollTop).toBe(999);
    dom.autoScrollToggle!.checked = false;
    dom.logTerminal!.scrollTop = 0;
    appendLog("noscroll", "t");
    expect(dom.logTerminal!.scrollTop).toBe(0);
  });

  it("appendLog tolerates missing elements", () => {
    removeIds("terminal-line-count", "auto-scroll-toggle");
    appendLog("x", "t");
    expect(dom.logTerminal!.children).toHaveLength(1);
    removeIds("log-terminal");
    expect(() => appendLog("y")).not.toThrow();
  });
});
