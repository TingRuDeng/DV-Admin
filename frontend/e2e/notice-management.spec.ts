import { expect, test, type Page, type Route } from "@playwright/test";

interface NoticeRow {
  id: string;
  title: string;
  type: number;
  level: string;
  targetType: number;
  publishStatus: number;
  publisherName: string;
  createTime: string;
  publishTime?: string;
}

interface DictItemOption {
  value: string | number;
  label: string;
  tagType?: string;
}

interface MockState {
  notices: NoticeRow[];
  dictItemsByCode: Record<string, DictItemOption[]>;
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
  query: URLSearchParams;
  readBody: () => unknown;
  state: MockState;
  auth: AuthMockOptions;
}

const API_PREFIX = "/dev-api";
const NOTICES_PATH = "/api/v1/system/notices";
const DICT_ITEMS_PATH = "/api/v1/system/dict-items/";
const DEFAULT_NOTICE_PERMS = [
  "system:notices:query",
  "system:notices:add",
  "system:notices:edit",
  "system:notices:delete",
  "system:notices:publish",
  "system:notices:revoke",
];

function createMockState(): MockState {
  return {
    notices: [
      {
        id: "801",
        title: "系统维护计划",
        type: 2,
        level: "M",
        targetType: 1,
        publishStatus: 0,
        publisherName: "管理员",
        createTime: "2026-06-09 09:00",
      },
      {
        id: "802",
        title: "安全提醒",
        type: 3,
        level: "H",
        targetType: 1,
        publishStatus: 1,
        publisherName: "管理员",
        createTime: "2026-06-09 09:10",
        publishTime: "2026-06-09 09:15",
      },
    ],
    dictItemsByCode: {
      notice_type: [
        { value: 2, label: "系统维护", tagType: "warning" },
        { value: 3, label: "安全警告", tagType: "danger" },
      ],
      notice_level: [
        { value: "M", label: "中", tagType: "warning" },
        { value: "H", label: "高", tagType: "danger" },
      ],
    },
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

async function installNoticeManagementMocks(
  page: Page,
  state: MockState,
  auth: AuthMockOptions = {}
) {
  await page.route(`**${API_PREFIX}/api/v1/**`, async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const context = {
      route,
      method: request.method(),
      path: url.pathname.replace(API_PREFIX, ""),
      query: url.searchParams,
      readBody: request.postDataJSON.bind(request),
      state,
      auth,
    };

    if (await handleAuthRequest(context)) return;
    if (await handleNoticeRequest(context)) return;
    if (await handleDictRequest(context)) return;

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
    perms: auth.perms ?? DEFAULT_NOTICE_PERMS,
  };
}

async function handleNoticeRequest(context: MockRouteContext) {
  if (context.method === "GET" && context.path === `${NOTICES_PATH}/page`) {
    await fulfillJson(
      context.route,
      success({ list: context.state.notices, total: context.state.notices.length })
    );
    return true;
  }

  if (context.path.startsWith(NOTICES_PATH) && context.method !== "GET") {
    context.state.writePayloads.push(context.readBody());
    await fulfillJson(context.route, success(null));
    return true;
  }

  return false;
}

async function handleDictRequest(context: MockRouteContext) {
  if (context.method !== "GET" || context.path !== DICT_ITEMS_PATH) return false;
  const dictCode = context.query.get("dict__dict_code") ?? "";

  await fulfillJson(context.route, success(context.state.dictItemsByCode[dictCode] ?? []));
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
          path: "notices",
          component: "system/notice/index",
          name: "NoticeManagement",
          meta: { title: "通知公告", perms: ["system:notices:query"] },
        },
      ],
    },
  ];
}

test.describe("通知公告权限链路 smoke", () => {
  test("后端通知权限码应显示通知写操作", async ({ page }) => {
    const state = createMockState();
    await installNoticeManagementMocks(page, state);

    await page.goto("/login?redirect=%2Fsystem%2Fnotices");
    await page.getByLabel("用户名").fill("admin");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/system\/notices/);
    await expect(page.locator("tbody").getByText("系统维护计划")).toBeVisible();
    await expect(page.getByRole("button", { name: "新增通知" })).toBeVisible();
    await expect(page.getByRole("button", { name: "批量删除" })).toBeVisible();
    await expect(page.getByRole("button", { name: "发布" })).toBeVisible();
    await expect(page.getByRole("button", { name: "撤回" })).toBeVisible();
    await expect(page.getByRole("button", { name: "编辑" })).toBeVisible();
    await expect(page.getByRole("button", { name: "删除", exact: true })).toBeVisible();
    expect(state.writePayloads).toHaveLength(0);
  });
});
