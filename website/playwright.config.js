import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "list",
  use: {
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command:
        'DEPLOY_BASE="" npm run build && DEPLOY_BASE="" npx astro preview --port 4321',
      port: 4321,
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
    },
    {
      command:
        "pnpm --dir ../web run build && pnpm --dir ../web exec vite preview --host 127.0.0.1 --port 49505",
      port: 49505,
      reuseExistingServer: !process.env.CI,
      timeout: 90000,
    },
    {
      // Real control plane + autoscaler against a fake GitHub API, serving its own
      // dashboard build (journeys.spec.js). Needs Go.
      command:
        "pnpm --dir ../web exec vite build --outDir ../test/e2e/.dist --emptyOutDir && cd .. && E2E_DIST_DIR=test/e2e/.dist go run -tags e2e ./test/e2e/harness",
      port: 49515,
      reuseExistingServer: !process.env.CI,
      timeout: 180000,
    },
  ],
});
