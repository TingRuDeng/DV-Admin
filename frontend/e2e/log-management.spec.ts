import { expect, test, type Page, type Route } from "@playwright/test";

interface LogRow {
  id: number;
  userId: number;
  createdAt: string;
  updatedAt: string;
  username: string;
  name: string;
  operation: string;
  queryParams: string;
  method: string;
  requestBody: string;
  path: string;
  responseStatus: number;
  responseBody: string;
  ip: string;
  browser: string;
  os: string;
  executionTime: number;
  status: number;
  errorMsg: string;
}

interface MockState {
  logs: LogRow[];
  seenPaths: string[];
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
  state: MockState;
  auth: AuthMockOptions;
}

const API_PREFIX = "/dev-api";
const LOGS_PAGE_PATH = "/api/v1/system/logs/page";
const MY_NOTICES_PATH = "/api/v1/system/notices/my-page/";
const DEFAULT_LOG_PERMS = ["system:logs:query"];

function createMockState(): MockState {
  return {
    logs: [
      {
        id: 901,
        userId: 1,
        createdAt: "2026-06-09 10:00:00",
        updatedAt: "2026-06-09 10:00:01",
        username: "admin",
        name: "管理员",
        operation: "删除用户失败",
        queryParams: "",
        method: "DELETE",
        requestBody: '{"ids":[99]}',
        path: "/api/v1/system/users/99",
        responseStatus: 500,
        responseBody: '{"message":"用户删除失败"}',
        ip: "127.0.0.1",
        browser: "Chromium",
        os: "macOS",
        executionTime: 12,
        status: 0,
        errorMsg: "用户删除失败",
      },
    ],
    seenPaths: [],
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

async function installLogManagementMocks(page: Page, state: MockState, auth: AuthMockOptions = {}) {
  await page.route(`**${API_PREFIX}/api/v1/**`, async (route) => {
    const request = route.request();
    const context = {
      route,
      method: request.method(),
      path: new URL(request.url()).pathname.replace(API_PREFIX, ""),
      state,
      auth,
    };
    state.seenPaths.push(context.path);

    if (await handleAuthRequest(context)) return;
    if (await handleMyNoticeRequest(context)) return;
    if (await handleLogRequest(context)) return;

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
    perms: auth.perms ?? DEFAULT_LOG_PERMS,
  };
}

async function handleMyNoticeRequest(context: MockRouteContext) {
  if (context.method !== "GET" || context.path !== MY_NOTICES_PATH) return false;

  await fulfillJson(context.route, success({ list: [], total: 0 }));
  return true;
}

async function handleLogRequest(context: MockRouteContext) {
  if (context.method !== "GET") return false;

  if (context.path === LOGS_PAGE_PATH) {
    await fulfillJson(
      context.route,
      success({ list: context.state.logs, total: context.state.logs.length })
    );
    return true;
  }

  const detailMatch = context.path.match(/^\/api\/v1\/system\/logs\/(\d+)$/);
  if (!detailMatch) return false;
  const log = context.state.logs.find((item) => item.id === Number(detailMatch[1]));
  if (!log) {
    await fulfillJson(context.route, { code: 40400, message: "操作日志不存在", data: null }, 404);
    return true;
  }

  await fulfillJson(context.route, success(log));
  return true;
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
          path: "logs",
          component: "system/log/index",
          name: "LogManagement",
          meta: { title: "日志管理", perms: ["system:logs:query"] },
        },
      ],
    },
  ];
}

test.describe("日志管理链路 smoke", () => {
  test("日志管理页应请求系统模块下的分页接口", async ({ page }) => {
    const state = createMockState();
    await installLogManagementMocks(page, state);

    await page.goto("/login?redirect=%2Fsystem%2Flogs");
    await page.getByLabel("用户名").fill("admin");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/system\/logs/);
    await expect.poll(() => state.seenPaths.join("|")).toContain(LOGS_PAGE_PATH);
    await expect(page.locator("tbody").getByText("删除用户失败")).toBeVisible();
    await expect(page.locator("tbody").getByText("失败", { exact: true })).toBeVisible();

    await page.getByRole("button", { name: "查看" }).click();

    await expect(page.getByText("操作日志详情")).toBeVisible();
    await expect(page.locator(".el-alert__description")).toHaveText("用户删除失败");
    await expect(page.getByText("DELETE /api/v1/system/users/99")).toBeVisible();
    await expect.poll(() => state.seenPaths.join("|")).toContain("/api/v1/system/logs/901");
  });
});
