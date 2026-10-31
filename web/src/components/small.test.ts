import { describe, expect, it, vi } from "vitest";
import { jsonResponse, stubFetch } from "../../test/helpers";
import type { FleetState } from "../api/client";
import { CachePanelComponent } from "./CachePanel";
import { CapacityMeterComponent } from "./CapacityMeter";
import { HeaderComponent } from "./Header";
import { PriorityManagerComponent } from "./PriorityManager";

const el = () => document.body.appendChild(document.createElement("div"));
const flush = () => new Promise((r) => setTimeout(r, 0));

describe("HeaderComponent", () => {
  it("renders quota and billing when available", () => {
    const c = el();
    new HeaderComponent(c).render({
      rate_limit_limit: 100,
      rate_limit_remaining: 40,
      actions_billing: { total_minutes_used: 12 },
    } as FleetState);
    expect(c.textContent).toContain("40/100");
    expect(c.textContent).toContain("12m");
    expect(c.innerHTML).toContain("var(--accent-emerald)");
  });

  it("renders placeholders when disconnected and empty", () => {
    const c = el();
    new HeaderComponent(c).render(undefined, false);
    expect(c.textContent).toContain("—");
    expect(c.innerHTML).toContain("var(--accent-amber)");
    new HeaderComponent(c).render({ rate_limit_limit: 5 } as FleetState);
    expect(c.textContent).toContain("—");
  });
});

describe("CapacityMeterComponent", () => {
  it("renders busy and free slots", () => {
    const c = el();
    new CapacityMeterComponent(c).render({ busy_runners: 1, max_runners: 4, free_slots: 1 } as FleetState);
    expect(c.textContent).toContain("1 Free Slot");
    expect(c.textContent).not.toContain("1 Free Slots");
    expect(c.innerHTML).toContain("width: 25%");
  });

  it("flags a saturated fleet", () => {
    const c = el();
    new CapacityMeterComponent(c).render({ busy_runners: 4, max_runners: 4 } as FleetState);
    expect(c.textContent).toContain("0 Free Slots");
    expect(c.innerHTML).toContain("var(--accent-redshift)");
  });

  it("uses defaults without state", () => {
    const c = el();
    new CapacityMeterComponent(c).render();
    expect(c.textContent).toContain("3 Free Slots");
  });
});

describe("CachePanelComponent", () => {
  const stats = {
    total_human: "1 GB",
    total_bytes: 1,
    categories: [{ category: "pnpm", bytes: 1, human_readable: "1 GB" }],
  };

  it("renders defaults before loading", () => {
    const c = el();
    new CachePanelComponent(c).render();
    expect(c.textContent).toContain("hostedtoolcache");
    expect(c.textContent).toContain("0 MB");
  });

  it("loads stats and shows the loading state in between", async () => {
    const c = el();
    stubFetch(() => jsonResponse(stats));
    const p = new CachePanelComponent(c);
    const pending = p.load();
    expect(c.textContent).toContain("Loading cache usage statistics");
    await pending;
    expect(c.textContent).toContain("1 GB");
  });

  it("shows load errors", async () => {
    const c = el();
    stubFetch(() => jsonResponse({}, { ok: false }));
    await new CachePanelComponent(c).load();
    expect(c.textContent).toContain("Failed to load cache stats");
  });

  it("purges a category after confirmation and reloads", async () => {
    const c = el();
    const f = stubFetch((url) => jsonResponse(url.includes("purge") ? { success: true } : stats));
    const p = new CachePanelComponent(c);
    await p.load();
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValueOnce(false);
    c.querySelector<HTMLButtonElement>("[data-purge-category]")!.click();
    expect(confirmSpy).toHaveBeenCalledWith("Are you sure you want to purge the category 'pnpm'?");
    await flush();
    expect(f.mock.calls.some((x) => x[0].includes("purge"))).toBe(false);
    confirmSpy.mockReturnValue(true);
    c.querySelector<HTMLButtonElement>("[data-purge-category]")!.click();
    await flush();
    expect(c.textContent).toContain("✓ Purged category 'pnpm'");
    expect(c.innerHTML).toContain("var(--accent-emerald)");
  });

  it("purges everything and reports failures", async () => {
    const c = el();
    stubFetch((url) => jsonResponse(url.includes("purge") ? { error: "nope" } : stats, { ok: !url.includes("purge") }));
    const p = new CachePanelComponent(c);
    await p.load();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    c.querySelector<HTMLButtonElement>("#purge-all-btn")!.click();
    await flush();
    expect(c.textContent).toContain("✗ Error purging: nope");
  });

  it("ignores purge buttons without a category", async () => {
    const c = el();
    const p = new CachePanelComponent(c);
    p.render();
    const b = c.querySelector<HTMLButtonElement>("[data-purge-category]")!;
    b.dataset.purgeCategory = "";
    const confirmSpy = vi.spyOn(window, "confirm");
    b.click();
    expect(confirmSpy).not.toHaveBeenCalled();
  });
});

