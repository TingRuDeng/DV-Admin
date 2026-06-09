import { expect, test, type Page, type Route } from "@playwright/test";

interface RoleRow {
  id: string;
  name: string;
  sort: number;
  status: number;
  isDefault: boolean;
  desc: string;
}

interface MockState {
  roles: RoleRow[];
  writePayloads: unknown[];
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
const ROLES_PATH = "/api/v1/system/roles/";
const DEFAULT_ROLE_PERMS = [
  "system:roles:query",
  "system:roles:add",
  "system:roles:edit",
  "system:roles:delete",
];

function createMockState(): MockState {
  return {
    roles: [
      {
        id: "201",
        name: "测试角色",
        sort: 1,
        status: 1,
        isDefault: false,
        desc: "仅用于角色权限链路 E2E",
      },
    ],
    writePayloads: [],
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

async function installRoleManagementMocks(
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
    if (await handleRoleRequest(context)) return;

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
    perms: auth.perms ?? DEFAULT_ROLE_PERMS,
  };
}

async function handleRoleRequest(context: MockRouteContext) {
  if (context.method === "GET" && context.path === ROLES_PATH) {
    await fulfillJson(
      context.route,
      success({ list: context.state.roles, total: context.state.roles.length })
    );
    return true;
  }

  if (context.path.startsWith(ROLES_PATH) && context.method !== "GET") {
    context.state.writePayloads.push(context.readBody());
    await fulfillJson(context.route, success(null));
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
          path: "roles",
          component: "system/role/index",
          name: "Role",
          meta: { title: "角色管理", perms: ["system:roles:query"] },
        },
      ],
    },
  ];
}

test.describe("角色管理权限链路 smoke", () => {
  test("只有查询权限时隐藏角色写操作", async ({ page }) => {
    const state = createMockState();
    await installRoleManagementMocks(page, state, { perms: ["system:roles:query"] });

    await page.goto("/login?redirect=%2Fsystem%2Froles");
    await page.getByLabel("用户名").fill("viewer");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/system\/roles/);
    await expect(page.getByText("角色数据")).toBeVisible();
    await expect(page.getByText("测试角色")).toBeVisible();
    await expect(page.getByRole("button", { name: "新增角色" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "批量删除" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "分配权限" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "编辑" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "删除" })).toHaveCount(0);
    expect(state.writePayloads).toHaveLength(0);
  });
});
