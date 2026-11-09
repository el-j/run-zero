import { beforeEach, describe, expect, it } from "vitest";
import { jsonResponse, mountDashboard, pinClockAndLocale, stubFetch } from "../../test/helpers";
import { queued, removeAllElements } from "../../test/factories";
import { dom, initDom } from "../dom";
import { state } from "../state";
import { renderRepos } from "./repos";

const lastToast = () =>
  document.getElementById("toast-container")?.lastElementChild as HTMLElement | null;
const toast = () => lastToast()?.textContent ?? "";
const toastIsError = () => lastToast()?.style.borderColor === "var(--crimson)";

beforeEach(() => {
  mountDashboard();
});

/** Renders and mirrors the arguments into the shared state, as the app does. */
function render(
  repos: string[],
  prio: string[] = [],
  paused: string[] = [],
  jobs = [queued({ repo: "o/a" })],
) {
  state.currentRepos = repos;
  state.currentQueuedJobs = jobs;
  state.currentRepoPriority = prio;
  state.currentPausedRepos = new Set(paused);
  renderRepos(repos, jobs, prio, state.currentPausedRepos);
}

const rowOrder = () =>
  Array.from(dom.reposList!.querySelectorAll<HTMLElement>(".repo-row")).map((r) => r.dataset.repo);
const btn = (root: Element, action: string, repo: string) =>
  root.querySelector<HTMLButtonElement>(`button[data-action="${action}"][data-repo="${repo}"]`)!;
const flush = () => new Promise((r) => setTimeout(r, 0));

describe("renderRepos rendering", () => {
  it("renders list and table with badges", () => {
    render(
      ["o/a", "o/b", "o/c"],
      [],
      ["o/b"],
      [queued({ repo: "o/a" }), queued({ repo: "o/a" }), queued({ repo: "" })],
    );
    expect(dom.tabReposCount!.textContent).toBe("3");
    expect(dom.reposCountBadge!.textContent).toBe("3 REPOSITORIES");
    expect(dom.reposList!.innerHTML).toContain("2 queued");
    expect(dom.reposList!.innerHTML).toContain("PAUSED");
    expect(dom.reposList!.innerHTML).toContain("idle");
    expect(dom.reposTableBody!.querySelectorAll("tr")).toHaveLength(3);
    expect(dom.reposTableBody!.innerHTML).toContain("RESUME");
  });

  it("uses the priority order and filters by search", () => {
    dom.repoSearchInput!.value = "  B ";
    render(["o/a", "o/b"], ["o/b", "o/a"]);
    expect(rowOrder()).toEqual(["o/b"]);
    dom.repoSearchInput!.value = "";
    render(["o/a", "o/b"], ["o/b", "o/a"]);
    expect(rowOrder()).toEqual(["o/b", "o/a"]);
  });

  it.each([
    ["rank", "asc"],
    ["rank", "desc"],
    ["repo", "asc"],
    ["status", "asc"],
    ["queued", "desc"],
  ] as const)("sorts the table by %s %s", (key, dir) => {
    state.reposSort = { key, dir };
    render(["o/a", "o/b"], [], ["o/a"]);
    expect(dom.reposTableBody!.querySelectorAll("tr")).toHaveLength(2);
  });

  it("shows empty and no-match states", () => {
    render([]);
    expect(dom.reposList!.innerHTML).toContain("Discovering");
    expect(dom.reposTableBody!.innerHTML).toContain("Discovering");
    dom.repoSearchInput!.value = "zzz";
    render(["o/a"]);
    expect(dom.reposList!.innerHTML).toContain('No repositories matching "zzz"');
    expect(dom.reposTableBody!.innerHTML).toContain("No repositories matching");
  });

  it("works without optional elements", () => {
    removeAllElements();
    expect(() => renderRepos(["a"], [], [], new Set())).not.toThrow();
    const list = document.createElement("div");
    list.id = "repos-list";
    document.body.appendChild(list);
    initDom();
    renderRepos([], [], [], new Set());
    expect(list.innerHTML).toContain("Discovering");
    renderRepos(["x"], [], [], new Set());
    expect(list.querySelectorAll(".repo-row")).toHaveLength(1);
    const search = document.createElement("input");
    search.id = "repo-search-input";
    search.value = "nomatch";
    document.body.appendChild(search);
    initDom();
    renderRepos(["x"], [], [], new Set());
    expect(list.innerHTML).toContain("No repositories matching");
  });
});

