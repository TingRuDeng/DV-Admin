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

  test("shows field errors without console errors when required fields are empty", async ({
    page,
  }) => {
    const consoleErrors: string[] = [];
    page.on("console", (message) => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });
    let loginRequests = 0;
    await page.route("**/oauth/login/**", async (route) => {
      loginRequests += 1;
      await route.abort();
    });

    await page.goto("/login");
    await page.getByLabel("用户名").fill("");
    await page.getByLabel("密码").fill("");
    await page.getByRole("button", { name: /登\s*录/ }).click();

    await expect(page.getByText("请输入用户名")).toBeVisible();
    await expect(page.getByText("请输入密码")).toBeVisible();
    expect(loginRequests).toBe(0);
    expect(consoleErrors).toEqual([]);
  });
});
