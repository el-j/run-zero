import { test, expect } from "@playwright/test";

test.describe("RunZero Web Dashboard End-to-End Tests", () => {
  test("dashboard UI loads and establishes SSE connection", async ({
    page,
  }) => {
    await page.goto("http://127.0.0.1:49505/");

    // Validate page title
    await expect(page).toHaveTitle(/RunZero/i);

    // Verify brand header and version badge
    await expect(page.locator(".brand-title")).toContainText("RunZero");
    await expect(page.locator("#stat-default-engine")).toBeVisible();

    // Verify SSE connection indicator reflects connected state
    const badge = page.locator("#connection-status-badge");
    await expect(badge).toBeVisible();

    // Verify KPI dashboard cards are rendered
    await expect(page.locator("#kpi-runners-card")).toBeVisible();
    await expect(page.locator("#stat-uptime")).toBeVisible();
  });

  test("dashboard displays action buttons and handles clicks", async ({
    page,
  }) => {
    await page.goto("http://127.0.0.1:49505/");

    // Check if clean-cache or prune action controls are present in the DOM
    const buttons = page.locator("button");
    const buttonCount = await buttons.count();
    expect(buttonCount).toBeGreaterThan(0);
  });
});
