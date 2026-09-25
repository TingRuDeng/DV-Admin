import { expect, test, type Page, type Route } from "@playwright/test";

const API_PREFIX = "/dev-api";
const OIDC_FLOW_KEY = "vea:auth:oidc_flow";

function success(data: unknown) {
  return { code: 20000, message: "成功", data };
}

async function fulfillJson(route: Route, data: unknown, status = 200) {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(data) });
}

async function installMocks(page: Page) {
  const oidcLoginBodies: Record<string, unknown>[] = [];
  await page.route(`**${API_PREFIX}/api/v1/**`, async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname.replace(API_PREFIX, "");
    const method = request.method();

    if (method === "POST" && path === "/api/v1/oauth/oidc/login/") {
      oidcLoginBodies.push(request.postDataJSON());
      await fulfillJson(
        route,
        success({
          accessToken: "oidc-access-token",
          refreshToken: "oidc-refresh-token",
          tokenType: "bearer",
          expiresIn: 3600,
        })
      );
      return;
    }
    if (method === "GET" && path === "/api/v1/oauth/info/") {
      await fulfillJson(
        route,
        success({ id: "7", username: "sso_user", name: "SSO", roles: ["user"], perms: [] })
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
                path: "roles",
                component: "system/role/index",
                name: "Role",
                meta: { title: "角色管理", icon: "role" },
              },
            ],
          },
        ])
      );
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
    await fulfillJson(route, { code: 404, message: `未 mock 的接口: ${method} ${path}` }, 404);
  });
  return oidcLoginBodies;
}

async function saveFlow(page: Page, state: string) {
  await page.goto("/login");
  await page.evaluate(
    ([key, value]) => sessionStorage.setItem(key, value),
    [
      OIDC_FLOW_KEY,
      JSON.stringify({ state, flowSecret: "flow-secret-1", redirect: "/system/roles" }),
    ]
  );
}

test.describe("单点登录回调", () => {
  test("state 一致时兑换授权码、清理地址栏并进入发起前的页面", async ({ page }) => {
    const bodies = await installMocks(page);
    await saveFlow(page, "state-1");

    await page.goto("/oidc/callback?code=code-1&state=state-1&iss=https%3A%2F%2Fidp.example");

    await expect(page).toHaveURL(/\/system\/roles$/);
    expect(bodies).toEqual([
      {
        authorizationCode: "code-1",
        state: "state-1",
        flowSecret: "flow-secret-1",
        iss: "https://idp.example",
      },
    ]);
    expect(await page.evaluate((key) => sessionStorage.getItem(key), OIDC_FLOW_KEY)).toBeNull();
    expect(page.url()).not.toContain("code-1");
  });

  test("state 不一致时不发请求，并能返回登录页", async ({ page }) => {
    const bodies = await installMocks(page);
    await saveFlow(page, "state-1");

    await page.goto("/oidc/callback?code=code-1&state=forged-state");

    await expect(page.getByRole("alert")).toContainText("登录状态无效或已过期");
    expect(page.url()).not.toContain("code-1");
    expect(bodies).toEqual([]);
    await page.getByRole("button", { name: "返回登录" }).click();
    await expect(page).toHaveURL(/\/login$/);
  });
});