describe("PriorityManagerComponent", () => {
  const setup = (onUpdate?: () => void) => {
    const c = el();
    const m = new PriorityManagerComponent(c, onUpdate);
    return { c, m };
  };

  it("renders nothing for an empty list", () => {
    const { c, m } = setup();
    c.innerHTML = "x";
    m.setState([], []);
    expect(c.innerHTML).toBe("");
  });

  it("renders repositories with paused markers", () => {
    const { c, m } = setup();
    m.setState(["a", "b"], ["b"]);
    expect(c.textContent).toContain("PAUSED");
    expect(c.textContent).toContain("Resume");
    expect(c.textContent).toContain("Pause");
    expect(c.querySelectorAll("button[disabled]")).toHaveLength(2);
  });

  it("moves, pauses and notifies", async () => {
    const onUpdate = vi.fn();
    const f = stubFetch(() => jsonResponse({ success: true }));
    const { c, m } = setup(onUpdate);
    m.setState(["a", "b"], []);
    c.querySelector<HTMLButtonElement>('[data-move="0"][data-dir="1"]')!.click();
    await flush();
    expect(JSON.parse(f.mock.calls[0][1]!.body as string).priority).toEqual(["b", "a"]);
    c.querySelector<HTMLButtonElement>("[data-toggle-pause]")!.click();
    await flush();
    expect(JSON.parse(f.mock.calls[1][1]!.body as string).paused).toEqual(["b"]);
    c.querySelector<HTMLButtonElement>("[data-toggle-pause]")!.click();
    await flush();
    expect(JSON.parse(f.mock.calls[2][1]!.body as string).paused).toEqual([]);
    expect(onUpdate).toHaveBeenCalledTimes(3);
  });

  it("works without a callback and ignores edge moves", async () => {
    const f = stubFetch(() => jsonResponse({ success: true }));
    const { c, m } = setup();
    m.setState(["a", "b"], []);
    c.querySelector<HTMLButtonElement>('[data-move="0"][data-dir="-1"]')!.click();
    await flush();
    expect(f).not.toHaveBeenCalled();
    c.querySelector<HTMLButtonElement>('[data-move="1"][data-dir="-1"]')!.click();
    await flush();
    expect(f).toHaveBeenCalledTimes(1);
    const down = c.querySelector<HTMLButtonElement>('[data-move="1"][data-dir="1"]')!;
    down.disabled = false;
    down.click();
    await flush();
    expect(f).toHaveBeenCalledTimes(1);
  });

  it("logs save failures", async () => {
    const err = vi.spyOn(console, "error").mockImplementation(() => {});
    stubFetch(() => jsonResponse({}, { ok: false }));
    const { c, m } = setup();
    m.setState(["a"], []);
    c.querySelector<HTMLButtonElement>("[data-toggle-pause]")!.click();
    await flush();
    expect(err).toHaveBeenCalled();
  });

  it("tolerates buttons with missing data attributes", async () => {
    stubFetch(() => jsonResponse({ success: true }));
    const { c, m } = setup();
    m.setState(["a", "b"], []);
    const mv = c.querySelector<HTMLButtonElement>('[data-move="1"]')!;
    delete mv.dataset.move;
    delete mv.dataset.dir;
    mv.click();
    const tp = c.querySelector<HTMLButtonElement>("[data-toggle-pause]")!;
    tp.dataset.togglePause = "";
    tp.click();
    await flush();
  });
});
