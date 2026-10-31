import { beforeEach, describe, expect, it, vi } from "vitest";
import { jsonResponse, mountDashboard, stubFetch } from "../test/helpers";
import {
  launchRunner,
  openRunnerTerminal,
  pruneFleet,
  purgeAllCaches,
  purgeCacheCategory,
  retryFailedJobs,
  stopRunner,
  triggerQueueAction,
} from "./actions";
import { client } from "./api/client";
import { hooks } from "./hooks";
import { dom } from "./dom";

const toast = () => document.getElementById("toast-container")?.lastElementChild?.textContent ?? "";

function button(data: Record<string, string>): HTMLButtonElement {
  const b = document.createElement("button");
  Object.assign(b.dataset, data);
  b.innerHTML = "orig";
  return b;
}

beforeEach(() => {
  mountDashboard();
  vi.spyOn(hooks, "refreshState").mockResolvedValue();
  vi.spyOn(hooks, "loadCacheStats").mockResolvedValue();
});

describe("stopRunner", () => {
  it("does nothing when not confirmed", async () => {
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(false);
    const ctl = vi.spyOn(client, "controlRunner");
    await stopRunner(button({ runnerId: "1", runnerName: "n" }));
    expect(confirmSpy).toHaveBeenCalledWith("Stop and delete runner 'n'?");
    expect(ctl).not.toHaveBeenCalled();
  });

  it("warns about running jobs and stops the runner", async () => {
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(true);
    const ctl = vi.spyOn(client, "controlRunner").mockResolvedValue({} as never);
    await stopRunner(button({ runnerId: "1", runnerName: "n", jobId: "9" }));
    expect(confirmSpy.mock.calls[0][0]).toContain("Job #9");
    expect(ctl).toHaveBeenCalledWith("stop", { runnerId: "1" });
    expect(hooks.refreshState).toHaveBeenCalled();
    expect(toast()).toContain("Stopped runner n");
  });

  it("reports failures", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    vi.spyOn(client, "controlRunner").mockRejectedValue(new Error("nope"));
    await stopRunner(button({ runnerId: "1", runnerName: "n" }));
    expect(toast()).toContain("Failed stopping runner: nope");
  });
});

describe("openRunnerTerminal", () => {
  const btn = () => button({ runnerId: "1", runnerName: "n", backend: "docker" });

  it("copies the command and reports a launched terminal", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    vi.spyOn(client, "controlRunner").mockResolvedValue({
      command: "docker exec",
      terminal_launched: true,
    } as never);
    const b = btn();
    await openRunnerTerminal(b);
    expect(writeText).toHaveBeenCalledWith("docker exec");
    expect(toast()).toContain("Terminal opened for n!");
    expect(b.innerHTML).toBe("orig");
    expect(b.disabled).toBe(false);
  });

  it("reports the copied command when no terminal launched and clipboard fails", async () => {
    vi.stubGlobal("navigator", { clipboard: { writeText: vi.fn().mockRejectedValue(new Error("x")) } });
    vi.spyOn(client, "controlRunner").mockResolvedValue({ command: "cmd" } as never);
    await openRunnerTerminal(btn());
    expect(toast()).toContain("Command copied: cmd");
  });

  it("handles a response without a command", async () => {
    vi.spyOn(client, "controlRunner").mockResolvedValue({ terminal_launched: true } as never);
    await openRunnerTerminal(btn());
    expect(toast()).toContain("Terminal opened");
  });

  it("reports failures and restores the button", async () => {
    vi.spyOn(client, "controlRunner").mockRejectedValue(new Error("bad"));
    const b = btn();
    await openRunnerTerminal(b);
    expect(toast()).toContain("Failed opening terminal: bad");
    expect(b.disabled).toBe(false);
  });
});

describe("retryFailedJobs", () => {
  it("ignores invalid buttons", async () => {
    const confirmSpy = vi.spyOn(window, "confirm");
    await retryFailedJobs(button({ repo: "", runId: "1" }));
    await retryFailedJobs(button({ repo: "o/r", runId: "x" }));
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it("respects a declined confirmation", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    const spy = vi.spyOn(client, "triggerWorkflowAction");
    await retryFailedJobs(button({ repo: "o/r", runId: "1" }));
    expect(spy).not.toHaveBeenCalled();
  });

  it("uses the server message or a default", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const spy = vi.spyOn(client, "triggerWorkflowAction");
    spy.mockResolvedValueOnce({ message: "queued!" } as never);
    await retryFailedJobs(button({ repo: "o/r", runId: "1" }));
    expect(toast()).toContain("queued!");
    spy.mockResolvedValueOnce({} as never);
    await retryFailedJobs(button({ repo: "o/r", runId: "1" }));
    expect(toast()).toContain("Retry queued for o/r run #1");
  });

  it("reports failures", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    vi.spyOn(client, "triggerWorkflowAction").mockRejectedValue(new Error("x"));
    await retryFailedJobs(button({ repo: "o/r", runId: "1" }));
    expect(toast()).toContain("Failed to retry jobs: x");
  });
});

