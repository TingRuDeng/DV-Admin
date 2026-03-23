import { test, expect } from "@playwright/test";

test.describe("Navigation E2E Tests", () => {
  test("should navigate to dashboard", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const hasContent = await page.locator("body").textContent();
    expect(hasContent).toBeTruthy();
  });

  test("should have sidebar navigation", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const sidebar = page.locator('aside, .sidebar, [class*="side"]');
    await expect(sidebar.first()).toBeVisible();
  });
});

test.describe("System Management E2E Tests", () => {
  test("should navigate to user management", async ({ page }) => {
    await page.goto("/system/users");
    await page.waitForLoadState("networkidle");

    const hasContent = await page.locator("body").textContent();
    expect(hasContent).toBeTruthy();
  });

  test("should navigate to role management", async ({ page }) => {
    await page.goto("/system/roles");
    await page.waitForLoadState("networkidle");

    const hasContent = await page.locator("body").textContent();
    expect(hasContent).toBeTruthy();
  });

  test("should navigate to menu management", async ({ page }) => {
    await page.goto("/system/menus");
    await page.waitForLoadState("networkidle");

    const hasContent = await page.locator("body").textContent();
    expect(hasContent).toBeTruthy();
  });

  test("should navigate to department management", async ({ page }) => {
    await page.goto("/system/departments");
    await page.waitForLoadState("networkidle");

    const hasContent = await page.locator("body").textContent();
    expect(hasContent).toBeTruthy();
  });
});