describe("renderRepos priority buttons", () => {
  it("toggles pause and saves", async () => {
    const f = stubFetch(() => jsonResponse({ success: true }));
    render(["o/a", "o/b"]);
    btn(dom.reposList!, "toggle-pause", "o/a").click();
    expect(state.currentPausedRepos.has("o/a")).toBe(true);
    await flush();
    expect(JSON.parse(f.mock.calls[0][1]!.body as string)).toEqual({
      priority: ["o/a", "o/b"],
      paused: ["o/a"],
    });
    expect(toast()).toBe("Priority updated");
    expect(toastIsError()).toBe(false);
    btn(dom.reposList!, "toggle-pause", "o/a").click();
    expect(state.currentPausedRepos.has("o/a")).toBe(false);
    await flush();
  });

  it("moves repositories up and down, ignoring edges", async () => {
    stubFetch(() => jsonResponse({ success: true }));
    render(["o/a", "o/b", "o/c"]);
    btn(dom.reposList!, "move-down", "o/a").click();
    expect(state.currentRepoPriority).toEqual(["o/b", "o/a", "o/c"]);
    btn(dom.reposList!, "move-up", "o/c").click();
    expect(state.currentRepoPriority).toEqual(["o/b", "o/c", "o/a"]);
    // Force the guarded edges by clicking disabled buttons programmatically
    btn(dom.reposTableBody!, "move-up", "o/b").onclick!(new PointerEvent("click"));
    expect(state.currentRepoPriority).toEqual(["o/b", "o/c", "o/a"]);
    btn(dom.reposTableBody!, "move-down", "o/a").onclick!(new PointerEvent("click"));
    expect(state.currentRepoPriority).toEqual(["o/b", "o/c", "o/a"]);
    await flush();
  });

  it("reports save failures", async () => {
    stubFetch(() => jsonResponse({ error: "no" }, { ok: false }));
    render(["o/a"]);
    btn(dom.reposList!, "toggle-pause", "o/a").click();
    await flush();
    expect(toast()).toContain("Failed updating priority: no");
    expect(toastIsError()).toBe(true);
  });

  it("keeps priority clicks from reaching the row", () => {
    stubFetch(() => jsonResponse({ success: true }));
    render(["o/a", "o/b"]);
    let bubbled = false;
    dom.reposList!.addEventListener("click", () => (bubbled = true));
    btn(dom.reposList!, "move-down", "o/a").click();
    expect(bubbled).toBe(false);
  });

  it("ignores buttons with unknown actions", () => {
    render(["o/a"]);
    const other = document.createElement("button");
    other.dataset.action = "other";
    document.body.appendChild(other);
    renderRepos(["o/a"], [], [], new Set());
    expect(other.onclick).toBeNull();
  });
});

