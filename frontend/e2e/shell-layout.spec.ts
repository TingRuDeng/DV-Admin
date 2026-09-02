import { expect, test, type Page, type Route } from "@playwright/test";

const API_PREFIX = "/dev-api";
const USER_PERMS = ["system:users:query"];

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

async function installShellMocks(page: Page) {
  await page.route(`**${API_PREFIX}/api/v1/**`, async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname.replace(API_PREFIX, "");
    const method = request.method();

    if (method === "POST" && path === "/api/v1/oauth/login/") {
      await fulfillJson(
        route,
        success({
          accessToken: "shell-access-token",
          refreshToken: "shell-refresh-token",
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
          id: "1",
          username: "admin",
          name: "管理员",
          avatar:
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32'/%3E",
          roles: ["admin"],
          perms: USER_PERMS,
        })
      );
      return;
    }

    if (method === "GET" && path === "/api/v1/oauth/menus/routes/") {
      await fulfillJson(
        route,
        success([
          {
            path: "/system",
            component: "Layout",
            name: "System",
            meta: { title: "系统管理", icon: "system" },
            children: [
              {
                path: "users",
                component: "system/user/index",
                name: "User",
                meta: {
                  title: "用户管理",
                  icon: "user",
                  perms: USER_PERMS,
                  keepAlive: true,
                  cacheKey: "User",
                },
              },
            ],
          },
        ])
      );
      return;
    }

    if (method === "GET" && path === "/api/v1/system/users/") {
      await fulfillJson(
        route,
        success({
          list: [
            {
              id: "101",
              username: "admin_mock",
              name: "管理员",
              deptName: "研发部",
              mobile: "13800138000",
              email: "admin@example.com",
              isActive: 1,
              roleNames: "管理员",
            },
          ],
          total: 1,
        })
      );
      return;
    }

    if (method === "GET" && path === "/api/v1/system/departments/") {
      await fulfillJson(route, success([{ id: 1, label: "研发部", name: "研发部", children: [] }]));
      return;
    }

    if (method === "GET" && path === "/api/v1/system/roles/options/") {
      await fulfillJson(route, success([{ id: 1, label: "管理员", value: 1 }]));
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

async function setPreferences(page: Page, preferences: Record<string, string>) {
  await page.addInitScript((values) => {
    Object.entries(values).forEach(([key, value]) => {
      if (localStorage.getItem(key) === null) {
        localStorage.setItem(key, value);
      }
    });
  }, preferences);
}

async function login(page: Page) {
  await page.goto("/login?redirect=%2Fsystem%2Fusers");
  await page.getByLabel("用户名").fill("admin");
  await page.getByLabel("密码").fill("123456");
  await page.getByRole("button", { name: /登\s*录|Login/i }).click();

  await expect(page).toHaveURL(/\/system\/users/);
  await expect(page.getByText("用户数据")).toBeVisible();
}

async function switchLayout(page: Page, layout: "left" | "top" | "mix") {
  await page.evaluate((value) => localStorage.setItem("vea:ui:layout", value), layout);
  await page.reload();
  await expect(page.locator(`.layout-${layout}`)).toBeVisible();
  await expect(page.getByText("用户数据")).toBeVisible();
}

test.describe("现代化壳层 smoke", () => {
  test("桌面端保持三种布局、TagsView、动态路由和暗色主题", async ({ page }) => {
    await installShellMocks(page);
    await setPreferences(page, {
      "vea:ui:layout": "left",
      "vea:ui:show_tags_view": "true",
      "vea:ui:theme": "light",
    });
    await login(page);

    await expect(page.locator(".layout-left .layout__sidebar")).toBeVisible();
    await expect(page.locator("main.app-main")).toBeVisible();
    await expect(page.locator(".tags-container")).toBeVisible();
    const tags = page.locator(".tags-container");
    const userTag = tags.getByRole("link", { name: "用户管理" });
    await expect(userTag).toHaveAttribute("aria-current", "page");

    const keywordInput = page.getByPlaceholder("用户名/昵称/手机号");
    await keywordInput.fill("缓存探针");
    await tags.getByRole("link", { name: "首页" }).press("Enter");
    await expect(page).toHaveURL(/\/dashboard/);
    await userTag.press("Enter");
    await expect(keywordInput).toHaveValue("缓存探针");

    await userTag.click({ button: "right" });
    await page.getByRole("menuitem", { name: "刷新" }).click();
    await expect(keywordInput).toHaveValue("");

    await userTag.click({ button: "right" });
    await page.getByRole("menuitem", { name: "关闭", exact: true }).click();
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(userTag).toHaveCount(0);

    await page.goto("/system/users");
    await expect(page.getByText("用户数据")).toBeVisible();

    await switchLayout(page, "top");
    await expect(page.locator(".layout-top .el-menu--horizontal")).toBeVisible();

    await switchLayout(page, "mix");
    await expect(page.locator(".layout-mix .layout__sidebar--left")).toBeVisible();

    await page.evaluate(() => localStorage.setItem("vea:ui:theme", "dark"));
    await page.reload();
    await expect(page.locator("html")).toHaveClass(/dark/);
    await expect(page.locator("main.app-main")).toBeVisible();
  });

  test("移动端三种布局提供可访问的抽屉导航", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await installShellMocks(page);
    await setPreferences(page, {
      "vea:ui:layout": "top",
      "vea:ui:show_tags_view": "true",
      "vea:ui:theme": "light",
    });
    await login(page);

    await expect(page.locator(".layout-top .layout__mobile-menu")).toHaveAttribute(
      "aria-hidden",
      "true"
    );
    const topToggle = page.getByRole("button", { name: "展开导航" });
    await expect(topToggle).toBeVisible();
    await topToggle.click();
    await expect(page.locator(".layout-top .layout__mobile-menu")).not.toHaveClass(/collapsed/);
    await expect(page.locator(".layout-top .layout__mobile-menu")).not.toHaveAttribute(
      "aria-hidden"
    );
    await expect(page.getByRole("button", { name: "关闭导航" })).toBeVisible();
    await page.getByRole("button", { name: "关闭导航" }).click();
    await expect(page.locator(".layout-top .layout__mobile-menu")).toHaveClass(/collapsed/);

    await switchLayout(page, "mix");
    await expect(page.locator(".layout-mix .layout__sidebar--left")).toHaveAttribute(
      "aria-hidden",
      "true"
    );
    const mixToggle = page
      .locator(".layout-mix .layout__header")
      .getByRole("button", { name: "展开导航" });
    await mixToggle.click();
    await expect(page.locator(".layout-mix .layout__sidebar--left")).toBeVisible();
    await expect(page.locator(".layout-mix .layout__overlay")).toBeVisible();

    await page.locator(".layout-mix .layout__overlay").click();
    await switchLayout(page, "left");
    await expect(page.locator(".layout-left .layout__sidebar")).toHaveAttribute(
      "aria-hidden",
      "true"
    );
    await page.locator(".layout-left .navbar").getByRole("button", { name: "展开导航" }).click();
    await expect(page.locator(".layout-left .layout__sidebar")).not.toHaveAttribute("aria-hidden");
    await expect(page.locator(".layout-left .layout__overlay")).toBeVisible();
  });
});
