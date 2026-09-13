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
  content?: string;
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
  pageQueries: Array<Record<string, string>>;
  detailRequests: string[];
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
        content: "<p>系统维护<strong>富文本</strong>正文</p>",
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
        content: "<p>安全提醒正文</p>",
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
    pageQueries: [],
    detailRequests: [],
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
  if (context.method === "GET" && context.path === `${NOTICES_PATH}/my-page/`) {
    await fulfillJson(context.route, success({ list: [], total: 0 }));
    return true;
  }

  if (context.method === "GET" && context.path === "/api/v1/system/users/options/") {
    await fulfillJson(context.route, success([{ id: "1", label: "管理员", value: "1" }]));
    return true;
  }

  if (context.method === "GET" && context.path === `${NOTICES_PATH}/page`) {
    context.state.pageQueries.push(Object.fromEntries(context.query.entries()));
    const title = context.query.get("title")?.trim();
    const publishStatus = context.query.get("publishStatus");
    const filteredNotices = context.state.notices.filter((notice) => {
      const matchesTitle = !title || notice.title.includes(title);
      const matchesStatus =
        publishStatus === null ||
        publishStatus === "" ||
        notice.publishStatus === Number(publishStatus);
      return matchesTitle && matchesStatus;
    });
    await fulfillJson(
      context.route,
      success({ list: filteredNotices, total: filteredNotices.length })
    );
    return true;
  }

  const detailMatch = context.path.match(/^\/api\/v1\/system\/notices\/(\d+)\/detail$/);
  if (context.method === "GET" && detailMatch) {
    const notice = context.state.notices.find((item) => item.id === detailMatch[1]);
    context.state.detailRequests.push(detailMatch[1]);
    await fulfillJson(context.route, success(notice ?? {}));
    return true;
  }

  const publishMatch = context.path.match(/^\/api\/v1\/system\/notices\/(\d+)\/publish$/);
  if (context.method === "PUT" && publishMatch) {
    const notice = context.state.notices.find((item) => item.id === publishMatch[1]);
    if (notice) notice.publishStatus = 1;
    context.state.writePayloads.push({ action: "publish", id: publishMatch[1] });
    await fulfillJson(context.route, success(null));
    return true;
  }

  const revokeMatch = context.path.match(/^\/api\/v1\/system\/notices\/(\d+)\/revoke$/);
  if (context.method === "PUT" && revokeMatch) {
    const notice = context.state.notices.find((item) => item.id === revokeMatch[1]);
    if (notice) notice.publishStatus = -1;
    context.state.writePayloads.push({ action: "revoke", id: revokeMatch[1] });
    await fulfillJson(context.route, success(null));
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
  const dictCode = context.query.get("dictCode") ?? "";
  const items = context.state.dictItemsByCode[dictCode] ?? [];
  const pageNum = Number(context.query.get("pageNum") ?? 1);
  const pageSize = Number(context.query.get("pageSize") ?? 10);
  const start = (pageNum - 1) * pageSize;
  await fulfillJson(
    context.route,
    success({ list: items.slice(start, start + pageSize), total: items.length })
  );
  return true;
}

