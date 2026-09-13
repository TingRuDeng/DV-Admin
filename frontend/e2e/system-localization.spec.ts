import { expect, test, type Page } from "@playwright/test";

const forms = [
  {
    path: "dept",
    component: "system/dept/index",
    name: "Dept",
    add: "新增部门",
    addEn: "Add department",
    error: "Enter a department name",
    input: "Enter department name",
  },
  {
    path: "dict",
    component: "system/dict/index",
    name: "Dict",
    add: "新增字典",
    addEn: "Add dictionary",
    error: "Enter dictionary name",
    input: "Enter dictionary name",
  },
  {
    path: "dict-item",
    component: "system/dict/dict-item",
    name: "DictItem",
    add: "新增字典项",
    addEn: "Add dictionary item",
    error: "Enter item label",
    input: "Enter item label",
  },
  {
    path: "role",
    component: "system/role/index",
    name: "Role",
    add: "新增角色",
    addEn: "Add role",
    error: "Enter a role name",
    input: "Enter a role name",
  },
  {
    path: "menu",
    component: "system/menu/index",
    name: "SysMenu",
    add: "新增菜单",
    addEn: "Add menu",
    error: "Enter a menu name",
    input: "Enter a menu name",
  },
  {
    path: "notice",
    component: "system/notice/index",
    name: "Notice",
    add: "新增通知",
    addEn: "Add announcement",
    error: "Enter an announcement title",
    input: "Title",
  },
];

async function installMocks(page: Page) {
  await page.route("**/dev-api/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname.replace("/dev-api/api/v1", "");
    let data: unknown;
    if (path === "/oauth/login/") {
      data = {
        accessToken: "test-token",
        refreshToken: "test-refresh",
        tokenType: "bearer",
        expiresIn: 3600,
      };
    } else if (path === "/oauth/info/") {
      data = { id: "1", username: "admin", name: "Admin", roles: ["ROOT"], perms: ["*:*:*"] };
    } else if (path === "/oauth/menus/routes/") {
      data = [
        {
          path: "/system",
          component: "Layout",
          name: "System",
          meta: { title: "System", icon: "system" },
          children: forms.map((form) => ({
            path: form.path,
            component: form.component,
            name: form.name,
            meta: { title: form.addEn },
          })),
        },
      ];
    } else if (route.request().method() === "GET" && path === "/system/menus/") {
      data = [];
    } else if (
      route.request().method() === "GET" &&
      (path.endsWith("/options/") ||
        path === "/system/departments/" ||
        path === "/system/permissions/")
    ) {
      data = [];
    } else if (
      route.request().method() === "GET" &&
      [
        "/system/dicts/",
        "/system/dict-items/",
        "/system/roles/",
        "/system/notices/",
        "/system/notices/page",
        "/system/notices/my-page/",
      ].includes(path)
    ) {
      data = { list: [], total: 0 };
    } else {
      await route.fulfill({
        status: 400,
        json: {
          code: 400,
          message: `Unexpected request: ${route.request().method()} ${path}`,
          data: null,
        },
      });
      return;
    }
    await route.fulfill({ json: { code: 20000, message: "OK", data } });
  });
}

for (const form of forms) {
  test(`${form.name}: cached form validates in the selected language on desktop and mobile`, async ({
    page,
  }, testInfo) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.setViewportSize({ width: 1440, height: 960 });
    await installMocks(page);
    await page.goto(`/login?redirect=${encodeURIComponent(`/system/${form.path}`)}`);
    await page.getByLabel("用户名").fill("admin");
    await page.getByLabel("密码").fill("test-password");
    await page.getByRole("button", { name: /登\s*录/ }).click();
    await expect(page).toHaveURL(new RegExp(`/system/${form.path}$`));

    await page.getByRole("button", { name: form.add, exact: true }).click();
    const drawer = page.getByRole("dialog");
    await expect(drawer).toBeVisible();
    await drawer.getByRole("button", { name: "取消", exact: true }).click();
    await expect(drawer).not.toBeVisible();
    await page.getByRole("button", { name: "切换语言" }).click();
    await page.getByRole("menuitem", { name: "English" }).click();
    await page.getByRole("button", { name: form.addEn, exact: true }).click();
    await expect(drawer).toBeVisible();
    await expect(drawer.locator(".el-form-item__error")).toHaveCount(0);
    await drawer.getByRole("button", { name: "Confirm", exact: true }).click();
    await expect(drawer.getByText(form.error, { exact: true })).toBeVisible();
    if (form.name === "Notice") {
      await expect(drawer.getByText("Enter announcement content", { exact: true })).toBeVisible();
      await expect(drawer.getByText("请选择", { exact: true })).toHaveCount(0);
    }
    await drawer.getByPlaceholder(form.input, { exact: true }).fill("Draft value");
    await drawer.getByPlaceholder(form.input, { exact: true }).blur();
    await expect(drawer.getByText(form.error, { exact: true })).not.toBeVisible();
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 960 });
      await expect(drawer.getByPlaceholder(form.input, { exact: true })).toHaveValue("Draft value");
      await expect
        .poll(() => drawer.evaluate((element) => element.scrollWidth - element.clientWidth))
        .toBeLessThanOrEqual(1);
      await page.screenshot({
        path: testInfo.outputPath(`${form.path}-en-${width}.png`),
        fullPage: true,
      });
    }
    expect(errors).toEqual([]);
  });
}
