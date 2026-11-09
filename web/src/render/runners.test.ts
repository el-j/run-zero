import { beforeEach, describe, expect, it, vi } from "vitest";
import { removeAllElements, runner } from "../../test/factories";
import { mountDashboard, pinClockAndLocale } from "../../test/helpers";
import { dom, initDom } from "../dom";
import { state } from "../state";
import { renderRunners } from "./runners";

const actions = vi.hoisted(() => ({ stopRunner: vi.fn(), openRunnerTerminal: vi.fn() }));
vi.mock("../actions", () => actions);

beforeEach(() => {
  mountDashboard();
});

const mixed = () => [
  runner({
    id: "a",
    name: "alpha",
    backend: "orbstack",
    target_arch: "arm64",
    created_at: "2026-01-01T00:00:00Z",
    progress_pct: 40,
    workflow_name: "wf",
    status: "busy",
    run_id: 1,
    job_id: 2,
    target_repo: "o/a",
    provider: "gitlab",
  }),
  runner({
    id: "b",
    name: "",
    backend: "",
    target_arch: "",
    status: "",
    provider: undefined,
    target_repo: "",
  }),
  runner({
    id: "c",
    name: "gamma",
    backend: "my-vm",
    is_cloud: true,
    origin: "cloud",
    job_url: "http://j",
    job_name: "jn",
  }),
  runner({
    id: "d",
    name: "delta",
    origin: "external",
    run_url: "http://r",
    run_id: 4,
    provider: "GitHub",
  }),
];

describe("renderRunners", () => {
  it("renders cards and table rows for a mixed fleet", () => {
    state.currentViewMode = "table";
    renderRunners(mixed());
    expect(dom.tabRunnersCount!.textContent).toBe("4");
    expect(dom.runnersCountBadge!.textContent).toBe("4 RUNNING");
    const group = dom.runnersOriginFilterGroup!;
    expect(group.querySelector('[data-origin="all"]')!.textContent).toBe("All (4)");
    expect(group.querySelector('[data-origin="local"]')!.textContent).toContain("(2)");
    expect(group.querySelector('[data-origin="cloud"]')!.textContent).toContain("(1)");
    expect(group.querySelector('[data-origin="external"]')!.textContent).toContain("(1)");

    const cards = dom.runnersGrid!.innerHTML;
    expect(cards).toContain("ORBSTACK");
    expect(cards).toContain("DOCKER");
    expect(cards).toContain("MY-VM");
    expect(cards).toContain("Standby Pool");
    expect(cards).toContain("GitLab");
    expect(cards).toContain("GitHub");
    expect(cards).toContain("Remote Managed");
    expect(cards).toContain("Workflow: wf");
    expect(cards).toContain("Run #1");
    expect(cards).toContain("jn");
    expect(cards).toContain("RUNNING");
    expect(cards).toContain("BUSY");
    expect(dom.runnersGrid!.classList.contains("hidden")).toBe(false);
    expect(dom.runnersEmptyState!.classList.contains("hidden")).toBe(true);

    const rows = dom.runnersTableBody!.querySelectorAll("tr");
    expect(rows).toHaveLength(4);
    expect(dom.runnersTableBody!.innerHTML).toContain("Standby / Idle");
    expect(dom.runnersTableBody!.innerHTML).toContain("Standby");
    expect(dom.runnersTableBody!.innerHTML).toContain("-</span>");
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(true);
  });

  it("shows the empty states with no runners", () => {
    renderRunners([]);
    expect(dom.runnersEmptyState!.classList.contains("hidden")).toBe(false);
    expect(dom.runnersEmptyState!.querySelector(".empty-title")!.textContent).toBe(
      "Fleet is on Standby",
    );
    expect(dom.runnersGrid!.classList.contains("hidden")).toBe(true);
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(false);
    state.currentViewMode = "table";
    renderRunners([]);
    expect(dom.runnersTableEmpty!.textContent).toBe("No active runners running.");
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(false);
  });

  it("filters by text, origin and provider", () => {
    dom.runnersSearchInput!.value = "  ALPHA ";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);
    expect(dom.runnersEmptyState!.querySelector(".empty-title")!.textContent).toBe(
      "No runners match this filter",
    );
    expect(dom.runnersEmptyState!.querySelector(".empty-desc")!.textContent).toContain('"alpha"');

    dom.runnersSearchInput!.value = "zzz";
    state.currentViewMode = "table";
    renderRunners(mixed());
    expect(dom.runnersGrid!.classList.contains("hidden")).toBe(true);
    expect(dom.runnersTableEmpty!.textContent).toBe('No runners matching "zzz".');
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(false);

    dom.runnersSearchInput!.value = "";
    state.currentRunnersOrigin = "cloud";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);
    state.currentRunnersOrigin = "external";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);

    state.currentRunnersOrigin = "all";
    state.currentRunnersProvider = "gitlab";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(1);
    state.currentRunnersProvider = "github";
    renderRunners(mixed());
    expect(dom.runnersGrid!.querySelectorAll(".runner-card")).toHaveLength(3);
  });

  it("sorts the table by every key in both directions", () => {
    state.currentViewMode = "table";
    const keys = ["name", "repo", "engine", "status", "workflow", "progress", "uptime"] as const;
    for (const key of keys) {
      for (const dir of ["asc", "desc"] as const) {
        state.runnersSort = { key, dir };
        renderRunners(mixed());
        expect(dom.runnersTableBody!.querySelectorAll("tr")).toHaveLength(4);
      }
    }
    state.runnersSort = { key: "name", dir: "asc" };
    renderRunners(mixed());
    const first = dom.runnersTableBody!.querySelector("tr td span:last-of-type")!;
    expect(first.textContent).toBe("alpha");
  });

  it("sorts pairs regardless of input order", () => {
    state.currentViewMode = "table";
    const dated = runner({ id: "d", created_at: "2026-01-01T00:00:00Z" });
    const undated = runner({ id: "u" });
    renderRunners([dated, undated]);
    renderRunners([undated, dated]);
    expect(dom.runnersTableBody!.querySelectorAll("tr")).toHaveLength(2);
  });

  it("binds stop and terminal buttons only for local runners", () => {
    renderRunners([
      runner({ id: "x", name: "x", job_id: 7 }),
      runner({ id: "y", origin: "cloud" }),
    ]);
    const stop = document.querySelectorAll<HTMLButtonElement>(".stop-runner-btn");
    const term = document.querySelectorAll<HTMLButtonElement>(".terminal-runner-btn");
    expect(stop).toHaveLength(2);
    expect(term).toHaveLength(2);
    stop[0].click();
    term[0].click();
    expect(actions.stopRunner).toHaveBeenCalledWith(stop[0]);
    expect(actions.openRunnerTerminal).toHaveBeenCalledWith(term[0]);
    expect(stop[0].dataset.jobId).toBe("7");
  });

  it("tolerates missing elements", () => {
    removeAllElements();
    expect(() => renderRunners(mixed())).not.toThrow();
    expect(() => renderRunners([])).not.toThrow();
    state.currentViewMode = "table";
    expect(() => renderRunners(mixed())).not.toThrow();
  });

  it("tolerates a bare filter group and bare empty state", () => {
    document.getElementById("runners-origin-filter-group")!.innerHTML = "";
    document.getElementById("runners-empty-state")!.innerHTML = "";
    initDom();
    expect(() => renderRunners(mixed())).not.toThrow();
    expect(() => renderRunners([])).not.toThrow();
  });
});

