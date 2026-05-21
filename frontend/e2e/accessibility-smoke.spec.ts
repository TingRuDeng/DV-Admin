import { expect, test } from "@playwright/test";

test.describe("可访问性 smoke", () => {
  test("登录页暴露标题、main landmark 和可命名表单控件", async ({ page }) => {
    await page.goto("/login");

    await expect(page.locator("main").first()).toBeVisible();
    await expect(page.getByRole("heading", { level: 2 })).toBeVisible();
    await expect(page.getByLabel("用户名")).toBeVisible();
    await expect(page.getByLabel("密码")).toBeVisible();
    await expect(page.getByRole("button", { name: /登\s*录|Login/i })).toBeVisible();
  });
});
