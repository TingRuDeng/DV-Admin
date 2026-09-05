import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { compile } from "sass";
import { describe, expect, it } from "vitest";

const readProjectFile = (relativePath: string) =>
  readFileSync(resolve(process.cwd(), relativePath), "utf8");

const TAG_ITEM_SOURCE = readProjectFile("src/layouts/components/TagsView/TagItem.vue");
const NAVBAR_ACTIONS_SOURCE = readProjectFile(
  "src/layouts/components/NavBar/components/NavbarActions.vue"
);
const MIX_LAYOUT_SOURCE = readProjectFile("src/layouts/modes/mix/index.vue");

const GLOBAL_PAGE_STYLE_FILES = [
  "src/styles/pages/_login.scss",
  "src/styles/pages/_profile.scss",
  "src/styles/pages/_system-role.scss",
  "src/styles/pages/_system-user.scss",
];

describe("壳层审计回归约束", () => {
  it("移除旧 Vite 后仍能加载开发 Mock 插件及其 esbuild 依赖", async () => {
    const plugin = await import("vite-plugin-mock-dev-server");

    expect(plugin.mockDevServerPlugin).toBeTypeOf("function");
  });

  it("把 TagsView 的视觉样式绑定到组件根节点", () => {
    expect(TAG_ITEM_SOURCE).toMatch(/<el-tag[\s\S]*class="tags-view-item"/);
    expect(TAG_ITEM_SOURCE).not.toContain(":deep(.el-tag)");
    expect(TAG_ITEM_SOURCE).toContain("height: 30px");
    expect(TAG_ITEM_SOURCE).toContain("&:focus-visible");
  });

  it("移除死的标签栏重置，并为传送菜单提供全局表面", () => {
    const elementPlusSource = readProjectFile("src/styles/element-plus.scss");
    const menuSkinSource = readProjectFile("src/styles/skins/_menu.scss");
    const css = compile(resolve(process.cwd(), "src/styles/index.scss")).css;

    expect(elementPlusSource).not.toContain(".tags-view-container");
    expect(elementPlusSource).not.toContain(".layout-tags-container");
    expect(menuSkinSource).toContain(".el-menu--popup");
    expect(css).not.toContain(":deep(");
  });

  it("不在全局页面 SCSS 中保留只能由 Vue SFC 改写的 :deep()", () => {
    const offenders = GLOBAL_PAGE_STYLE_FILES.filter((file) =>
      readProjectFile(file).includes(":deep(")
    );

    expect(offenders).toEqual([]);
  });

  it("通过共享 PageShell 和 ProTable skin 覆盖所有系统数据页的移动端收缩", () => {
    const foundationSource = readProjectFile("src/styles/foundation/_layout.scss");
    const tableSkinSource = readProjectFile("src/styles/skins/_table.scss");
    const pageFiles = [
      ["src/views/system/role/index.vue", "ff-role-page"],
      ["src/views/system/menu/index.vue", "ff-menu-page"],
      ["src/views/system/dept/index.vue", "ff-dept-page"],
      ["src/views/system/dict/index.vue", "ff-dict-page"],
      ["src/views/system/dict/dict-item.vue", "ff-dict-item-page"],
      ["src/views/system/log/index.vue", "ff-log-page"],
      ["src/views/system/notice/index.vue", "ff-notice-page"],
      ["src/views/system/notice/components/MyNotice.vue", "ff-my-notice-page"],
    ];

    for (const [file, pageClass] of pageFiles) {
      expect(readProjectFile(file)).toContain(`<PageShell class="${pageClass}">`);
    }
    expect(foundationSource).toMatch(/\.ff-page-shell\s*\{[\s\S]*?min-width:\s*0/);
    expect(tableSkinSource).toContain("@media (max-width: 767px)");
    expect(tableSkinSource).toContain(".ff-page-shell .ff-table .el-table-fixed-column--right");
  });

  it("让导航栏动作使用可聚焦且有名称的原生控件", () => {
    const componentSources = [
      NAVBAR_ACTIONS_SOURCE,
      readProjectFile("src/components/MenuSearch/index.vue"),
      readProjectFile("src/components/Fullscreen/index.vue"),
      readProjectFile("src/components/SizeSelect/index.vue"),
      readProjectFile("src/components/LangSelect/index.vue"),
      readProjectFile("src/components/Notification/index.vue"),
    ];

    for (const source of componentSources) {
      expect(source).toContain("aria-label");
      expect(source).toContain("<button");
    }
    expect(NAVBAR_ACTIONS_SOURCE).toMatch(
      /<button[\s\S]*navbar-actions__button[\s\S]*aria-label[\s\S]*@click="handleSettingsClick"/
    );
  });

  it("让 mix 移动端抽屉样式命中布局根节点", () => {
    expect(MIX_LAYOUT_SOURCE).toContain(":global(.mobile)");
    expect(MIX_LAYOUT_SOURCE).toContain("transform: translateX(-$sidebar-width)");
  });

  it("让测试与构建共用 Vite 8，并移除未启用的 MSW", () => {
    const packageSource = readProjectFile("package.json");
    const lockSource = readProjectFile("pnpm-lock.yaml");
    const workspaceSource = readProjectFile("pnpm-workspace.yaml");
    const vitestSource = readProjectFile("vitest.config.ts");
    const tsconfigSource = readProjectFile("tsconfig.json");

    expect(packageSource).toContain('"vitest": "^4.1.11"');
    expect(packageSource).not.toContain('"msw"');
    expect(lockSource).not.toContain("vite@7.");
    expect(workspaceSource).not.toContain("msw:");
    expect(vitestSource).not.toContain("deps:");
    expect(vitestSource).not.toContain("__dirname");
    expect(tsconfigSource).toContain('"vitest.config.ts"');
    expect(existsSync(resolve(process.cwd(), "src/mocks/handlers.ts"))).toBe(false);
    expect(existsSync(resolve(process.cwd(), "public/mockServiceWorker.js"))).toBe(false);
  });
});
