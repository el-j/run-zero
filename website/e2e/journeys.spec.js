import { test, expect } from "@playwright/test";

// Operator journeys against the real control plane: the Go API server, the
// autoscaler and the built dashboard, wired to a fake GitHub API and an
// in-memory runner driver by test/e2e/harness. Nothing here is stubbed in the
// browser, so a regression anywhere between GitHub polling and rendering fails.
const DASHBOARD = "http://127.0.0.1:49515/";
const FAKE_GITHUB = "http://127.0.0.1:49599";
const REPO = "el-j/landing.inquam-services";
const RUN_URL = `https://github.com/${REPO}/actions/runs/9001`;

test.describe.configure({ mode: "serial" });

test.describe("RunZero operator journeys (real control plane)", () => {
  test.beforeEach(async ({ request }) => {
    await request.post(`${FAKE_GITHUB}/__e2e/reset`);
  });

  test("queued job gets one runner, fails, and can be retried from the dashboard", async ({ page, request }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(DASHBOARD);

    // 1. The autoscaler spawns exactly one runner for the queued job. The fake
    //    driver lists it under a lossy OrbStack-style name, yet the dashboard
    //    must show the real repo and a working run link.
    await page.locator("#tab-btn-runners").click();
    await page.locator("#view-mode-table").click();
    const row = page.locator("#runners-table-body tr").first();
    await expect(row.locator("td").nth(1)).toHaveText(REPO, { timeout: 15000 });
    await expect(row.locator("a.run-link")).toHaveAttribute("href", RUN_URL);
    await expect(page.locator("#tab-runners-count")).toHaveText("1");

    // A few more scale cycles must not spawn duplicates for the same job.
    await page.waitForTimeout(3000);
    await expect(page.locator("#tab-runners-count")).toHaveText("1");

    // 2. The job fails on GitHub: the runner is pruned and the failure shows up
    //    under completed jobs with its diagnosis.
    await request.post(`${FAKE_GITHUB}/__e2e/fail`);
    await expect(page.locator("#tab-runners-count")).toHaveText("0", { timeout: 15000 });
    await page.locator("#tab-btn-jobs").click();
    const jobs = page.locator("#jobs-list");
    await expect(jobs).toContainText("Step 4 “Run tests” failed.", { timeout: 15000 });
    await expect(jobs).toContainText("assertion failed in retry path");

    // 3. Retrying from the dashboard reaches GitHub's rerun-failed-jobs endpoint.
    page.once("dialog", (dialog) => dialog.accept());
    await page.locator(".job-rerun-btn").filter({ visible: true }).first().click();
    await expect(page.locator("#toast-container")).toContainText("9001");

    const { calls } = await (await request.get(`${FAKE_GITHUB}/__e2e/calls`)).json();
    expect(calls).toContain(`POST /repos/${REPO}/actions/runs/9001/rerun-failed-jobs`);
  });
});