describe("triggerQueueAction", () => {
  const btn = () => button({ repo: "o/r", runId: "5", action: "cancel" });

  it("skips when declined", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    const spy = vi.spyOn(client, "triggerWorkflowAction");
    await triggerQueueAction(btn());
    expect(spy).not.toHaveBeenCalled();
  });

  it("triggers and refreshes", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const spy = vi.spyOn(client, "triggerWorkflowAction").mockResolvedValue({} as never);
    await triggerQueueAction(btn());
    expect(spy).toHaveBeenCalledWith("o/r", 5, "cancel");
    expect(hooks.refreshState).toHaveBeenCalled();
  });

  it("reports failures", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    vi.spyOn(client, "triggerWorkflowAction").mockRejectedValue(new Error("x"));
    await triggerQueueAction(btn());
    expect(toast()).toContain("Action failed: x");
  });
});

describe("pruneFleet", () => {
  it("posts and refreshes", async () => {
    const f = stubFetch(() => jsonResponse({}));
    await pruneFleet();
    expect(f).toHaveBeenCalledWith("/api/actions/prune", expect.objectContaining({ method: "POST" }));
    expect(hooks.refreshState).toHaveBeenCalled();
  });

  it("reports failures", async () => {
    stubFetch(() => Promise.reject(new Error("down")));
    await pruneFleet();
    expect(toast()).toContain("Prune failed: down");
  });
});

describe("cache purges", () => {
  it("purgeAllCaches covers decline, success and failure", async () => {
    const confirmSpy = vi.spyOn(window, "confirm");
    const purge = vi.spyOn(client, "purgeCache");
    confirmSpy.mockReturnValueOnce(false);
    await purgeAllCaches();
    expect(purge).not.toHaveBeenCalled();
    confirmSpy.mockReturnValue(true);
    purge.mockResolvedValueOnce({} as never);
    await purgeAllCaches();
    expect(hooks.loadCacheStats).toHaveBeenCalled();
    purge.mockRejectedValueOnce(new Error("x"));
    await purgeAllCaches();
    expect(toast()).toContain("Purge failed: x");
  });

  it("purgeCacheCategory covers decline, success and failure", async () => {
    const confirmSpy = vi.spyOn(window, "confirm");
    const purge = vi.spyOn(client, "purgeCache");
    confirmSpy.mockReturnValueOnce(false);
    await purgeCacheCategory(button({ purgeCategory: "apt" }));
    expect(purge).not.toHaveBeenCalled();
    confirmSpy.mockReturnValue(true);
    purge.mockResolvedValueOnce({} as never);
    await purgeCacheCategory(button({ purgeCategory: "apt" }));
    expect(purge).toHaveBeenCalledWith({ category: "apt" });
    expect(toast()).toContain("Purged apt cache");
    purge.mockRejectedValueOnce(new Error("x"));
    await purgeCacheCategory(button({ purgeCategory: "apt" }));
    expect(toast()).toContain("Purge error: x");
  });
});

describe("launchRunner", () => {
  const modal = () => document.createElement("dialog") as HTMLDialogElement;

  it("requires a repository", async () => {
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
    dom.manualRepoInput!.value = "  ";
    await launchRunner(modal());
    expect(alertSpy).toHaveBeenCalled();
  });

  it("launches with the selected arch", async () => {
    dom.manualRepoInput!.value = " o/r ";
    dom.manualArchSelect!.value = "arm64";
    const ctl = vi.spyOn(client, "controlRunner").mockResolvedValue({} as never);
    const m = modal();
    m.open = true;
    await launchRunner(m);
    expect(ctl).toHaveBeenCalledWith("start", { repo: "o/r", arch: "arm64" });
    expect(m.open).toBe(false);
    expect(hooks.refreshState).toHaveBeenCalled();
  });

  it("reports failures", async () => {
    dom.manualRepoInput!.value = "o/r";
    vi.spyOn(client, "controlRunner").mockRejectedValue(new Error("x"));
    await launchRunner(modal());
    expect(toast()).toContain("Launch failed: x");
  });

  it("handles missing inputs", async () => {
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
    (dom as { manualRepoInput: unknown }).manualRepoInput = null;
    (dom as { manualArchSelect: unknown }).manualArchSelect = null;
    await launchRunner(modal());
    expect(alertSpy).toHaveBeenCalled();
  });

  it("defaults the arch when only the select is missing", async () => {
    dom.manualRepoInput!.value = "o/r";
    (dom as { manualArchSelect: unknown }).manualArchSelect = null;
    const ctl = vi.spyOn(client, "controlRunner").mockResolvedValue({} as never);
    await launchRunner(modal());
    expect(ctl).toHaveBeenCalledWith("start", { repo: "o/r", arch: "amd64" });
  });
});