async function login(page: Page) {
  await page.goto("/login?redirect=%2Fsystem%2Fnotices");
  await page.getByLabel("用户名").fill("admin");
  await page.getByLabel("密码").fill("123456");
  await page.getByRole("button", { name: /登\s*录|Login/i }).click();
  await expect(page).toHaveURL(/\/system\/notices/);
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
  test("编辑器语言跟随切换且保留草稿与撤销记录", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const state = createMockState();
    await installNoticeManagementMocks(page, state);
    await login(page);

    await page.getByRole("button", { name: "新增通知", exact: true }).click();
    const drawer = page.getByRole("dialog");
    const editor = drawer.locator("[data-slate-editor]");
    const placeholder = drawer.locator(".w-e-text-placeholder");
    const toolbar = drawer.locator(".w-e-toolbar");
    await expect(placeholder).toHaveText("请输入内容...");
    await drawer.getByRole("button", { name: "取消", exact: true }).click();
    await page.getByRole("button", { name: "切换语言" }).click();
    await page.getByRole("menuitem", { name: "English" }).click();
    await page.getByRole("button", { name: "Add announcement", exact: true }).click();
    await expect(placeholder).toHaveText("Enter content...");
    await expect(toolbar.getByRole("button", { name: "Bold", exact: true })).toBeVisible();
    const editorId = await editor.getAttribute("id");

    await editor.click();
    const bold = toolbar.getByRole("button", { name: "Bold", exact: true });
    await expect(bold).not.toHaveClass(/disabled/);
    await bold.click();
    await expect(bold).toHaveClass(/active/);
    await editor.pressSequentially("Draft stays intact");
    await expect(editor.locator("strong")).toHaveText("Draft stays intact");
    const draftHtml = await editor.innerHTML();

    // Keep the open modal and draft intact while exercising the application's locale source.
    // The navbar language control is outside the modal's focus boundary.
    for (const locale of ["zh-cn", "en"]) {
      await page.evaluate(async (language) => {
        const modulePath = "/src/lang/index.ts";
        const { default: i18n } = await import(/* @vite-ignore */ modulePath);
        i18n.global.locale.value = language;
      }, locale);
      await expect(toolbar.locator('[data-menu-key="bold"]')).toHaveAttribute(
        "aria-label",
        locale === "en" ? "Bold" : "粗体"
      );
      await expect(editor).toHaveAttribute("id", editorId!);
      expect(await editor.innerHTML()).toBe(draftHtml);
      await expect(toolbar.locator("svg:not([data-editor-lucide])")).toHaveCount(0);
    }
    // The native language change dismisses its selection/hoverbar; resume editing
    // before checking that the original document history remains available.
    await editor.click();
    await expect(toolbar.locator('[data-menu-key="undo"]')).not.toHaveClass(/disabled/);
    await toolbar.locator('[data-menu-key="undo"]').click();
    await expect(editor).not.toContainText("Draft stays intact");
    await toolbar.locator('[data-menu-key="redo"]').click();
    await expect(editor.locator("strong")).toHaveText("Draft stays intact");
    await expect(placeholder).not.toBeVisible();
    await editor.click();
    await editor.press("ControlOrMeta+A");
    await editor.press("Backspace");
    await expect(placeholder).toBeVisible();
    await expect(placeholder).toHaveText("Enter content...");
    await drawer.getByRole("button", { name: "Cancel", exact: true }).click();
    await page.reload();
    await page.getByRole("button", { name: "Add announcement", exact: true }).click();
    await expect(placeholder).toHaveText("Enter content...");
    await expect(toolbar.getByRole("button", { name: "Bold", exact: true })).toBeVisible();
    expect(errors).toEqual([]);
    expect(state.writePayloads).toEqual([]);
  });

  test("后端通知权限码应显示通知写操作", async ({ page }) => {
    const state = createMockState();
    await installNoticeManagementMocks(page, state);

    await login(page);
    await expect(page.locator("tbody").getByText("系统维护计划")).toBeVisible();
    await expect(page.getByRole("button", { name: "新增通知" })).toBeVisible();
    await expect(page.getByRole("button", { name: "批量删除" })).toBeVisible();
    await expect(page.getByRole("button", { name: "发布" })).toBeVisible();
    await expect(page.getByRole("button", { name: "撤回" })).toBeVisible();
    await expect(page.getByRole("button", { name: "编辑" })).toBeVisible();
    await expect(page.getByRole("button", { name: "删除", exact: true })).toBeVisible();

    await page.getByPlaceholder("标题").fill("系统维护");
    await page.getByRole("button", { name: "搜索", exact: true }).click();
    await expect.poll(() => state.pageQueries.at(-1)?.title).toBe("系统维护");
    await expect(page.locator("tbody").getByText("安全提醒")).toHaveCount(0);
    await page.getByRole("button", { name: "重置" }).click();

    const draftRow = page.locator(".el-table__row", { hasText: "系统维护计划" });
    await draftRow.getByRole("button", { name: "查看" }).click();
    const detailDialog = page.locator(".ff-notice-detail-dialog");
    await expect(detailDialog).toContainText("系统维护富文本正文");
    await detailDialog.getByRole("button", { name: "关闭通知详情" }).click();
    expect(state.detailRequests).toEqual(["801"]);

    await draftRow.getByRole("button", { name: "发布" }).click();
    await expect.poll(() => state.notices[0].publishStatus).toBe(1);
    await expect(draftRow).toContainText("已发布");

    const publishedRow = page.locator(".el-table__row", { hasText: "安全提醒" });
    await publishedRow.getByRole("button", { name: "撤回" }).click();
    await expect.poll(() => state.notices[1].publishStatus).toBe(-1);
    await expect(publishedRow).toContainText("已撤回");

    await page.getByRole("button", { name: "新增通知" }).click();
    const drawer = page.locator(".el-drawer", { hasText: "新增公告" });
    await expect(drawer).toBeVisible();
    const toolbar = drawer.locator(".w-e-bar");
    await expect(toolbar.locator('svg[data-editor-lucide="true"]').first()).toBeVisible();
    await expect(toolbar.locator("svg:not([data-editor-lucide])")).toHaveCount(0);
    await expect(toolbar.getByRole("button", { name: "上传图片", exact: true })).toBeVisible();
    const editor = drawer.locator("[data-slate-editor]");
    await editor.click();
    const bold = toolbar.locator('[data-menu-key="bold"]');
    await expect(bold).not.toHaveClass(/disabled/);
    await bold.click();
    await editor.pressSequentially("Lucide editor");
    await expect(editor).toContainText("Lucide editor");
    await expect(toolbar.locator('[data-menu-key="bold"]')).toHaveClass(/active/);
    const fullscreen = toolbar.locator('[data-menu-key="fullScreen"]');
    await fullscreen.click();
    await expect(fullscreen.locator(".lucide-minimize-2")).toBeVisible();
    await fullscreen.click();
    await expect(fullscreen.locator(".lucide-maximize-2")).toBeVisible();
    await expect(editor).toContainText("Lucide editor");
    await drawer.getByRole("button", { name: /取\s*消/ }).click();
    expect(state.writePayloads).toEqual([
      { action: "publish", id: "801" },
      { action: "revoke", id: "802" },
    ]);
  });

  test("移动端详情和表单保持在视口内", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    const state = createMockState();
    await installNoticeManagementMocks(page, state);
    await login(page);

    const row = page.locator(".el-table__row", { hasText: "系统维护计划" });
    await row.getByRole("button", { name: "查看" }).click();
    const dialog = page.locator(".ff-notice-detail-dialog");
    await expect(dialog).toBeVisible();
    await expect
      .poll(() => dialog.evaluate((element) => element.getBoundingClientRect().width))
      .toBeLessThanOrEqual(390);
    await dialog.getByRole("button", { name: "关闭通知详情" }).click();

    await page.getByRole("button", { name: "新增通知" }).click();
    const drawer = page.locator(".el-drawer", { hasText: "新增公告" });
    await expect
      .poll(() => drawer.evaluate((element) => element.getBoundingClientRect().width))
      .toBeLessThanOrEqual(390);
    await drawer.getByRole("button", { name: /取\s*消/ }).click();

    const pageWidth = await page.evaluate(() => ({
      viewport: window.innerWidth,
      document: document.documentElement.scrollWidth,
    }));
    expect(pageWidth.document).toBeLessThanOrEqual(pageWidth.viewport);
  });
});
