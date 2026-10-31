import { beforeEach, describe, expect, it, vi } from "vitest";
import { viewport } from "../../test/setup";
import { mountDashboard } from "../../test/helpers";
import { runner } from "../../test/factories";
import { dom, initDom } from "../dom";
import { filterStorageKeys, state } from "../state";

const rr = vi.hoisted(() => ({
  renderRunners: vi.fn(),
  renderQueue: vi.fn(),
  renderCompletedJobs: vi.fn(),
  renderRepos: vi.fn(),
}));
vi.mock("../render/runners", () => ({ renderRunners: rr.renderRunners }));
vi.mock("../render/queue", () => ({ renderQueue: rr.renderQueue }));
vi.mock("../render/jobs", () => ({ renderCompletedJobs: rr.renderCompletedJobs }));
vi.mock("../render/repos", () => ({ renderRepos: rr.renderRepos }));

const acts = vi.hoisted(() => ({
  launchRunner: vi.fn(),
  pruneFleet: vi.fn(),
  purgeAllCaches: vi.fn(),
  purgeCacheCategory: vi.fn(),
}));
vi.mock("../actions", () => acts);

const settingsFns = vi.hoisted(() => ({ openSettingsModal: vi.fn(), saveSettings: vi.fn() }));
vi.mock("../settings", () => settingsFns);

import {
  initClearLogs,
  initFilterControls,
  initTableSortingControls,
  initTerminalControls,
  initViewControls,
} from "./controls";
import { initHandlers, startUptimeTicker } from "./index";
import { initHeaderMenu } from "./headerMenu";
import { initMaintenanceControls, initSettingsModal, initSpawnModal } from "./modals";
import { initTelemetryDrawer } from "./telemetry";

beforeEach(() => {
  mountDashboard();
});

/** Removes every element matched by the ids and refreshes the DOM refs. */
function drop(...ids: string[]) {
  for (const id of ids) document.getElementById(id)?.remove();
  initDom();
}

describe("initTableSortingControls", () => {
  it("toggles the matching sort state and re-renders", () => {
    initTableSortingControls();
    const th = (table: string, key: string) => {
      const el = document.createElement("th");
      el.className = "sortable-col";
      if (table) el.dataset.table = table;
      if (key) el.dataset.sortKey = key;
      return el;
    };
    const ths = [
      th("runners", "name"),
      th("queue", "repo"),
      th("jobs", "name"),
      th("repos", "name"),
      th("", "name"),
      th("runners", ""),
      th("other", "x"),
    ];
    // Re-run so the dynamically added headers are bound too.
    ths.forEach((t) => document.body.appendChild(t));
    initTableSortingControls();
    ths.forEach((t) => t.click());
    expect(state.runnersSort.key).toBe("name");
    expect(state.queueSort.key).toBe("repo");
    expect(state.jobsSort.key).toBe("name");
    expect(state.reposSort.key).toBe("name");
    expect(rr.renderRunners).toHaveBeenCalled();
    expect(rr.renderRepos).toHaveBeenCalled();
  });
});

describe("initViewControls", () => {
  it("wires tabs and view modes", () => {
    initViewControls();
    dom.tabBtnQueue!.click();
    expect(state.currentTab).toBe("queue");
    for (const b of [dom.tabBtnRunners, dom.tabBtnQueue, dom.tabBtnJobs, dom.tabBtnRepos]) b!.click();
    dom.viewModeTable!.click();
    expect(state.currentViewMode).toBe("table");
    dom.viewModeCards!.click();
    expect(state.currentViewMode).toBe("cards");
    dom.selectViewModeSetting!.value = "table";
    dom.selectViewModeSetting!.dispatchEvent(new Event("change"));
    expect(state.currentViewMode).toBe("table");
  });

  it("tolerates missing elements", () => {
    document.body.innerHTML = "";
    initDom();
    expect(() => initViewControls()).not.toThrow();
  });
});

