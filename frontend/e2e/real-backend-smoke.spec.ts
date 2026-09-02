import { expect, test, type Page, type Response } from "@playwright/test";

const backendName = requireEnv("REAL_BACKEND_NAME");
const username = requireEnv("REAL_BACKEND_USERNAME");
const password = requireEnv("REAL_BACKEND_PASSWORD");
const noticeTitle = requireEnv("REAL_BACKEND_NOTICE_TITLE");
const noticeContent = requireEnv("REAL_BACKEND_NOTICE_CONTENT");
const updatedName = `${backendName} E2E 用户`;

test.describe(`前端连接真实 ${backendName} 后端`, () => {
  test("完成个人中心、用户管理和通知公告代表页闭环", async ({ page }) => {
    const failedApiResponses = collectFailedApiResponses(page);

    await page.goto("/login?redirect=%2Fprofile");
    await page.getByLabel("用户名").fill(username);
    await page.getByLabel("密码").fill(password);

    const loginBootstrap = Promise.all([
      waitForApiResponse(page, "/api/v1/oauth/login/", "POST"),
      waitForApiResponse(page, "/api/v1/oauth/info/", "GET"),
      waitForApiResponse(page, "/api/v1/oauth/menus/routes/", "GET"),
      waitForApiResponse(page, "/api/v1/information/profile/", "GET"),
    ]);
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();
    await loginBootstrap;

    await expect(page).toHaveURL(/\/profile$/);
    await expect(page.locator(".user-profile__name")).toHaveText(username);
    await expect(page.locator(".ff-profile-user__display-name")).toBeVisible();

    await page.locator(".ff-profile-user__edit").click();
    const profileDialog = page.getByRole("dialog", { name: "账号资料" });
    await profileDialog.locator("input").first().fill(updatedName);
    const updateProfileResponse = waitForApiResponse(page, "/api/v1/information/profile/", "PUT");
    await profileDialog.getByRole("button", { name: /确\s*定/ }).click();
    await updateProfileResponse;
    await expect(page.getByText("账号资料修改成功")).toBeVisible();
    await expect(page.locator(".ff-profile-user__display-name")).toHaveText(updatedName);

    const avatarResponse = waitForApiResponse(page, "/api/v1/information/change-avatar/", "POST");
    await page.locator('.ff-profile-user input[type="file"]').setInputFiles({
      name: "playwright-avatar.gif",
      mimeType: "image/gif",
      buffer: Buffer.from("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=", "base64"),
    });
    await avatarResponse;
    const avatarImage = page.locator(".ff-profile-user__avatar img");
    await expect(avatarImage).toHaveAttribute("src", /\/media\/avatar\//);
    await expect
      .poll(() => avatarImage.evaluate((image: HTMLImageElement) => image.naturalWidth))
      .toBeGreaterThan(0);

    await page.goto("/my-notice");
    const noticeRow = page.locator(".el-table__row", { hasText: noticeTitle });
    await expect(noticeRow).toBeVisible();
    await noticeRow.getByRole("button", { name: "查看" }).click();
    const noticeDialog = page.getByRole("dialog", { name: noticeTitle });
    await expect(noticeDialog).toContainText(noticeContent);
    await page.keyboard.press("Escape");
    await expect(noticeDialog).toBeHidden();

    await page.reload();
    await expect(page.locator(".el-table__row", { hasText: noticeTitle })).toContainText("已读");

    const userPageResponse = waitForApiResponse(page, "/api/v1/system/users/", "GET");
    await page.goto("/runtime-contract/user");
    await userPageResponse;
    await expect(page).toHaveURL(/\/runtime-contract\/user$/);
    const userTable = page.locator(".ff-user-page .ff-table");
    await expect(userTable.getByText(username, { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "新增用户" })).toBeVisible();
    await expect(page.getByRole("button", { name: "导入用户" })).toBeVisible();
    await expect(page.getByRole("button", { name: "导出用户" })).toBeVisible();
    await page.getByRole("button", { name: "新增用户" }).click();
    const userDrawer = page.locator(".el-drawer", { hasText: "新增用户" });
    await expect(userDrawer).toBeVisible();
    await userDrawer.getByRole("button", { name: /取\s*消/ }).click();

    const noticePageResponse = waitForApiResponse(page, "/api/v1/system/notices/page", "GET");
    await page.locator(".layout__sidebar .el-menu-item", { hasText: "通知公告" }).click();
    await noticePageResponse;
    await expect(page).toHaveURL(/\/runtime-contract\/notices$/);
    const managementRow = page.locator(".ff-notice-page .el-table__row", {
      hasText: noticeTitle,
    });
    await expect(managementRow).toContainText("已发布");
    await expect(managementRow.getByRole("button", { name: "撤回" })).toBeVisible();
    await managementRow.getByRole("button", { name: "查看" }).click();
    const managementDialog = page.locator(".ff-notice-detail-dialog");
    await expect(managementDialog).toContainText(noticeContent);
    await managementDialog.getByRole("button", { name: "关闭通知详情" }).click();

    await page.getByRole("button", { name: "新增通知" }).click();
    const noticeDrawer = page.locator(".el-drawer", { hasText: "新增公告" });
    await expect(noticeDrawer).toBeVisible();
    await noticeDrawer.getByRole("button", { name: /取\s*消/ }).click();
    expect(failedApiResponses).toEqual([]);
  });
});

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required for the real backend Playwright smoke`);
  }
  return value;
}

function waitForApiResponse(page: Page, path: string, method: string): Promise<Response> {
  return page.waitForResponse(
    (response) =>
      response.url().includes(path) &&
      response.request().method() === method &&
      response.status() === 200
  );
}

function collectFailedApiResponses(page: Page): string[] {
  const failures: string[] = [];
  page.on("response", (response) => {
    if (response.url().includes("/dev-api/api/v1/") && response.status() >= 400) {
      failures.push(`${response.status()} ${response.request().method()} ${response.url()}`);
    }
  });
  return failures;
}
