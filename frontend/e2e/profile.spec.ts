import { expect, test, type Page, type Route } from "@playwright/test";

interface ProfileState {
  profile: {
    id: string;
    username: string;
    name: string;
    avatar: string;
    gender: number;
    mobile: string;
    email: string;
    deptName: string;
    roleNames: string;
  };
  passwordPayloads: unknown[];
  avatarUploads: number;
}

const API_PREFIX = "/dev-api";
const ONE_PIXEL_GIF = Buffer.from("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=", "base64");

function success(data: unknown) {
  return { code: 20000, message: "成功", data };
}

async function fulfillJson(route: Route, data: unknown, status = 200) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(data),
  });
}

function createProfileState(): ProfileState {
  return {
    profile: {
      id: "1",
      username: "profile_admin",
      name: "个人中心管理员",
      avatar: "/media/avatar/profile.gif",
      gender: 1,
      mobile: "13800138000",
      email: "profile@example.com",
      deptName: "研发部",
      roleNames: "管理员",
    },
    passwordPayloads: [],
    avatarUploads: 0,
  };
}

async function installProfileMocks(page: Page, state: ProfileState) {
  await page.route("**/media/avatar/*.gif", async (route) => {
    await route.fulfill({ status: 200, contentType: "image/gif", body: ONE_PIXEL_GIF });
  });

  await page.route(`**${API_PREFIX}/api/v1/**`, async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname.replace(API_PREFIX, "");
    const method = request.method();

    if (method === "POST" && path === "/api/v1/oauth/login/") {
      await fulfillJson(
        route,
        success({
          accessToken: "profile-access-token",
          refreshToken: "profile-refresh-token",
          tokenType: "bearer",
          expiresIn: 3600,
        })
      );
      return;
    }

    if (method === "GET" && path === "/api/v1/oauth/info/") {
      await fulfillJson(
        route,
        success({
          ...state.profile,
          roles: ["admin"],
          perms: [],
        })
      );
      return;
    }

    if (method === "GET" && path === "/api/v1/oauth/menus/routes/") {
      await fulfillJson(route, success([]));
      return;
    }

    if (method === "GET" && path === "/api/v1/information/profile/") {
      await fulfillJson(route, success(state.profile));
      return;
    }

    if (method === "PUT" && path === "/api/v1/information/profile/") {
      Object.assign(state.profile, request.postDataJSON());
      await fulfillJson(route, success(state.profile));
      return;
    }

    if (method === "PUT" && path === "/api/v1/information/password") {
      state.passwordPayloads.push(request.postDataJSON());
      await fulfillJson(route, success(null));
      return;
    }

    if (method === "POST" && path === "/api/v1/information/change-avatar/") {
      state.avatarUploads += 1;
      await fulfillJson(route, success({ url: "/media/avatar/profile-updated.gif" }));
      return;
    }

    if (method === "GET" && path === "/api/v1/system/notices/my-page/") {
      await fulfillJson(route, success({ list: [], total: 0 }));
      return;
    }

    await fulfillJson(
      route,
      { code: 404, message: `未 mock 的接口: ${method} ${path}`, data: null },
      404
    );
  });
}

async function login(page: Page) {
  await page.goto("/login?redirect=%2Fprofile");
  await page.getByLabel("用户名").fill("profile_admin");
  await page.getByLabel("密码").fill("123456");
  await page.getByRole("button", { name: /登\s*录|Login/i }).click();
  await expect(page).toHaveURL(/\/profile$/);
  await expect(page.locator(".ff-profile-user__display-name")).toHaveText("个人中心管理员");
}

test.describe("个人中心代表页 smoke", () => {
  test("移动端支持资料、头像、密码与静态资源 URL", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    const state = createProfileState();
    await installProfileMocks(page, state);
    await login(page);

    await expect(page.getByRole("button", { name: "上传头像" })).toBeVisible();
    await expect(page.getByRole("button", { name: "编辑账号资料" })).toBeVisible();

    await page.getByRole("button", { name: "编辑账号资料" }).click();
    const accountDialog = page.getByRole("dialog", { name: "账号资料" });
    await expect(accountDialog).toBeVisible();
    await expect
      .poll(() => accountDialog.evaluate((element) => element.getBoundingClientRect().width))
      .toBeLessThanOrEqual(390);
    await accountDialog.getByRole("button", { name: /取\s*消/ }).click();

    await page.getByRole("button", { name: "上传头像" }).click();
    await page.locator('.ff-profile-user input[type="file"]').setInputFiles({
      name: "profile-updated.gif",
      mimeType: "image/gif",
      buffer: ONE_PIXEL_GIF,
    });
    await expect.poll(() => state.avatarUploads).toBe(1);
    await expect(page.locator(".ff-profile-user__avatar img")).toHaveAttribute(
      "src",
      "http://127.0.0.1:8769/media/avatar/profile-updated.gif"
    );

    await page.getByRole("button", { name: "修改", exact: true }).click();
    const passwordDialog = page.getByRole("dialog", { name: "修改密码" });
    const passwordInputs = passwordDialog.locator('input[type="password"]');
    await passwordInputs.nth(0).fill("old-pass");
    await passwordInputs.nth(1).fill("new-pass");
    await passwordInputs.nth(2).fill("different-pass");
    await passwordDialog.getByRole("button", { name: /确\s*定/ }).click();
    await expect(page.getByText("两次输入的密码不一致")).toBeVisible();
    expect(state.passwordPayloads).toHaveLength(0);

    await passwordInputs.nth(2).fill("new-pass");
    await passwordDialog.getByRole("button", { name: /确\s*定/ }).click();
    await expect.poll(() => state.passwordPayloads.length).toBe(1);
    await expect(page.getByText("密码修改成功")).toBeVisible();

    const pageWidth = await page.evaluate(() => ({
      viewport: window.innerWidth,
      document: document.documentElement.scrollWidth,
    }));
    expect(pageWidth.document).toBeLessThanOrEqual(pageWidth.viewport);
  });
});
