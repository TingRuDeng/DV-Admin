import { expect, test, type Page, type Route } from "@playwright/test";

interface DictRow {
  id: string;
  name: string;
  dictCode: string;
  status: number;
}

interface DictItemRow {
  id: string;
  dictName: string;
  dictCode: string;
  label: string;
  value: string;
  status: number;
  tagType?: string;
}

interface MockState {
  dicts: DictRow[];
  dictItems: DictItemRow[];
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
const DICTS_PATH = "/api/v1/system/dicts/";
const DICT_ITEMS_PATH = "/api/v1/system/dict-items/";
const DEFAULT_DICT_ITEM_PERMS = [
  "system:dictitems:query",
  "system:dictitems:add",
  "system:dictitems:edit",
  "system:dictitems:delete",
];

function createMockState(): MockState {
  return {
    dicts: [
      {
        id: "501",
        name: "通知类型",
        dictCode: "notice_type",
        status: 1,
      },
    ],
    dictItems: [
      {
        id: "701",
        dictName: "通知类型",
        dictCode: "notice_type",
        label: "系统升级",
        value: "upgrade",
        status: 1,
        tagType: "success",
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

async function installDictItemManagementMocks(
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
    perms: auth.perms ?? DEFAULT_DICT_ITEM_PERMS,
  };
}

async function handleDictRequest(context: MockRouteContext) {
  if (context.method === "GET" && context.path === DICTS_PATH) {
    await fulfillJson(
      context.route,
      success({ list: context.state.dicts, total: context.state.dicts.length })
    );
    return true;
  }

  if (context.method === "GET" && context.path === DICT_ITEMS_PATH) {
    await fulfillJson(
      context.route,
      success({ list: context.state.dictItems, total: context.state.dictItems.length })
    );
    return true;
  }

  if (context.path.startsWith(DICT_ITEMS_PATH) && context.method !== "GET") {
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
          path: "dict-item",
          component: "system/dict/dict-item",
          name: "DictData",
          meta: { title: "字典项", perms: ["system:dictitems:query"] },
        },
      ],
    },
  ];
}

test.describe("字典项管理权限链路 smoke", () => {
  test("只有查询权限时隐藏字典项写操作", async ({ page }) => {
    const state = createMockState();
    await installDictItemManagementMocks(page, state, { perms: ["system:dictitems:query"] });

    await page.goto("/login?redirect=%2Fsystem%2Fdict-item");
    await page.getByLabel("用户名").fill("viewer");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/system\/dict-item/);
    await expect(page.getByText("字典项数据")).toBeVisible();
    await expect(page.locator("tbody").getByText("系统升级")).toBeVisible();
    await expect(page.getByRole("button", { name: "新增字典项" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "批量删除" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "编辑" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "删除" })).toHaveCount(0);
    expect(state.writePayloads).toHaveLength(0);
  });
});