describe("initTerminalControls / initClearLogs", () => {
  it("toggles the terminal and clears logs", () => {
    initTerminalControls();
    dom.btnToggleTerminalExpand!.click();
    expect(state.terminalExpanded).toBe(true);
    dom.logTerminal!.innerHTML = "<div>x</div>";
    initClearLogs();
    dom.btnClearLogs!.click();
    expect(dom.logTerminal!.innerHTML).toBe("");
  });

  it("tolerates missing elements", () => {
    drop("log-terminal");
    initClearLogs();
    dom.btnClearLogs!.click();
    document.body.innerHTML = "";
    initDom();
    initTerminalControls();
    initClearLogs();
  });
});

describe("initFilterControls", () => {
  it("persists search text and re-renders", () => {
    state.currentRunners = [runner()];
    initFilterControls();
    const type = (el: HTMLInputElement | null, v: string) => {
      el!.value = v;
      el!.dispatchEvent(new Event("input"));
    };
    type(dom.runnersSearchInput, "a");
    type(dom.queueSearchInput, "b");
    type(dom.jobsSearchInput, "c");
    type(dom.repoSearchInput, "d");
    expect(localStorage.getItem(filterStorageKeys.runners)).toBe("a");
    expect(localStorage.getItem(filterStorageKeys.queue)).toBe("b");
    expect(localStorage.getItem(filterStorageKeys.jobs)).toBe("c");
    expect(localStorage.getItem(filterStorageKeys.repos)).toBe("d");
  });

  it("handles origin filter clicks and provider changes", () => {
    initFilterControls();
    const group = dom.runnersOriginFilterGroup!;
    group.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    const buttons = group.querySelectorAll<HTMLButtonElement>("button[data-origin]");
    buttons[1].click();
    expect(state.currentRunnersOrigin).toBe(buttons[1].dataset.origin);
    expect(buttons[1].classList.contains("active")).toBe(true);
    const noOrigin = document.createElement("button");
    noOrigin.setAttribute("data-origin", "");
    group.appendChild(noOrigin);
    noOrigin.click();
    expect(state.currentRunnersOrigin).toBe("all");
    dom.runnersProviderSelect!.add(new Option("gh", "gh"));
    dom.runnersProviderSelect!.value = "gh";
    dom.runnersProviderSelect!.dispatchEvent(new Event("change"));
    expect(state.currentRunnersProvider).toBe("gh");
  });

  it("tolerates missing elements", () => {
    document.body.innerHTML = "";
    initDom();
    expect(() => initFilterControls()).not.toThrow();
  });
});

describe("initMaintenanceControls", () => {
  it("wires the buttons", () => {
    const cat = document.createElement("button");
    cat.dataset.purgeCategory = "apt";
    document.body.appendChild(cat);
    initMaintenanceControls();
    dom.btnPruneRunners!.click();
    dom.btnPurgeAllCaches!.click();
    cat.click();
    expect(acts.pruneFleet).toHaveBeenCalled();
    expect(acts.purgeAllCaches).toHaveBeenCalled();
    expect(acts.purgeCacheCategory).toHaveBeenCalledWith(cat);
  });

  it("tolerates missing elements", () => {
    document.body.innerHTML = "";
    initDom();
    initMaintenanceControls();
  });
});

describe("initSpawnModal", () => {
  it("opens prefilled, closes and submits", () => {
    state.currentRepos = ["o/top"];
    initSpawnModal();
    dom.btnStartRunner!.click();
    expect(dom.manualRepoInput!.value).toBe("o/top");
    expect(dom.spawnModal!.open).toBe(true);
    dom.spawnModalClose!.click();
    expect(dom.spawnModal!.open).toBe(false);
    dom.spawnModal!.open = true;
    dom.spawnModalCancel!.click();
    expect(dom.spawnModal!.open).toBe(false);
    dom.spawnModalSubmit!.click();
    expect(acts.launchRunner).toHaveBeenCalledWith(dom.spawnModal);
  });

  it("does not prefill without repositories or input", () => {
    state.currentRepos = [];
    dom.manualRepoInput!.value = "keep";
    initSpawnModal();
    dom.btnStartRunner!.click();
    expect(dom.manualRepoInput!.value).toBe("keep");
    state.currentRepos = ["x"];
    drop("manual-repo-input");
    initSpawnModal();
    dom.btnStartRunner!.click();
  });

  it("tolerates missing dialog", () => {
    document.body.innerHTML = "";
    initDom();
    initSpawnModal();
  });
});

