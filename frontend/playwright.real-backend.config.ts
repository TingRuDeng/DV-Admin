import { defineConfig, devices } from "@playwright/test";

const backendUrl = process.env.REAL_BACKEND_URL;
if (!backendUrl) {
  throw new Error("REAL_BACKEND_URL is required for the real backend Playwright smoke");
}

const appPort = Number(process.env.REAL_FRONTEND_PORT || 9530);
const appBaseUrl = `http://127.0.0.1:${appPort}`;

process.env.VITE_APP_API_URL = backendUrl;
process.env.VITE_APP_STATIC_URL = backendUrl;
process.env.VITE_APP_PORT = String(appPort);
process.env.VITE_LOGIN_DEFAULT_USERNAME = "";
process.env.VITE_LOGIN_DEFAULT_PASSWORD = "";
process.env.VITE_MOCK_DEV_SERVER = "false";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  timeout: 60_000,
  reporter: process.env.CI
    ? [["line"], ["html", { outputFolder: "playwright-report", open: "never" }]]
    : "list",
  use: {
    baseURL: appBaseUrl,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "real-backend-chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "pnpm dev -- --host 127.0.0.1 --strictPort",
    url: appBaseUrl,
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
