import { beforeEach, describe, expect, it } from "vitest";
import { jsonResponse, mountDashboard, stubFetch } from "../test/helpers";
import { initDom, dom } from "./dom";
import { openSettingsModal, saveSettings } from "./settings";

const toasts = () =>
  [...(document.getElementById("toast-container")?.children ?? [])] as HTMLElement[];
const toast = () => toasts().at(-1)?.textContent ?? "";
const toastIsError = () => toasts().at(-1)?.style.borderColor === "var(--crimson)";
const full = {
  max_runners: 7,
  min_runners: 2,
  runner_cpus: 4,
  runner_memory: "8G",
  runner_backend: "vm",
  runner_arch: "arm64",
  auto_route_vm: true,
  native_arch_override: "on",
  poll_interval: 20,
  discovery_interval: 600,
  cache_enabled: true,
  proxies_enabled: true,
  host_cache_dir: "/c",
};

function addOption(sel: HTMLSelectElement | null, ...values: string[]) {
  for (const v of values) sel!.add(new Option(v, v));
}

beforeEach(() => {
  mountDashboard();
  addOption(dom.selectRunnerBackend, "vm", "auto");
  addOption(dom.selectRunnerArch, "arm64", "both");
  addOption(dom.selectNativeOverride, "on", "off");
});

describe("openSettingsModal", () => {
  it("fills the form and opens the dialog", async () => {
    stubFetch(() => jsonResponse(full));
    await openSettingsModal();
    expect(dom.inputMaxRunners!.value).toBe("7");
    expect(dom.inputRunnerMemory!.value).toBe("8G");
    expect(dom.selectRunnerBackend!.value).toBe("vm");
    expect(dom.checkboxAutoRouteVm!.checked).toBe(true);
    expect(dom.inputCacheDir!.value).toBe("/c");
    expect(dom.settingsModal!.open).toBe(true);
  });

  it("applies defaults for an empty config", async () => {
    stubFetch(() => jsonResponse({}));
    await openSettingsModal();
    expect(dom.inputMaxRunners!.value).toBe("3");
    expect(dom.inputRunnerCpus!.value).toBe("2");
    expect(dom.inputRunnerMemory!.value).toBe("4G");
    expect(dom.selectRunnerBackend!.value).toBe("auto");
    expect(dom.selectRunnerArch!.value).toBe("both");
    expect(dom.selectNativeOverride!.value).toBe("off");
    expect(dom.inputPollInterval!.value).toBe("10");
    expect(dom.inputDiscoveryInterval!.value).toBe("300");
    expect(dom.inputCacheDir!.value).toBe("");
  });

  it("tolerates missing inputs", async () => {
    for (const el of document.querySelectorAll("#settings-modal input, #settings-modal select"))
      el.remove();
    initDom();
    stubFetch(() => jsonResponse(full));
    await openSettingsModal();
    expect(dom.settingsModal!.open).toBe(true);
  });

  it("does nothing without the dialog", async () => {
    document.body.innerHTML = "";
    initDom();
    const f = stubFetch(() => jsonResponse(full));
    await openSettingsModal();
    expect(f).not.toHaveBeenCalled();
  });

  it("reports load failures", async () => {
    stubFetch(() => jsonResponse({}, { ok: false, status: 500 }));
    await openSettingsModal();
    expect(toast()).toContain("Failed to load settings");
    expect(toastIsError()).toBe(true);
    expect(toasts()[0].textContent).toBe("Loading configuration...");
  });
});

describe("saveSettings", () => {
  it("posts the form values and refreshes", async () => {
    stubFetch(() => jsonResponse(full));
    await openSettingsModal();
    const f = stubFetch(() => jsonResponse({ success: true }));
    await saveSettings();
    const post = f.mock.calls.find((c) => c[1]?.method === "POST")!;
    expect(JSON.parse(post[1]!.body as string)).toEqual(full);
    expect(dom.settingsModal!.open).toBe(false);
    expect(toast()).toContain("Settings updated");
    expect(toastIsError()).toBe(false);
    expect(toasts().map((t) => t.textContent)).toContain("Applying configuration update...");
    // Reloads the settings and the fleet afterwards.
    const gets = f.mock.calls
      .filter((c) => !c[1]?.method || c[1].method === "GET")
      .map((c) => String(c[0]));
    expect(gets.some((u) => u.endsWith("/api/settings"))).toBe(true);
    expect(gets.some((u) => u.endsWith("/api/fleet"))).toBe(true);
  });

  it("omits optional fields whose inputs are missing", async () => {
    for (const el of document.querySelectorAll("#settings-modal input, #settings-modal select")) {
      if (!["input-max-runners", "input-min-runners"].includes(el.id)) el.remove();
    }
    initDom();
    dom.inputMaxRunners!.value = "1";
    dom.inputMinRunners!.value = "0";
    const f = stubFetch(() => jsonResponse({ success: true }));
    await saveSettings();
    const post = f.mock.calls.find((c) => c[1]?.method === "POST")!;
    expect(JSON.parse(post[1]!.body as string)).toEqual({ max_runners: 1, min_runners: 0 });
  });

  it("reports failures", async () => {
    stubFetch(() => jsonResponse({}, { ok: false }));
    await saveSettings();
    expect(toast()).toContain("Failed to save settings");
    expect(toastIsError()).toBe(true);
  });

  it("trims the memory and cache directory", async () => {
    dom.inputMaxRunners!.value = "1";
    dom.inputMinRunners!.value = "0";
    dom.inputRunnerMemory!.value = "  8G ";
    dom.inputCacheDir!.value = " /cache  ";
    const f = stubFetch(() => jsonResponse({ success: true }));
    await saveSettings();
    const body = JSON.parse(f.mock.calls.find((c) => c[1]?.method === "POST")![1]!.body as string);
    expect(body.runner_memory).toBe("8G");
    expect(body.host_cache_dir).toBe("/cache");
  });

  it("does not save without the dialog", async () => {
    const f = stubFetch(() => jsonResponse({}));
    (dom as { settingsModal: HTMLDialogElement | null }).settingsModal = null;
    await saveSettings();
    expect(f).not.toHaveBeenCalled();
  });

  it("bails out when required elements are missing", async () => {
    const f = stubFetch(() => jsonResponse({}));
    dom.inputMinRunners!.remove();
    initDom();
    await saveSettings();
    dom.settingsModal!.remove();
    initDom();
    await saveSettings();
    expect(f).not.toHaveBeenCalled();
  });
});