// Runners whose table order differs for every sort key and direction.
const trio = () => [
  runner({
    id: "b",
    name: "bravo",
    target_repo: "o/c",
    backend: "orbstack",
    target_arch: "arm64",
    status: "idle",
    workflow_name: "Lint",
    progress_pct: 10,
    created_at: "2026-01-05T11:00:00Z",
  }),
  runner({
    id: "c",
    name: "",
    target_repo: "",
    backend: "",
    target_arch: "",
    status: "",
    progress_pct: undefined,
  }),
  runner({
    id: "a",
    name: "alpha",
    target_repo: "o/b",
    backend: "multipass",
    target_arch: "amd64",
    status: "busy",
    workflow_name: "CI",
    progress_pct: 50,
    created_at: "2026-01-05T10:00:00Z",
  }),
];

const rowIds = () =>
  [...dom.runnersTableBody!.querySelectorAll("tr")].map(
    (tr) => tr.querySelector<HTMLElement>("td > div:last-child")!.textContent,
  );

describe("renderRunners output", () => {
  beforeEach(() => pinClockAndLocale("2026-01-05T12:00:00Z"));

  it("renders a mixed fleet as cards and table rows", () => {
    state.currentViewMode = "table";
    renderRunners([
      ...mixed(),
      runner({ id: "w", name: "wsl", backend: "wsl2", created_at: "2026-01-05T11:58:30Z" }),
    ]);
    expect(dom.runnersGrid!.innerHTML).toMatchSnapshot("cards");
    expect(dom.runnersTableBody!.innerHTML).toMatchSnapshot("table");
  });

  it.each([
    ["name", ["a", "b", "c"]],
    ["repo", ["a", "b", "c"]],
    ["engine", ["c", "a", "b"]],
    ["status", ["c", "a", "b"]],
    ["workflow", ["c", "a", "b"]],
    ["progress", ["c", "b", "a"]],
    ["uptime", ["c", "a", "b"]],
  ] as const)("sorts the table by %s", (key, asc) => {
    state.runnersSort = { key, dir: "asc" };
    renderRunners(trio());
    expect(rowIds()).toEqual(asc);
    state.runnersSort = { key, dir: "desc" };
    renderRunners([...trio()].reverse());
    expect(rowIds()).toEqual([...asc].reverse());
  });

  it("sorts by name falling back to the id, and repo falling back to Standby", () => {
    state.runnersSort = { key: "name", dir: "asc" };
    renderRunners([runner({ id: "zz", name: "m" }), runner({ id: "aa", name: "" })]);
    expect(rowIds()).toEqual(["aa", "zz"]);
    state.runnersSort = { key: "repo", dir: "asc" };
    renderRunners([
      runner({ id: "x", target_repo: "Zeta" }),
      runner({ id: "y", target_repo: "" }),
      runner({ id: "z", target_repo: "Alpha" }),
    ]);
    expect(rowIds()).toEqual(["z", "y", "x"]);
  });

  it("sorts engines by backend and arch", () => {
    state.runnersSort = { key: "engine", dir: "asc" };
    renderRunners([
      runner({ id: "x", backend: "docker", target_arch: "arm64" }),
      runner({ id: "y", backend: "docker", target_arch: "amd64" }),
    ]);
    expect(rowIds()).toEqual(["y", "x"]);
    // engine decides before arch
    renderRunners([
      runner({ id: "x", backend: "orbstack", target_arch: "amd64" }),
      runner({ id: "y", backend: "docker", target_arch: "arm64" }),
    ]);
    expect(rowIds()).toEqual(["y", "x"]);
  });

  it("only shows runners of the selected origin and provider, in cards and table", () => {
    const fleet = [
      runner({ id: "l", origin: "local" }),
      runner({ id: "c", is_cloud: true }),
      runner({ id: "e", origin: "external", provider: "GitLab" }),
    ];
    const shown = () =>
      [...dom.runnersGrid!.querySelectorAll(".runner-id")].map((s) => s.textContent);
    for (const [origin, provider, want] of [
      ["local", "all", ["runner-1"]],
      ["cloud", "all", ["runner-1"]],
      ["all", "gitlab", ["runner-1"]],
      ["all", "github", ["runner-1", "runner-1"]],
      ["external", "github", []],
    ] as const) {
      state.currentRunnersOrigin = origin;
      state.currentRunnersProvider = provider;
      renderRunners(fleet);
      expect(shown()).toEqual(want);
      expect(dom.runnersTableBody!.querySelectorAll("tr")).toHaveLength(want.length);
      expect(dom.runnersEmptyState!.querySelector(".empty-title")!.textContent).toBe(
        "No runners match this filter",
      );
    }
    state.currentRunnersOrigin = "cloud";
    state.currentRunnersProvider = "all";
    renderRunners(fleet);
    expect(dom.runnersTableBody!.querySelector("td > div:last-child")!.textContent).toBe("c");
  });

  it("counts runners per origin", () => {
    renderRunners([
      runner({ id: "1" }),
      runner({ id: "2", origin: "cloud" }),
      runner({ id: "3", is_cloud: true, origin: "external" }),
      runner({ id: "4", origin: "external" }),
    ]);
    const group = dom.runnersOriginFilterGroup!;
    expect(group.querySelector('[data-origin="local"]')!.textContent).toBe("🖥️ Local (1)");
    expect(group.querySelector('[data-origin="cloud"]')!.textContent).toBe("☁️ Cloud (2)");
    expect(group.querySelector('[data-origin="external"]')!.textContent).toBe("🌐 External (1)");
  });

  it("describes the empty fleet in the empty state", () => {
    renderRunners([]);
    expect(dom.runnersEmptyState!.querySelector(".empty-desc")!.textContent).toContain(
      "Zero active runner containers",
    );
    dom.runnersSearchInput!.value = "x";
    renderRunners([]);
    expect(dom.runnersEmptyState!.querySelector(".empty-desc")!.textContent).toBe(
      'Try a different filter. Current query: "x".',
    );
  });

  it("toggles the table hint with the filtered fleet", () => {
    dom.runnersSearchInput!.value = "nomatch";
    renderRunners([runner()]);
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(false);
    expect(dom.runnersTableEmpty!.textContent).toBe('No runners matching "nomatch".');
    dom.runnersSearchInput!.value = "";
    renderRunners([runner()]);
    expect(dom.runnersTableEmpty!.classList.contains("hidden")).toBe(true);
    expect(dom.runnersGrid!.classList.contains("hidden")).toBe(false);
  });
});
