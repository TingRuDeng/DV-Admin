import { expect, test, type Locator, type Page, type Route } from "@playwright/test";

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
              {
                path: "roles",
                component: "system/role/index",
                name: "Role",
                meta: {
                  title: "角色管理",
                  icon: "role",
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

async function focusWithKeyboard(page: Page, target: Locator) {
  await page.evaluate(() => {
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
  });

  for (let index = 0; index < 30; index += 1) {
    await page.keyboard.press("Tab");
    if (await target.evaluate((element) => document.activeElement === element)) {
      return;
    }
  }

  throw new Error("无法通过键盘 Tab 顺序聚焦目标元素");
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
    await expect(userTag).toHaveCSS("height", "30px");
    await expect(userTag).toHaveCSS("border-style", "solid");
    await expect(tags).toHaveCSS("border-bottom-style", "solid");
    expect(await tags.evaluate((element) => getComputedStyle(element).backgroundColor)).not.toBe(
      "rgba(0, 0, 0, 0)"
    );
    await focusWithKeyboard(page, userTag);
    await expect(userTag).toBeFocused();
    await expect(userTag).toHaveCSS("outline-style", "solid");

    for (const accessibleName of [
      "搜索菜单",
      "进入全屏",
      "布局大小",
      "切换语言",
      "通知消息",
      "用户菜单",
      "系统设置",
    ]) {
      await expect(page.getByRole("button", { name: accessibleName })).toBeVisible();
    }

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
    await page.locator(".layout-top .el-sub-menu__title", { hasText: "系统管理" }).hover();
    const topMenuPopup = page.locator(".el-menu--popup:visible");
    await expect(topMenuPopup).toBeVisible();
    await expect(topMenuPopup).toHaveCSS("min-width", "160px");
    expect(
      await topMenuPopup.evaluate((element) => getComputedStyle(element).backgroundColor)
    ).not.toBe("rgba(0, 0, 0, 0)");

    await switchLayout(page, "mix");
    await expect(page.locator(".layout-mix .layout__sidebar--left")).toBeVisible();

    await page.evaluate(() => localStorage.setItem("vea:ui:theme", "dark"));
    await page.reload();
    await expect(page.locator("html")).toHaveClass(/dark/);
    await expect(page.locator("main.app-main")).toBeVisible();
    const sidebarTitle = page.locator(".layout-mix .sidebar-title");
    await expect(sidebarTitle).toBeVisible();
    expect(
      await sidebarTitle.evaluate((element) => getComputedStyle(element).webkitTextFillColor)
    ).not.toBe("rgba(0, 0, 0, 0)");
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
    const mixSidebar = page.locator(".layout-mix .layout__sidebar--left");
    const mixOverlay = page.locator(".layout-mix .layout__overlay");

    await expect(mixSidebar).toHaveAttribute("aria-hidden", "true");
    await expect(mixSidebar).toHaveCSS("position", "fixed");
    await expect.poll(async () => (await mixSidebar.boundingBox())?.x ?? 0).toBeLessThan(0);

    const mixToggle = page.locator(".layout-mix .layout__header .hamburger-wrapper");
    await expect(mixToggle).toHaveAttribute("aria-label", "展开导航");
    await mixToggle.click();
    await expect(mixToggle).toHaveAttribute("aria-controls", "layout-sidebar");
    await expect(mixSidebar).toHaveAttribute("id", "layout-sidebar");
    await expect(mixSidebar).toBeVisible();
    await expect(mixSidebar).not.toHaveAttribute("aria-hidden");
    await expect(mixSidebar).toHaveCSS("position", "fixed");
    await expect(mixSidebar).toHaveCSS("z-index", "1000");
    await expect.poll(async () => page.evaluate(() => document.body.style.overflow)).toBe("hidden");
    await expect
      .poll(async () => (await mixSidebar.boundingBox())?.x ?? -1)
      .toBeGreaterThanOrEqual(0);
    const sidebarToggle = mixSidebar.locator(".layout__sidebar-toggle button");
    await expect(sidebarToggle).toHaveAttribute("aria-label", "收起侧边导航");
    await expect
      .poll(async () =>
        page.evaluate(() => document.activeElement?.closest("#layout-sidebar") !== null)
      )
      .toBe(true);
    await page.keyboard.press("Shift+Tab");
    await expect
      .poll(async () =>
        page.evaluate(() => document.activeElement?.closest("#layout-sidebar") !== null)
      )
      .toBe(true);
    await page.keyboard.press("Tab");
    await expect
      .poll(async () =>
        page.evaluate(() => document.activeElement?.closest("#layout-sidebar") !== null)
      )
      .toBe(true);

    await page.keyboard.press("Escape");
    await expect(mixSidebar).toHaveAttribute("aria-hidden", "true");
    await expect(mixToggle).toBeFocused();
    await expect
      .poll(async () => page.evaluate(() => document.body.style.overflow))
      .not.toBe("hidden");

    await mixToggle.click();
    await sidebarToggle.click();
    await expect(mixSidebar).toHaveAttribute("aria-hidden", "true");
    await expect.poll(async () => (await mixSidebar.boundingBox())?.x ?? 0).toBeLessThan(0);

    await mixToggle.click();
    await expect(mixOverlay).toBeVisible();
    await mixOverlay.click();
    await expect(mixSidebar).toHaveAttribute("aria-hidden", "true");
    await expect.poll(async () => (await mixSidebar.boundingBox())?.x ?? 0).toBeLessThan(0);

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