describe("renderRepos drag and drop", () => {
  const rows = () => Array.from(dom.reposList!.querySelectorAll<HTMLElement>(".repo-row"));
  const fire = (el: Element, type: string) =>
    el.dispatchEvent(new Event(type, { cancelable: true }));

  it("tracks drag state", () => {
    render(["o/a", "o/b"]);
    const [a, b] = rows();
    fire(a, "dragstart");
    expect(state.draggedRepo).toBe("o/a");
    expect(a.classList.contains("repo-row-dragging")).toBe(true);
    fire(b, "dragover");
    expect(b.classList.contains("repo-row-drag-over")).toBe(true);
    fire(b, "dragleave");
    expect(b.classList.contains("repo-row-drag-over")).toBe(false);
    fire(b, "dragover");
    fire(a, "dragend");
    expect(state.draggedRepo).toBeNull();
    expect(b.classList.contains("repo-row-drag-over")).toBe(false);
  });

  it("accepts drops by preventing the browser default", () => {
    stubFetch(() => jsonResponse({ success: true }));
    render(["o/a", "o/b"]);
    const over = new Event("dragover", { cancelable: true });
    rows()[1].dispatchEvent(over);
    expect(over.defaultPrevented).toBe(true);
    const drop = new Event("drop", { cancelable: true });
    rows()[1].dispatchEvent(drop);
    expect(drop.defaultPrevented).toBe(true);
  });

  it("drops onto the first row", () => {
    stubFetch(() => jsonResponse({ success: true }));
    render(["o/a", "o/b", "o/c"]);
    fire(rows()[2], "dragstart");
    fire(rows()[0], "drop");
    expect(state.currentRepoPriority).toEqual(["o/c", "o/a", "o/b"]);
  });

  it("ignores drops on a row without a repo", () => {
    const f = stubFetch(() => jsonResponse({}));
    render(["o/a", "o/b"]);
    fire(rows()[0], "dragstart");
    delete rows()[1].dataset.repo;
    fire(rows()[1], "drop");
    expect(f).not.toHaveBeenCalled();
  });

  it("falls back to null when the row has no repo", () => {
    render(["o/a"]);
    const [a] = rows();
    delete a.dataset.repo;
    fire(a, "dragstart");
    expect(state.draggedRepo).toBeNull();
  });

  it("reorders on drop and saves", async () => {
    const f = stubFetch(() => jsonResponse({ success: true }));
    render(["o/a", "o/b", "o/c"]);
    fire(rows()[0], "dragstart");
    fire(rows()[2], "drop");
    expect(state.currentRepoPriority).toEqual(["o/b", "o/c", "o/a"]);
    await flush();
    expect(f).toHaveBeenCalled();
    expect(toast()).toBe("Priority reordered");
    expect(toastIsError()).toBe(false);
    expect(rowOrder()).toEqual(["o/b", "o/c", "o/a"]);
  });

  it("reports drop save failures", async () => {
    stubFetch(() => jsonResponse({ error: "bad" }, { ok: false }));
    render(["o/a", "o/b"]);
    fire(rows()[0], "dragstart");
    fire(rows()[1], "drop");
    await flush();
    expect(toast()).toContain("Error saving priority: bad");
    expect(toastIsError()).toBe(true);
  });

  it("ignores drops without a source, on itself, or on unknown repos", () => {
    const f = stubFetch(() => jsonResponse({}));
    render(["o/a", "o/b"]);
    fire(rows()[0], "drop");
    state.draggedRepo = "o/a";
    fire(rows()[0], "drop");
    state.draggedRepo = "unknown";
    fire(rows()[1], "drop");
    expect(f).not.toHaveBeenCalled();
  });
});

describe("renderRepos output", () => {
  beforeEach(() => pinClockAndLocale());
  const tableOrder = () =>
    [...dom.reposTableBody!.querySelectorAll<HTMLElement>(".repo-name")].map((r) => r.textContent);

  it("renders the priority list and table", () => {
    render(
      ["o/a", "o/b", "o/c"],
      ["o/c", "o/a", "o/b"],
      ["o/b"],
      [queued({ repo: "o/a" }), queued({ repo: "o/a" }), queued({ repo: "o/c" })],
    );
    expect(dom.reposList!.innerHTML).toMatchSnapshot("list");
    expect(dom.reposTableBody!.innerHTML).toMatchSnapshot("table");
  });

  it("renders the empty and no-match states", () => {
    render([]);
    expect(dom.reposList!.innerHTML).toMatchSnapshot("discovering list");
    expect(dom.reposTableBody!.innerHTML).toMatchSnapshot("discovering table");
    dom.repoSearchInput!.value = "<x>";
    render(["o/a"]);
    expect(dom.reposList!.innerHTML).toMatchSnapshot("no match list");
    expect(dom.reposTableBody!.innerHTML).toMatchSnapshot("no match table");
  });

  // Ties (both ACTIVE) keep the priority order in either direction.
  it.each([
    ["rank", ["o/c", "o/a", "o/b"], ["o/b", "o/a", "o/c"]],
    ["repo", ["o/a", "o/b", "o/c"], ["o/c", "o/b", "o/a"]],
    ["status", ["o/c", "o/a", "o/b"], ["o/b", "o/c", "o/a"]],
    ["queued", ["o/b", "o/c", "o/a"], ["o/a", "o/c", "o/b"]],
  ] as const)("sorts the table by %s", (key, asc, desc) => {
    const jobs = [queued({ repo: "o/a" }), queued({ repo: "o/a" }), queued({ repo: "o/c" })];
    state.reposSort = { key, dir: "asc" };
    render(["o/a", "o/b", "o/c"], ["o/c", "o/a", "o/b"], ["o/b"], jobs);
    expect(tableOrder()).toEqual(asc);
    state.reposSort = { key, dir: "desc" };
    render(["o/a", "o/b", "o/c"], ["o/c", "o/a", "o/b"], ["o/b"], jobs);
    expect(tableOrder()).toEqual(desc);
  });
});
