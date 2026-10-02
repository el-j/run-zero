import { test, expect } from "@playwright/test";

const BASE_URL =
  process.env.WEBSITE_BASE_URL || "http://localhost:4321/run-zero";

test.describe("RunZero Website End-to-End Tests", () => {
  test("homepage loads, displays branding and navigates", async ({ page }) => {
    await page.goto(`${BASE_URL}/`);

    // Validate title & main heading
    await expect(page).toHaveTitle(/RunZero/i);
    const mainHeading = page.locator("h1");
    await expect(mainHeading).toBeVisible();

    // Check presence of navigation links
    const docsLink = page.locator('a[href*="/docs"]').first();
    await expect(docsLink).toBeVisible();

    // Navigate to docs
    await docsLink.click();
    await expect(page).toHaveURL(/.*\/docs\/?/);
  });

  test("docs page renders documentation layout and topics", async ({
    page,
  }) => {
    await page.goto(`${BASE_URL}/docs/`);

    // Check main docs container or heading
    await expect(page.locator("body")).toContainText(/RunZero/i);
    await expect(page.locator("h1, h2").first()).toBeVisible();

    // Check navigation back or version link
    const versionsLink = page.locator('a[href*="/versions"]').first();
    if ((await versionsLink.count()) > 0) {
      await expect(versionsLink).toBeAttached();
    }
  });

  test("versions page renders version switcher and release history", async ({
    page,
  }) => {
    await page.goto(`${BASE_URL}/versions/`);

    await expect(page).toHaveTitle(/RunZero/i);
    await expect(page.locator("body")).toContainText(/Version/i);
  });
});
