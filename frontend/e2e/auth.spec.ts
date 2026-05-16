import { test, expect } from "@playwright/test";

test.describe("Auth E2E Tests", () => {
  test("should display login page", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading").first()).toBeVisible();
  });

  test("should have login form", async ({ page }) => {
    await page.goto("/login");
    const usernameInput = page.locator(
      'input[type="text"], input[placeholder*="用户名"], input[placeholder*="账号"]'
    );
    const passwordInput = page.locator('input[type="password"]');

    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
  });
});
