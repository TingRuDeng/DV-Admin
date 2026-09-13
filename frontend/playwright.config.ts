import { defineConfig, devices } from "@playwright/test";
import { loadEnv } from "vite";

const env = loadEnv("development", process.cwd(), "");
const appPort = Number(process.env.VITE_APP_PORT || env.VITE_APP_PORT || 9527);
const appBaseUrl = `http://127.0.0.1:${appPort}`;

export default defineConfig({
  testDir: "./e2e",
  testIgnore: process.env.REAL_AUTH_CAPTURE_FILE
    ? ["**/real-backend-smoke.spec.ts"]
    : ["**/real-backend-smoke.spec.ts", "**/real-auth.spec.ts"],
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: appBaseUrl,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "pnpm dev -- --host 127.0.0.1 --strictPort",
    url: appBaseUrl,
    reuseExistingServer: false,
  },
});
