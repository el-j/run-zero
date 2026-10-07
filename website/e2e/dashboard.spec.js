import { test, expect } from "@playwright/test";

test.describe("RunZero Web Dashboard End-to-End Tests", () => {
  test.beforeEach(async ({ page }) => {
    const fleetResponse = {
      runners: [
        {
          id: "runner-live-1",
          name: "runner-live-1",
          status: "running",
          state: "running",
          target_repo: "el-j/run-zero",
          target_arch: "amd64",
          backend: "docker",
        },
      ],
      queued_jobs: [
        {
          id: 901,
          run_id: 1901,
          name: "integration",
          status: "queued",
          labels: ["self-hosted", "local", "amd64"],
          html_url: "https://github.com/el-j/run-zero/actions/runs/1901/job/901",
          repo: "el-j/run-zero",
        },
      ],
      completed_jobs: [
        {
          id: 777,
          run_id: 1777,
          name: "test-and-lint",
          workflow_name: "CI",
          head_branch: "develop",
          run_attempt: 2,
          conclusion: "failure",
          completed_at: "2026-10-07T17:00:00Z",
          duration_sec: 84,
          labels: ["self-hosted", "local"],
          html_url: "https://github.com/el-j/run-zero/actions/runs/1777/job/777",
          run_url: "https://github.com/el-j/run-zero/actions/runs/1777",
          repo: "el-j/run-zero",
          failed_step: "Run tests",
          failure_reason: "Step 4 “Run tests” failed.",
          messages: ["assertion failed in retry path"],
        },
      ],
      busy_runners: 1,
      max_runners: 4,
      free_slots: 3,
      repo_priority: ["el-j/run-zero"],
      paused_repos: [],
      rate_limit_remaining: 4970,
      rate_limit_limit: 5000,
      actions_billing: {
        included_minutes: 2000,
        total_minutes_used: 250,
        total_paid_minutes_used: 0,
      },
      autoscaler_status: "running",
      version: "1.0.0",
    };

    await page.route("**/api/stream", async (route) => {
      await route.abort();
    });

    await page.route("**/api/fleet", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(fleetResponse),
      });
    });

    await page.route("**/api/logs", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ logs: [{ timestamp: "2026-10-07T17:00:00Z", message: "daemon started" }] }),
      });
    });

    await page.route("**/api/cache", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_bytes: 3_145_728_000,
          total_human: "2.93 GiB",
          categories: [
            { category: "npm", bytes: 1_572_864_000, human_readable: "1.46 GiB" },
            { category: "pip", bytes: 1_048_576_000, human_readable: "1000 MiB" },
            { category: "go", bytes: 524_288_000, human_readable: "500 MiB" },
          ],
        }),
      });
    });

    await page.route("**/api/settings", async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            max_runners: 4,
            min_runners: 1,
            runner_cpus: 2,
            runner_memory: "5g",
            runner_backend: "auto",
            auto_route_vm: true,
            cache_enabled: true,
          }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ok: true, message: "saved" }),
      });
    });
  });

  test("drawer behaves as inline panel on desktop and keeps workspace visible", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("http://127.0.0.1:49505/");

    await expect(page).toHaveTitle(/RunZero/i);
    await expect(page.locator("#panel-fleet-control")).toBeVisible();

    await page.locator("#btn-open-drawer").click();
    await expect(page.locator("#telemetry-drawer")).toHaveClass(/open/);
    await expect(page.locator(".main-workspace-full")).toHaveClass(/drawer-open/);

    const drawerPosition = await page.locator("#telemetry-drawer").evaluate((el) => getComputedStyle(el).position);
    expect(drawerPosition).toBe("absolute");

    const panelBox = await page.locator("#panel-fleet-control").boundingBox();
    const drawerBox = await page.locator("#telemetry-drawer").boundingBox();
    expect(panelBox).toBeTruthy();
    expect(drawerBox).toBeTruthy();
    expect(panelBox.width).toBeGreaterThan(drawerBox.width);
  });

  test("failed completed jobs expose retry and trigger rerun-failed action", async ({ page }) => {
    let rerunPayload = null;
    await page.route("**/api/actions/workflow", async (route) => {
      rerunPayload = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ok: true, message: "Retry queued for run #1777" }),
      });
    });

    await page.goto("http://127.0.0.1:49505/");
    await page.locator("#tab-btn-jobs").click();
    await expect(page.locator("#jobs-list")).toContainText("Why it failed");
    await expect(page.locator("#jobs-list")).toContainText("Step 4 “Run tests” failed.");

    page.once("dialog", async (dialog) => dialog.accept());
    await page.locator(".job-rerun-btn").first().click();
    await expect(page.locator("#toast-container")).toContainText("Retry queued for run #1777");

    expect(rerunPayload).toEqual({
      repo: "el-j/run-zero",
      run_id: 1777,
      action: "rerun-failed",
    });
  });

  test("prune action calls lifecycle cleanup endpoint and reports success", async ({ page }) => {
    let pruneCalled = false;
    await page.route("**/api/actions/prune", async (route) => {
      pruneCalled = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ok: true, message: "Prune executed. Removed 1 finished runner(s).", pruned: 1 }),
      });
    });

    await page.goto("http://127.0.0.1:49505/");
    await page.locator("#btn-prune-runners").click();

    expect(pruneCalled).toBeTruthy();
    await expect(page.locator("#toast-container")).toContainText("Triggered fleet runner prune");
  });
});
