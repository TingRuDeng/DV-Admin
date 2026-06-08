import { expect, test, type Page, type Route } from "@playwright/test";

interface UserRow {
  id: string;
  username: string;
  name: string;
  deptName: string;
  mobile: string;
  email: string;
  isActive: number;
  roleNames: string;
}

interface MockState {
  users: UserRow[];
  createPayloads: unknown[];
}

interface AuthMockOptions {
  username?: string;
  name?: string;
  roles?: string[];
  perms?: string[];
}

interface MockRouteContext {
  route: Route;
  method: string;
  path: string;
  readBody: () => unknown;
  state: MockState;
  auth: AuthMockOptions;
}

const API_PREFIX = "/dev-api";
const USERS_PATH = "/api/v1/system/users/";
const DEFAULT_USER_PERMS = [
  "system:users:query",
  "system:users:add",
  "system:users:edit",
  "system:users:delete",
];
const USER_FORM = {
  username: "e2e_user",
  name: "E2E 用户",
  mobile: "13800139000",
  email: "e2e_user@example.com",
};

function createMockState(): MockState {
  return {
    users: [
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
    createPayloads: [],
  };
}

async function fulfillJson(route: Route, data: unknown, status = 200) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(data),
  });
}

function success(data: unknown) {
  return { code: 20000, message: "成功", data };
}

async function installUserManagementMocks(
  page: Page,
  state: MockState,
  auth: AuthMockOptions = {}
) {
  await page.route(`**${API_PREFIX}/api/v1/**`, async (route) => {
    const request = route.request();
    const context = {
      route,
      method: request.method(),
      path: new URL(request.url()).pathname.replace(API_PREFIX, ""),
      readBody: request.postDataJSON.bind(request),
      state,
      auth,
    };

    if (await handleAuthRequest(context)) return;
    if (await handleSystemRequest(context)) return;

    await fulfillJson(
      route,
      { code: 404, message: `未 mock 的接口: ${context.method} ${context.path}`, data: null },
      404
    );
  });
}

async function handleAuthRequest(context: MockRouteContext) {
  if (context.method === "POST" && context.path === "/api/v1/oauth/login/") {
    await fulfillJson(
      context.route,
      success({
        accessToken: "test-access-token",
        refreshToken: "test-refresh-token",
        tokenType: "bearer",
        expiresIn: 3600,
      })
    );
    return true;
  }

  if (context.method === "GET" && context.path === "/api/v1/oauth/info/") {
    await fulfillJson(context.route, success(createAuthInfo(context.auth)));
    return true;
  }

  if (context.method === "GET" && context.path === "/api/v1/oauth/menus/routes/") {
    await fulfillJson(context.route, success(buildRoutes()));
    return true;
  }

  return false;
}

function createAuthInfo(auth: AuthMockOptions) {
  return {
    id: "1",
    username: auth.username ?? "admin",
    name: auth.name ?? "管理员",
    roles: auth.roles ?? ["admin"],
    perms: auth.perms ?? DEFAULT_USER_PERMS,
  };
}

async function handleSystemRequest(context: MockRouteContext) {
  if (context.method === "GET" && context.path === "/api/v1/system/departments/") {
    await fulfillJson(
      context.route,
      success([{ id: 1, label: "研发部", name: "研发部", children: [] }])
    );
    return true;
  }

  if (context.method === "GET" && context.path === "/api/v1/system/roles/options/") {
    await fulfillJson(context.route, success([{ id: 1, label: "管理员", value: 1 }]));
    return true;
  }

  if (context.method === "GET" && context.path === USERS_PATH) {
    await fulfillJson(
      context.route,
      success({ list: context.state.users, total: context.state.users.length })
    );
    return true;
  }

  if (context.method === "POST" && context.path === USERS_PATH) {
    context.state.createPayloads.push(context.readBody());
    context.state.users.push({
      id: "102",
      username: USER_FORM.username,
      name: USER_FORM.name,
      deptName: "研发部",
      mobile: USER_FORM.mobile,
      email: USER_FORM.email,
      isActive: 1,
      roleNames: "管理员",
    });
    await fulfillJson(context.route, success({ id: "102" }), 201);
    return true;
  }

  return false;
}

function buildRoutes() {
  return [
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
          meta: { title: "用户管理", perms: ["system:users:query"] },
        },
      ],
    },
  ];
}

test.describe("用户管理核心业务 smoke", () => {
  test("登录后可以进入用户管理并新增用户", async ({ page }) => {
    const state = createMockState();
    await installUserManagementMocks(page, state);

    await page.goto("/login?redirect=%2Fsystem%2Fusers");
    await page.getByLabel("用户名").fill("admin");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/system\/users/);
    await expect(page.getByText("用户数据")).toBeVisible();
    await expect(page.getByText("admin_mock")).toBeVisible();

    await page.getByRole("button", { name: "新增用户" }).click();
    const drawer = page.locator(".el-drawer").filter({ hasText: "新增用户" });

    await drawer.getByPlaceholder("请输入用户名").fill(USER_FORM.username);
    await drawer.getByPlaceholder("请输入用户昵称").fill(USER_FORM.name);
    await drawer
      .locator(".el-form-item", { hasText: "所属部门" })
      .locator(".el-select__wrapper")
      .click();
    await page.getByRole("option", { name: "研发部" }).click();
    await expect(drawer.getByText("研发部")).toBeVisible();
    await drawer
      .locator(".el-form-item", { hasText: "角色" })
      .locator(".el-select__wrapper")
      .click();
    await page.getByRole("option", { name: "管理员" }).click();
    await page.keyboard.press("Escape");
    await expect(drawer.getByText("管理员")).toBeVisible();
    await drawer.getByPlaceholder("请输入手机号码").fill(USER_FORM.mobile);
    await drawer.getByPlaceholder("请输入邮箱").fill(USER_FORM.email);
    await drawer.getByRole("button", { name: /确\s*定/ }).click();

    await expect.poll(() => state.createPayloads.length).toBe(1);
    await expect(page.getByText(USER_FORM.username, { exact: true })).toBeVisible();
  });

  test("只有查询权限时隐藏用户写操作", async ({ page }) => {
    const state = createMockState();
    await installUserManagementMocks(page, state, { perms: ["system:users:query"] });

    await page.goto("/login?redirect=%2Fsystem%2Fusers");
    await page.getByLabel("用户名").fill("viewer");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/system\/users/);
    await expect(page.getByText("用户数据")).toBeVisible();
    await expect(page.getByText("admin_mock")).toBeVisible();
    await expect(page.getByRole("button", { name: "新增用户" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "批量删除" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "编辑" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "删除" })).toHaveCount(0);
    expect(state.createPayloads).toHaveLength(0);
  });
});
