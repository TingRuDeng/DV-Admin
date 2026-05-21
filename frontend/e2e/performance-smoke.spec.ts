import { expect, test } from "@playwright/test";

const MAX_LOGIN_PAGE_DURATION_MS = 8000;
const MAX_CRITICAL_RESOURCE_COUNT = 180;

test.describe("性能预算 smoke", () => {
  test("登录页首屏加载保持在宽松预算内", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType("navigation")[0];
      const resources = performance.getEntriesByType("resource");
      const criticalResources = resources.filter((entry) =>
        ["script", "link", "css"].includes(entry.initiatorType)
      );

      return {
        duration: navigation?.duration ?? 0,
        criticalResourceCount: criticalResources.length,
      };
    });

    expect(metrics.duration).toBeLessThan(MAX_LOGIN_PAGE_DURATION_MS);
    expect(metrics.criticalResourceCount).toBeLessThan(MAX_CRITICAL_RESOURCE_COUNT);
  });
});