describe("initSettingsModal", () => {
  it("wires every control", () => {
    initSettingsModal();
    dom.btnOpenSettings!.click();
    dom.btnOpenSettingsPanel!.click();
    expect(settingsFns.openSettingsModal).toHaveBeenCalledTimes(2);
    dom.settingsModal!.open = true;
    dom.settingsModalClose!.click();
    expect(dom.settingsModal!.open).toBe(false);
    dom.settingsModal!.open = true;
    dom.settingsModalCancel!.click();
    expect(dom.settingsModal!.open).toBe(false);
    dom.settingsModalSave!.click();
    dom.settingsForm!.dispatchEvent(new Event("submit", { cancelable: true }));
    expect(settingsFns.saveSettings).toHaveBeenCalledTimes(2);
  });

  it("tolerates missing elements", () => {
    document.body.innerHTML = "";
    initDom();
    initSettingsModal();
  });
});

describe("initTelemetryDrawer", () => {
  it("opens, toggles and closes the drawer", () => {
    const closeDrawer = initTelemetryDrawer();
    const drawer = document.getElementById("telemetry-drawer")!;
    const open = document.getElementById("btn-open-drawer")!;
    viewport.width = 500;
    open.click();
    expect(drawer.classList.contains("open")).toBe(true);
    expect(document.getElementById("drawer-backdrop")!.classList.contains("open")).toBe(true);
    open.click();
    expect(drawer.classList.contains("open")).toBe(false);
    open.click();
    document.getElementById("btn-close-drawer")!.click();
    expect(drawer.classList.contains("open")).toBe(false);
    open.click();
    document.getElementById("drawer-backdrop")!.click();
    expect(drawer.classList.contains("open")).toBe(false);
    open.click();
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "x" }));
    expect(drawer.classList.contains("open")).toBe(true);
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    expect(drawer.classList.contains("open")).toBe(false);
    closeDrawer();
  });

  it("collapses the header menu when opening and handles resize", () => {
    initTelemetryDrawer();
    document.querySelector(".app-header")!.classList.add("menu-open");
    document.getElementById("btn-open-drawer")!.click();
    expect(document.querySelector(".app-header")!.classList.contains("menu-open")).toBe(false);
    const backdrop = document.getElementById("drawer-backdrop")!;
    backdrop.classList.add("open");
    viewport.width = 500;
    window.dispatchEvent(new Event("resize"));
    expect(backdrop.classList.contains("open")).toBe(true);
    viewport.width = 1200;
    window.dispatchEvent(new Event("resize"));
    expect(backdrop.classList.contains("open")).toBe(false);
  });

  it("routes KPI cards to tabs or drawer panels", () => {
    vi.useFakeTimers();
    const mk = (target: string) => {
      const el = document.createElement("div");
      el.dataset.kpiTarget = target;
      document.body.appendChild(el);
      return el;
    };
    const cards = [mk("runners"), mk("queue"), mk("routing"), mk("unknown")];
    const spy = vi.spyOn(Element.prototype, "scrollIntoView");
    initTelemetryDrawer();
    cards.forEach((c) => c.click());
    vi.advanceTimersByTime(200);
    expect(spy).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });

  it("opens without a header panel", () => {
    initTelemetryDrawer();
    const open = document.getElementById("btn-open-drawer")!;
    document.querySelector(".header-right")!.remove();
    open.click();
    expect(document.getElementById("telemetry-drawer")!.classList.contains("open")).toBe(true);
  });

  it("works with a bare document", () => {
    document.body.innerHTML = "";
    initDom();
    const close = initTelemetryDrawer();
    close();
    window.dispatchEvent(new Event("resize"));
  });
});

