import { expect, test, type Locator, type Page, type Route } from "@playwright/test";
import { expectReadableAction } from "./helpers/visual-assertions";

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
          avatar: "",
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
                path: "icons",
                component: "demo/icon-select",
                name: "IconSelectDemo",
                meta: { title: "图标选择", hidden: true },
              },
              {
                path: "uploads",
                component: "demo/upload",
                name: "UploadDemo",
                meta: { title: "上传", hidden: true },
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

    if (method === "GET" && path === "/api/v1/system/roles/") {
      await fulfillJson(route, success({ list: [], total: 0 }));
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
  test("图片预览按钮在键盘聚焦后可见并可操作", async ({ page }) => {
    await installShellMocks(page);
    await page.route("https://s2.loli.net/**", (route) =>
      route.fulfill({
        contentType: "image/png",
        body: Buffer.from(
          "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a/R8AAAAASUVORK5CYII=",
          "base64"
        ),
      })
    );
    await login(page);
    await page.goto("/system/uploads");
    const preview = page.getByRole("button", { name: "预览图片", exact: true });
    await preview.focus();
    await expect(preview.locator("..")).toHaveCSS("opacity", "1");
    await preview.press("Enter");
    await expect(page.locator(".el-image-viewer__wrapper")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator(".el-image-viewer__wrapper")).not.toBeVisible();
  });

  test("通知请求失败后可重试，不误显示为空通知", async ({ page }) => {
    await installShellMocks(page);
    let attempts = 0;
    await page.route("**/api/v1/system/notices/my-page/**", async (route) => {
      attempts += 1;
      await fulfillJson(
        route,
        attempts === 1
          ? { code: 50000, message: "暂时无法加载通知", data: null }
          : success({ list: [], total: 0 }),
        attempts === 1 ? 503 : 200
      );
    });
    await login(page);
    await page.getByRole("button", { name: "通知消息", exact: true }).click();
    const notifications = page.locator(".notification-list");
    await expect(notifications.getByRole("alert")).toBeVisible();
    await expect(notifications.locator(".el-empty")).toHaveCount(0);
    await notifications.getByRole("button", { name: "重试", exact: true }).click();
    await expect(notifications.getByRole("alert")).toHaveCount(0);
    await expect(notifications.locator(".el-empty")).toBeVisible();
    expect(attempts).toBe(2);
  });

  test("只读用户不显示操作列，手机部门筛选可展开并清除", async ({ page }) => {
    await installShellMocks(page);
    await page.setViewportSize({ width: 390, height: 844 });
    await login(page);
    await expect(page.getByRole("columnheader", { name: "操作", exact: true })).toHaveCount(0);
    await expect(page.locator(".ff-table .el-checkbox")).toHaveCount(0);
    const filter = page.locator(".ff-user-page__dept-toggle");
    await expect(filter).toHaveAttribute("aria-expanded", "false");
    await filter.click();
    await page.getByRole("treeitem", { name: "研发部" }).click();
    await expect(filter).toHaveText("研发部");
    await expect(filter).toHaveAttribute("aria-expanded", "false");
    await page.getByRole("button", { name: "重置", exact: true }).click();
    await expect(filter).toHaveText("部门");
  });

  test("菜单搜索支持空状态、键盘选择和搜索历史", async ({ page }) => {
    await installShellMocks(page);
    await login(page);
    const trigger = page.getByRole("button", { name: "搜索菜单", exact: true });
    await trigger.click();
    const dialog = page.getByRole("dialog", { name: "搜索菜单", exact: true });
    const input = dialog.getByRole("textbox", { name: "搜索菜单", exact: true });
    await expect(input).toBeFocused();
    await input.fill("no-such-menu");
    await expect(dialog.getByRole("status")).toHaveText("未找到匹配的菜单");
    await input.fill("角色管理");
    await input.press("Enter");
    await expect(page).toHaveURL(/\/system\/roles/);
    await trigger.click();
    await expect(dialog.getByText("搜索历史")).toBeVisible();
    await expect(dialog.getByRole("button", { name: "角色管理", exact: true })).toBeVisible();
    await input.press("Escape");
    await expect(dialog).not.toBeVisible();
    await expect(trigger).toBeFocused();
  });

  test("图标选择可搜索、清除并保持键盘焦点", async ({ page }) => {
    await installShellMocks(page);
    await login(page);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/system/icons");
    const trigger = page.getByRole("button", { name: "选择图标", exact: true });
    await trigger.click();
    const input = page.getByRole("textbox", { name: "搜索图标", exact: true });
    await expect(input).toBeFocused();
    await input.fill("no-such-icon");
    await expect(page.getByRole("status")).toHaveText("未找到匹配的图标");
    await input.fill("search");
    await page.getByRole("button", { name: "search", exact: true }).click();
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await expect(trigger).toBeFocused();
    const clear = page.getByRole("button", { name: "清除图标", exact: true });
    await clear.focus();
    await page.keyboard.press("Space");
    await expect(clear).not.toBeVisible();
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await expect(trigger).toBeFocused();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true
    );
  });

  test("首页与用户页的桌面和手机视觉验收", async ({ page }, testInfo) => {
    await installShellMocks(page);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await setPreferences(page, { "vea:ui:theme": "dark", "vea:ui:layout": "left" });
    await login(page);
    for (const theme of ["dark", "light"]) {
      await page.evaluate((value) => localStorage.setItem("vea:ui:theme", value), theme);
      for (const width of [1440, 390]) {
        await page.setViewportSize({ width, height: width > 600 ? 1000 : 844 });
        await page.goto("/system/users");
        await expect(page.getByText("用户数据")).toBeVisible();
        await expectReadableAction(page.getByRole("button", { name: "搜索", exact: true }));
        await expect(page.locator(".user-profile__avatar.lucide")).toBeVisible();
        await page.mouse.move(0, 0);
        const users = testInfo.outputPath(`users-${theme}-${width}.png`);
        await page.screenshot({ path: users, fullPage: true, animations: "disabled" });
        await testInfo.attach("Users", { path: users, contentType: "image/png" });
        await page.goto("/dashboard");
        await expect(page.locator(".dashboard-hero")).toBeVisible();
        await expect(page.locator(".dashboard-metric")).toHaveCount(3);
        await expect(page.locator(".dashboard-hero__beam").first()).toHaveCSS(
          "animation-name",
          "none"
        );
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
          true
        );
        if (width === 390) {
          await expect(
            page.getByRole("button", { name: "用户管理", exact: true }).last()
          ).toBeInViewport();
        }
        const dashboard = testInfo.outputPath(`dashboard-${theme}-${width}.png`);
        await page.screenshot({ path: dashboard, fullPage: true, animations: "disabled" });
        await testInfo.attach("Dashboard", { path: dashboard, contentType: "image/png" });
      }
    }
  });

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
    await expect(page.locator(".dashboard-page")).toBeVisible();
    await expect(page.locator("#dashboard-title")).toBeVisible();
    await expect(page.locator(".dashboard-metrics")).toBeVisible();
    await expect(page.locator(".dashboard-actions")).toBeVisible();
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
    await expect(sidebarToggle).toHaveAttribute("aria-label", "收起导航");
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
