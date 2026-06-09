import { expect, test, type Page, type Route } from "@playwright/test";

interface MockState {
  uploadCount: number;
  deletedPaths: string[];
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
  searchParams: URLSearchParams;
  state: MockState;
  auth: AuthMockOptions;
}

const API_PREFIX = "/dev-api";
const FILES_PATH = "/api/v1/files/";
const DEFAULT_FILE_PERMS = ["demo:upload:query"];
const UPLOADED_FILE = {
  name: "e2e-file.txt",
  url: "http://127.0.0.1/media/files/1/e2e-file.txt",
  path: "files/1/e2e-file.txt",
};

function createMockState(): MockState {
  return {
    uploadCount: 0,
    deletedPaths: [],
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

async function installFileUploadMocks(page: Page, state: MockState, auth: AuthMockOptions = {}) {
  await page.route(`**${API_PREFIX}/api/v1/**`, async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const context = {
      route,
      method: request.method(),
      path: url.pathname.replace(API_PREFIX, ""),
      searchParams: url.searchParams,
      state,
      auth,
    };

    if (await handleAuthRequest(context)) return;
    if (await handleFileRequest(context)) return;

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
    perms: auth.perms ?? DEFAULT_FILE_PERMS,
  };
}

async function handleFileRequest(context: MockRouteContext) {
  if (context.method === "POST" && context.path === FILES_PATH) {
    context.state.uploadCount += 1;
    await fulfillJson(context.route, success(UPLOADED_FILE));
    return true;
  }

  if (context.method === "DELETE" && context.path === FILES_PATH) {
    context.state.deletedPaths.push(context.searchParams.get("filePath") ?? "");
    await fulfillJson(context.route, success(null));
    return true;
  }

  return false;
}

function buildRoutes() {
  return [
    {
      path: "/demo",
      component: "Layout",
      name: "Demo",
      meta: { title: "组件示例", icon: "component" },
      children: [
        {
          path: "upload",
          component: "demo/upload",
          name: "DemoUpload",
          meta: { title: "文件上传", perms: DEFAULT_FILE_PERMS },
        },
      ],
    },
  ];
}

test.describe("文件上传删除链路 smoke", () => {
  test("上传后使用后端返回的相对 path 删除文件", async ({ page }) => {
    const state = createMockState();
    await installFileUploadMocks(page, state);

    await page.goto("/login?redirect=%2Fdemo%2Fupload");
    await page.getByLabel("用户名").fill("admin");
    await page.getByLabel("密码").fill("123456");
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();

    await expect(page).toHaveURL(/\/demo\/upload/);
    const fileUploadFormItem = page.locator(".el-form-item", { hasText: "文件上传" });
    await expect(fileUploadFormItem.getByRole("button", { name: "上传文件" })).toBeVisible();

    await fileUploadFormItem.locator("input[type=file]").setInputFiles({
      name: UPLOADED_FILE.name,
      mimeType: "text/plain",
      buffer: Buffer.from("file upload delete e2e"),
    });

    await expect.poll(() => state.uploadCount).toBe(1);
    const uploadedRow = fileUploadFormItem
      .locator(".el-upload-list__item")
      .filter({ hasText: UPLOADED_FILE.name });
    await expect(uploadedRow).toBeVisible();

    await uploadedRow.hover();
    await uploadedRow.locator(".el-icon--close").click();

    await expect.poll(() => state.deletedPaths).toEqual([UPLOADED_FILE.path]);
    await expect(fileUploadFormItem.getByText(UPLOADED_FILE.name)).toHaveCount(0);
  });
});