describe("initHeaderMenu", () => {
  const header = () => document.querySelector<HTMLElement>(".app-header")!;
  const panel = () => header().querySelector<HTMLElement>(".header-right")!;

  it("toggles the menu on mobile", () => {
    const closeDrawer = vi.fn();
    viewport.width = 500;
    initHeaderMenu(closeDrawer);
    dom.btnHeaderMenu!.click();
    expect(header().classList.contains("menu-open")).toBe(true);
    expect(panel().style.display).toBe("flex");
    expect(dom.btnHeaderMenu!.getAttribute("aria-expanded")).toBe("true");
    expect(closeDrawer).toHaveBeenCalled();
    dom.btnHeaderMenu!.click();
    expect(panel().style.display).toBe("none");
  });

  it("clears the inline display on desktop", () => {
    initHeaderMenu(vi.fn());
    panel().style.display = "none";
    dom.btnHeaderMenu!.click();
    expect(panel().style.display).toBe("");
  });

  it("closes through the backdrop, outside clicks, resize and Escape", () => {
    viewport.width = 500;
    initHeaderMenu(vi.fn());
    const open = () => {
      if (!header().classList.contains("menu-open")) dom.btnHeaderMenu!.click();
    };
    open();
    dom.headerMenuBackdrop!.click();
    expect(header().classList.contains("menu-open")).toBe(false);

    open();
    header().click();
    expect(header().classList.contains("menu-open")).toBe(true);
    document.body.click();
    expect(header().classList.contains("menu-open")).toBe(false);

    open();
    viewport.width = 1200;
    window.dispatchEvent(new Event("resize"));
    expect(header().classList.contains("menu-open")).toBe(false);
    viewport.width = 500;
    window.dispatchEvent(new Event("resize"));

    open();
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "a" }));
    expect(header().classList.contains("menu-open")).toBe(true);
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    expect(header().classList.contains("menu-open")).toBe(false);
  });

  it("ignores outside clicks on desktop or without a target", () => {
    initHeaderMenu(vi.fn());
    header().classList.add("menu-open");
    document.body.click();
    expect(header().classList.contains("menu-open")).toBe(true);
    viewport.width = 500;
    const addSpy = vi.spyOn(document, "addEventListener");
    initHeaderMenu(vi.fn());
    const clickListener = addSpy.mock.calls.find((c) => c[0] === "click")![1] as (e: Event) => void;
    clickListener({ target: null } as unknown as Event);
    expect(header().classList.contains("menu-open")).toBe(true);
    header().remove();
    clickListener({ target: document.body } as unknown as Event);
  });

  it("copes with a missing header and backdrop", () => {
    viewport.width = 500;
    drop("header-menu-backdrop");
    initHeaderMenu(vi.fn());
    header().remove();
    dom.btnHeaderMenu!.click();
    document.body.click();
  });

  it("does nothing without the menu button", () => {
    document.body.innerHTML = "";
    initDom();
    expect(() => initHeaderMenu(vi.fn())).not.toThrow();
  });
});

describe("handlers index", () => {
  it("ticks the uptime counter", () => {
    vi.useFakeTimers();
    state.lastUptimeSeconds = 3599;
    startUptimeTicker();
    vi.advanceTimersByTime(1000);
    expect(dom.statUptime!.textContent).toBe("01:00:00");
    document.body.innerHTML = "";
    initDom();
    vi.advanceTimersByTime(1000);
    vi.useRealTimers();
  });

  it("initHandlers binds everything", () => {
    vi.useFakeTimers();
    initHandlers();
    dom.btnPruneRunners!.click();
    expect(acts.pruneFleet).toHaveBeenCalled();
    vi.useRealTimers();
  });
});
