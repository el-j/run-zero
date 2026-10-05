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
      command: "PYTHONPATH=../src ../.venv-dev/bin/python -m dashboard.server",
      port: 49505,
      reuseExistingServer: !process.env.CI,
      timeout: 30000,
      env: {
        PYTHONPATH: "../src",
        DASHBOARD_PORT: "49505",
        DASHBOARD_HOST: "127.0.0.1",
      },
    },
  ],
});
