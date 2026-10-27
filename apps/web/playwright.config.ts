import { defineConfig, devices } from "@playwright/test";

const artifactRoot = process.env.AUTOSOC_E2E_ARTIFACT_DIR ?? "E:/AUTOSOC/runtime-logs/playwright";

export default defineConfig({
  testDir: "./e2e",
  outputDir: `${artifactRoot}/test-results`,
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["html", { outputFolder: `${artifactRoot}/html-report`, open: "never" }],
  ],
  use: {
    baseURL: process.env.AUTOSOC_E2E_BASE_URL ?? "http://127.0.0.1:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    viewport: { width: 1280, height: 900 },
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
});
