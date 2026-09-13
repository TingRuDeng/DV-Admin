import { test, expect } from "@playwright/test";
import { expectReadableAction } from "./helpers/visual-assertions";

function success(data: unknown) {
  return { code: 20000, message: "成功", data };
}

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

  test("should expose registration and password recovery flows", async ({ page }) => {
    await page.goto("/login");
    await page.getByText(/注册账号|Register account/i, { exact: true }).click();
    await expect(page.getByPlaceholder(/^(邮箱|Email)$/i)).toBeVisible();
    await expect(page.getByPlaceholder(/^(邮箱验证码|Email code)$/i)).toBeVisible();
    await page.getByText(/^(登\s*录|Login)$/i).click();
    await expect(page.getByPlaceholder(/^(用户名|Username)$/i)).toBeVisible();
    await page.waitForTimeout(400);
    await page.getByText(/忘记密码|Forget password/i).click({ force: true });
    await expect(page.getByText(/重置密码|Reset password/i).first()).toBeVisible();
    await expect(page.getByPlaceholder(/^(新密码|New password)$/i)).toBeVisible();
  });

  test("should complete mocked registration and password recovery submissions", async ({
    page,
  }) => {
    const requests: string[] = [];
    await page.route("**/dev-api/api/v1/oauth/**", async (route) => {
      const request = route.request();
      const path = new URL(request.url()).pathname.replace("/dev-api", "");
      requests.push(`${request.method()} ${path}`);
      if (request.method() === "GET" && path === "/api/v1/oauth/captcha/") {
        await route.fulfill({
          contentType: "application/json",
          body: JSON.stringify(
            success({
              captchaKey: "mock-captcha",
              captchaBase64:
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
            })
          ),
        });
        return;
      }
      if (request.method() === "POST" && path === "/api/v1/oauth/email-code/") {
        await route.fulfill({
          contentType: "application/json",
          body: JSON.stringify(success(null)),
        });
        return;
      }
      if (request.method() === "POST" && path === "/api/v1/oauth/register/") {
        await route.fulfill({
          contentType: "application/json",
          body: JSON.stringify(success(null)),
        });
        return;
      }
      if (request.method() === "POST" && path === "/api/v1/oauth/password/reset/") {
        await route.fulfill({
          contentType: "application/json",
          body: JSON.stringify(success(null)),
        });
        return;
      }
      await route.continue();
    });

    await page.goto("/login");
    await page.getByText(/注册账号|Register account/i, { exact: true }).click();
    await page.getByPlaceholder(/^(用户名|Username)$/i).fill("mock-user");
    await page.getByPlaceholder(/^(邮箱|Email)$/i).fill("mock@example.com");
    await page.getByPlaceholder(/验证码|Captcha/i).fill("1234");
    await page.getByPlaceholder(/^(密码|Password)$/i).fill("a sufficiently long passphrase");
    await page
      .getByPlaceholder(/确认密码|Confirm password/i)
      .fill("a sufficiently long passphrase");
    await page.getByRole("button", { name: /发送验证码|Send code/i }).click();
    await page.getByPlaceholder(/^(邮箱验证码|Email code)$/i).fill("123456");
    await page.getByRole("button", { name: /注册|Register/i }).click();
    await expect(page.getByPlaceholder(/^(用户名|Username)$/i)).toBeVisible();

    await page.getByText(/忘记密码|Forget password/i).click({ force: true });
    const resetForm = page.locator(".login-form").filter({ hasText: /重置密码|Reset password/i });
    const resetInputs = resetForm.locator("input");
    await resetInputs.nth(0).fill("mock-user");
    await resetInputs.nth(1).fill("mock@example.com");
    await resetInputs.nth(3).fill("another sufficiently long passphrase");
    await resetInputs.nth(4).fill("another sufficiently long passphrase");
    await page.getByRole("button", { name: /发送验证码|Send code/i }).click();
    await resetInputs.nth(2).fill("654321");
    await page.getByRole("button", { name: /重置密码|Reset password/i }).click();
    await expect(page.getByText(/^(登\s*录|Login)$/i).last()).toBeVisible();
    expect(requests).toEqual(
      expect.arrayContaining([
        "POST /api/v1/oauth/email-code/",
        "POST /api/v1/oauth/register/",
        "POST /api/v1/oauth/password/reset/",
      ])
    );
  });

  test("should render the immersive login canvas without emoji decoration", async ({ page }) => {
    const runtimeErrors: string[] = [];
    page.on("pageerror", (error) => runtimeErrors.push(error.message));
    await page.goto("/login");

    await expect(page.locator(".login-container")).toBeVisible();
    await expect(page.locator(".login-art")).toBeVisible();
    await expect(page.locator(".login-card")).toBeVisible();
    await expect(page.getByLabel("用户名")).toBeVisible();
    await expect(page.getByLabel("密码")).toBeVisible();
    const icons = page.locator(".login-card .app-icon");
    expect(await icons.count()).toBeGreaterThan(0);
    for (const icon of await icons.all()) {
      await expect(icon).toHaveAttribute("aria-hidden", "true");
    }
    await expect(page.locator(".action-bar .navbar-icon-button")).toHaveCount(2);

    const bodyText = await page.locator("body").innerText();
    expect(bodyText).not.toMatch(/[\u{1f000}-\u{1faff}\u{2600}-\u{27bf}]/u);
    expect(runtimeErrors).toEqual([]);
  });

  for (const variant of [
    { width: 1440, height: 1000, theme: "dark" },
    { width: 1440, height: 1000, theme: "light" },
    { width: 390, height: 844, theme: "dark" },
  ]) {
    test(`login visual acceptance ${variant.theme} ${variant.width}`, async ({
      page,
    }, testInfo) => {
      await page.setViewportSize({ width: variant.width, height: variant.height });
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.addInitScript(
        (theme) => localStorage.setItem("vea:ui:theme", theme),
        variant.theme
      );
      await page.goto("/login");
      await expect(page.getByLabel("用户名")).toBeVisible();
      await expect(page.getByRole("button", { name: /登\s*录|Login/i })).toBeVisible();
      await expectReadableAction(page.getByRole("button", { name: /登\s*录|Login/i }));
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
      ).toBe(true);
      const screenshot = testInfo.outputPath(`login-${variant.theme}-${variant.width}.png`);
      await page.screenshot({ path: screenshot, fullPage: true, animations: "disabled" });
      await testInfo.attach("Login", { path: screenshot, contentType: "image/png" });
    });
  }
});
