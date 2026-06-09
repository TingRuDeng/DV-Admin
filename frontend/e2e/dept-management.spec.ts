import { expect, test, type Page, type Route } from "@playwright/test";

interface DeptRow {
  id: string;
  name: string;
  sort: number;
  status: number;
  children?: DeptRow[];
}

interface MockState {
  depts: DeptRow[];
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
const DEPTS_PATH = "/api/v1/system/departments/";
const HTTP_OK = 200;
const DEFAULT_DEPT_PERMS = [
  "system:departments:query",
  "system:departments:add",
  "system:departments:edit",
  "system:departments:delete",
];

function createMockState(): MockState {
  return {
    depts: [
      {
        id: "401",
        name: "研发部",
        sort: 1,
        status: 1,
        children: [
          {
            id: "402",
            name: "前端组",
            sort: 2,
            status: 1,
          },
        ],
      },
    ],
    writePayloads: [],
  };
}

async function fulfillJson(route: Route, data: unknown, status = HTTP_OK) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(data),
  });
}

function success(data: unknown) {
  return { code: 20000, message: "成功", data };
}

async function installDeptManagementMocks(
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
    if (await handleDeptRequest(context)) return;

    await fulfillJson(
      route,
      { code: 404, message: `未 mock 的接口: ${context.method} ${context.path}`, data: null },
      404
    );
  });
}

async function waitForDepartmentLoginBootstrap(page: Page, clickLogin: () => Promise<void>) {
  // 登录后的目标路由依赖用户信息和动态路由；显式等待可避免只观察 URL 的竞态。
  const loginResponse = page.waitForResponse(
    (response) =>
      response.url().includes(`${API_PREFIX}/api/v1/oauth/login/`) &&
      response.request().method() === "POST" &&
      response.status() === HTTP_OK
  );
  const userInfoResponse = page.waitForResponse(
    (response) =>
      response.url().includes(`${API_PREFIX}/api/v1/oauth/info/`) &&
      response.request().method() === "GET" &&
      response.status() === HTTP_OK
  );
  const routeResponse = page.waitForResponse(
    (response) =>
      response.url().includes(`${API_PREFIX}/api/v1/oauth/menus/routes/`) &&
      response.request().method() === "GET" &&
      response.status() === HTTP_OK
  );

  await Promise.all([loginResponse, userInfoResponse, routeResponse, clickLogin()]);
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
    perms: auth.perms ?? DEFAULT_DEPT_PERMS,
  };
}

async function handleDeptRequest(context: MockRouteContext) {
  if (context.method === "GET" && context.path === DEPTS_PATH) {
    await fulfillJson(context.route, success(context.state.depts));
    return true;
  }

  if (context.path.startsWith(DEPTS_PATH) && context.method !== "GET") {
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
          path: "departments",
          component: "system/dept/index",
          name: "Dept",
          meta: { title: "部门管理", perms: ["system:departments:query"] },
        },
      ],
    },
  ];
}

test.describe("部门管理权限链路 smoke", () => {
  test("只有查询权限时隐藏部门写操作", async ({ page }) => {
    const state = createMockState();
    await installDeptManagementMocks(page, state, { perms: ["system:departments:query"] });

    await page.goto("/login?redirect=%2Fsystem%2Fdepartments");
    await page.getByLabel("用户名").fill("viewer");
    await page.getByLabel("密码").fill("123456");
    await waitForDepartmentLoginBootstrap(page, () =>
      page.getByRole("button", { name: /登\s*录|Login/i }).click()
    );

    await expect(page).toHaveURL(/\/system\/departments/);
    await expect(page.getByText("部门数据")).toBeVisible();
    await expect(page.locator("tbody").getByText("研发部")).toBeVisible();
    await expect(page.getByRole("button", { name: "新增部门" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "批量删除" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "新增" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "编辑" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "删除" })).toHaveCount(0);
    expect(state.writePayloads).toHaveLength(0);
  });
});
