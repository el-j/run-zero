import { describe, expect, it, vi } from "vitest";
import { jsonResponse, stubFetch } from "../../test/helpers";
import { SettingsPanelComponent } from "./SettingsPanel";

const full = {
  max_runners: 5,
  min_runners: 1,
  runner_cpus: 2,
  runner_memory: "8G",
  runner_backend: "docker",
  auto_route_vm: true,
  runner_arch: "arm64",
  native_arch_override: "all",
  poll_interval: 7,
  discovery_interval: 60,
  cache_enabled: true,
  proxies_enabled: false,
  host_cache_dir: "/cache",
};

const setup = () => {
  const c = document.body.appendChild(document.createElement("div"));
  return { c, p: new SettingsPanelComponent(c) };
};
const flush = () => new Promise((r) => setTimeout(r, 0));
const field = (c: HTMLElement, n: string) => c.querySelector<HTMLInputElement>(`[name="${n}"]`)!;

describe("SettingsPanelComponent", () => {
  it("shows loading, then settings", async () => {
    stubFetch(() => jsonResponse(full));
    const { c, p } = setup();
    const done = p.load();
    expect(c.textContent).toContain("Loading runtime settings...");
    await done;
    expect(field(c, "max_runners").value).toBe("5");
    expect(field(c, "host_cache_dir").value).toBe("/cache");
    expect(c.querySelector<HTMLOptionElement>('option[value="docker"]')!.selected).toBe(true);
  });

  it("falls back to defaults and shows load errors", async () => {
    stubFetch(() => jsonResponse({}, { ok: false, status: 500, statusText: "Err" }));
    const { c, p } = setup();
    await p.load();
    expect(c.textContent).toContain("Failed to load settings: Failed to fetch settings: 500 Err");
    expect(field(c, "max_runners").value).toBe("3");
    expect(field(c, "runner_memory").value).toBe("4G");
    expect(field(c, "host_cache_dir").value).toBe("");
  });

  it("selects every backend and arch option", async () => {
    const backends = ["auto", "docker", "orbstack-vm", "wsl2", "multipass"];
    const arches = ["both", "arm64", "amd64"];
    for (const [i, b] of backends.entries()) {
      stubFetch(() =>
        jsonResponse({
          ...full,
          runner_backend: b,
          runner_arch: arches[i % 3],
          auto_route_vm: i % 2 === 0,
          cache_enabled: i % 2 === 1,
          proxies_enabled: i % 2 === 0,
          native_arch_override: i % 2 ? "" : "x",
          host_cache_dir: i % 2 ? "" : "/c",
        }),
      );
      const { c, p } = setup();
      await p.load();
      expect(c.querySelector<HTMLOptionElement>(`option[value="${b}"]`)!.selected).toBe(true);
      expect(c.querySelector<HTMLOptionElement>(`option[value="${arches[i % 3]}"]`)!.selected).toBe(true);
    }
  });

  it("saves settings with a rotated token", async () => {
    const calls: { url: string; init?: RequestInit }[] = [];
    stubFetch((url, init) => {
      calls.push({ url, init });
      return jsonResponse(full);
    });
    const { c, p } = setup();
    await p.load();
    field(c, "access_token").value = "  tok  ";
    c.querySelector("form")!.dispatchEvent(new Event("submit", { cancelable: true }));
    await flush();
    await flush();
    const post = calls.find((x) => x.init?.method === "POST")!;
    const body = JSON.parse(post.init!.body as string);
    expect(body.access_token).toBe("tok");
    expect(body.auto_route_vm).toBe(true);
    expect(body.proxies_enabled).toBe(false);
    expect(c.textContent).toContain("✓ Settings applied live");
  });

  it("saves without a token and reports failures", async () => {
    const f = stubFetch(() => jsonResponse(full));
    const { c, p } = setup();
    await p.load();
    c.querySelector("form")!.dispatchEvent(new Event("submit", { cancelable: true }));
    await flush();
    await flush();
    const post = f.mock.calls.find((x) => x[1]?.method === "POST")!;
    expect(JSON.parse(post[1]!.body as string).access_token).toBeUndefined();

    stubFetch(() => jsonResponse({ error: "nope" }, { ok: false }));
    c.querySelector("form")!.dispatchEvent(new Event("submit", { cancelable: true }));
    await flush();
    await flush();
    expect(c.textContent).toContain("✗ Error saving settings: nope");
    vi.restoreAllMocks();
  });
});
