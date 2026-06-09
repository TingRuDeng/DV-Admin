import { expect, test, type Page, type Route } from "@playwright/test";

interface MenuRow {
  id: string;
  name: string;
  type: "CATALOG" | "MENU" | "BUTTON" | "EXTLINK";
  routeName?: string;
  routePath?: string;
  component?: string;
  perm?: string;
  visible: number;
  sort: number;
  children?: MenuRow[];
}

interface MockState {
  menus: MenuRow[];
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
const MENUS_PATH = "/api/v1/system/menus/";
const DEFAULT_MENU_PERMS = [
  "system:permissions:query",
  "system:permissions:add",
  "system:permissions:edit",
  "system:permissions:delete",
];

function createMockState(): MockState {
  return {
    menus: [
      {
        id: "301",
        name: "系统管理",
        type: "CATALOG",
        routeName: "System",
        routePath: "/system",
        component: "Layout",
        visible: 1,
        sort: 1,
        children: [
          {
            id: "302",
            name: "菜单管理",
            type: "MENU",
            routeName: "Menu",
            routePath: "menus",
            component: "system/menu/index",
            perm: "system:permissions:query",
            visible: 1,
            sort: 3,
          },
        ],
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

async function installMenuManagementMocks(
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
    if (await handleMenuRequest(context)) return;

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
    perms: auth.perms ?? DEFAULT_MENU_PERMS,
  };
}

async function handleMenuRequest(context: MockRouteContext) {
  if (context.method === "GET" && context.path === MENUS_PATH) {
    await fulfillJson(context.route, success(context.state.menus));
    return true;
  }

  if (context.path.startsWith(MENUS_PATH) && context.method !== "GET") {
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
          path: "menus",
          component: "system/menu/index",
          name: "Menu",
          meta: { title: "菜单管理", perms: ["system:permissions:query"] },
        },
      ],
    },
  ];
}

test.describe("菜单管理权限链路 smoke", () => {
  test("只有查询权限时隐藏菜单写操作", async ({ page }) => {
    const state = createMockState();
    await installMenuManagementMocks(page, state, { perms: ["system:permissions:query"] });

    await page.goto("/login?redirect=%2Fsystem%2Fmenus");
    await page.getByLabel("用户名").fill("viewer");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/system\/menus/);
    await expect(page.getByText("菜单数据")).toBeVisible();
    await expect(page.locator("tbody").getByText("系统管理")).toBeVisible();
    await expect(page.getByRole("button", { name: "新增菜单" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "新增" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "编辑" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "删除" })).toHaveCount(0);
    expect(state.writePayloads).toHaveLength(0);
  });
});
