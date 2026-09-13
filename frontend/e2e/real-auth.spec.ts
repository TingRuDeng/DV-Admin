import { expect, test } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";

function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required for real auth Playwright`);
  return value;
}

test("real backend registration, password recovery and re-login", async ({ page }) => {
  const captureFile = required("REAL_AUTH_CAPTURE_FILE");
  const suffix = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
  const username = `real-auth-${suffix}`;
  const email = `real-auth-${suffix}@example.com`;
  const password = "first sufficiently long passphrase";
  const resetPassword = "second sufficiently long passphrase";

  const capturedCode = (purpose: string) => {
    if (!existsSync(captureFile)) return "";
    const text = readFileSync(captureFile, "utf-8");
    return text.match(new RegExp(`${purpose}:${email.replace(".", "\\.")}=(\\d{6})`))?.[1] ?? "";
  };

  await page.goto("/login");
  await page.getByText(/注册账号|Register account/i, { exact: true }).click();
  const registerForm = page.getByRole("heading", { name: /注\s*册|Register/i }).locator("..");
  await registerForm.getByPlaceholder(/^(用户名|Username)$/i).fill(username);
  await registerForm.getByPlaceholder(/^(邮箱|Email)$/i).fill(email);
  await registerForm.getByPlaceholder(/^(密码|Password)$/i).fill(password);
  await registerForm.getByPlaceholder(/确认密码|Confirm password/i).fill(password);
  await registerForm.getByRole("button", { name: /发送验证码|Send code/i }).click();
  await expect.poll(() => capturedCode("register")).toMatch(/^\d{6}$/);
  await registerForm.getByPlaceholder(/^(邮箱验证码|Email code)$/i).fill(capturedCode("register"));
  await registerForm.getByText(/我已同意并阅读|I agree/i, { exact: false }).click();
  await registerForm.getByRole("button", { name: /注册|Register/i }).click();
  await expect(page.getByText(/忘记密码|Forget password/i)).toBeVisible();

  await page.getByText(/忘记密码|Forget password/i).click({ force: true });
  const resetForm = page.locator(".login-form").filter({ hasText: /重置密码|Reset password/i });
  await resetForm.getByPlaceholder(/^(用户名|Username)$/i).fill(username);
  await resetForm.getByPlaceholder(/^(邮箱|Email)$/i).fill(email);
  await resetForm.getByPlaceholder(/^(新密码|New password)$/i).fill(resetPassword);
  await resetForm.getByPlaceholder(/确认密码|Confirm password/i).fill(resetPassword);
  await resetForm.getByRole("button", { name: /发送验证码|Send code/i }).click();
  await expect.poll(() => capturedCode("reset_password")).toMatch(/^\d{6}$/);
  await resetForm
    .getByPlaceholder(/^(邮箱验证码|Email code)$/i)
    .fill(capturedCode("reset_password"));
  const resetResponsePromise = page.waitForResponse(
    (response) =>
      response.url().includes("/api/v1/oauth/password/reset/") &&
      response.request().method() === "POST"
  );
  await resetForm.getByRole("button", { name: /重置密码|Reset password/i }).click();
  expect((await resetResponsePromise).status()).toBe(200);
  await expect(page.getByText(/^(登\s*录|Login)$/i).last()).toBeVisible();

  const loginForm = page
    .locator(".login-form")
    .filter({ has: page.locator("#login-username-input") });
  await expect(loginForm.getByLabel("用户名")).toBeVisible();
  await loginForm.getByLabel("用户名").fill(username);
  await loginForm.getByLabel("密码").fill(resetPassword);
  const loginResponsePromise = page.waitForResponse(
    (response) =>
      response.url().includes("/api/v1/oauth/login/") && response.request().method() === "POST"
  );
  await loginForm.getByRole("button", { name: /登\s*录|Login/i }).click();
  expect((await loginResponsePromise).status()).toBe(200);
  await expect(page.getByRole("heading", { name: /你好|Hello/i })).toBeVisible({ timeout: 30_000 });
  await expect(page).not.toHaveURL(/\/login/, { timeout: 30_000 });
});
