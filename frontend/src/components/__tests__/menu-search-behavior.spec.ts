import { nextTick } from "vue";
import type { RouteRecordRaw } from "vue-router";
import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import zhCn from "@/lang/package/zh-cn.json";
import MenuSearch from "@/components/MenuSearch/index.vue";

const view = () => Promise.resolve({});

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  routes: [] as RouteRecordRaw[],
  translate: (key: string) => key,
}));

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => mocks.translate(key) }),
}));

vi.mock("vue-router", async (importOriginal) => ({
  ...(await importOriginal<typeof import("vue-router")>()),
  useRoute: () => ({ fullPath: "/system/users" }),
  useRouter: () => ({ push: mocks.push }),
}));

vi.mock("@/store", () => ({
  usePermissionStore: () => ({ routes: mocks.routes }),
}));

const HISTORY_KEY = "menu_search_history";
const NAVBAR_MESSAGES = zhCn.navbar as Record<string, string>;

let wrapper: VueWrapper | undefined;

function mountMenuSearch() {
  wrapper = mount(MenuSearch, {
    attachTo: document.body,
    global: { stubs: { teleport: true } },
  });
  return wrapper;
}

function getInput() {
  return wrapper!.get<HTMLInputElement>("input");
}

function getListbox() {
  return wrapper!.get('[role="listbox"]');
}

function optionTitles() {
  return wrapper!.findAll('[role="option"]').map((option) => option.text());
}

async function press(key: string, init: KeyboardEventInit = {}) {
  await getInput().trigger("keydown", { key, ...init });
}

beforeEach(() => {
  mocks.push.mockReset();
  mocks.translate = (key) => NAVBAR_MESSAGES[key.replace("navbar.", "")] ?? key;
  mocks.routes = [
    {
      path: "/",
      component: view,
      children: [
        { path: "profile", component: view, meta: { title: "个人中心", hidden: true } },
        { path: "/detail/:id(\\d+)", component: view, meta: { title: "详情页缓存" } },
      ],
    },
    {
      path: "/system",
      component: view,
      meta: { title: "系统管理" },
      children: [
        { path: "users", component: view, meta: { title: "用户管理" } },
        { path: "roles", component: view, meta: { title: "角色管理" } },
      ],
    },
  ];
  localStorage.clear();
});

afterEach(() => {
  wrapper?.unmount();
  wrapper = undefined;
  document.body.innerHTML = "";
});

describe("MenuSearch 内联 combobox", () => {
  it("在原生输入框上暴露 combobox 语义", () => {
    mountMenuSearch();
    const input = getInput();
    const listbox = getListbox();

    expect(input.attributes("role")).toBe("combobox");
    expect(input.attributes("aria-label")).toBe("搜索菜单");
    expect(input.attributes("placeholder")).toBe("搜索菜单");
    expect(input.attributes("aria-autocomplete")).toBe("list");
    expect(input.attributes("aria-expanded")).toBe("false");
    expect(input.attributes("aria-controls")).toBe(listbox.attributes("id"));
    expect(input.attributes("aria-activedescendant")).toBeUndefined();
    expect(wrapper!.get(".menu-search__kbd").attributes("aria-hidden")).toBe("true");
  });

  it("按标题不区分大小写过滤，回车在没有高亮时选第一个匹配", async () => {
    mocks.routes[1].children!.push({
      path: "logs",
      component: view,
      meta: { title: "Audit Log" },
    });
    mountMenuSearch();
    const input = getInput();

    await input.trigger("focus");
    await input.setValue("audit");
    expect(optionTitles()).toEqual(["Audit Log"]);

    await input.setValue("管理");
    expect(input.attributes("aria-expanded")).toBe("true");
    expect(optionTitles()).toEqual(["用户管理", "角色管理"]);

    await input.setValue("角色");
    await press("Enter");

    expect(mocks.push).toHaveBeenCalledWith({ path: "/system/roles", query: undefined });
    expect(input.element.value).toBe("");
    expect(input.attributes("aria-expanded")).toBe("false");
    expect(JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]")[0].path).toBe("/system/roles");
  });

  it("上下键循环高亮并同步 aria-activedescendant，Esc 只收起面板", async () => {
    mountMenuSearch();
    const input = getInput();

    await input.trigger("focus");
    await input.setValue("管理");
    await press("ArrowUp");

    const options = wrapper!.findAll('[role="option"]');
    expect(input.attributes("aria-activedescendant")).toBe(options[1].attributes("id"));
    expect(options[1].attributes("aria-selected")).toBe("true");

    await press("ArrowDown");
    expect(input.attributes("aria-activedescendant")).toBe(options[0].attributes("id"));

    await press("Enter");
    expect(mocks.push).toHaveBeenCalledWith({ path: "/system/users", query: undefined });

    await input.trigger("focus");
    await input.setValue("用户");
    await press("Escape");
    expect(input.attributes("aria-expanded")).toBe("false");
    expect(getListbox().isVisible()).toBe(false);
    expect(input.element.value).toBe("用户");
  });

  it("隐藏路由和参数路由搜不到，给出空状态但不展开 listbox", async () => {
    mountMenuSearch();
    const input = getInput();

    await input.trigger("focus");
    await input.setValue("个人中心");

    expect(input.attributes("aria-expanded")).toBe("false");
    expect(wrapper!.get('[role="status"]').text()).toBe("无匹配菜单");

    await input.setValue("详情");
    expect(wrapper!.get('[role="status"]').text()).toBe("无匹配菜单");
  });

  it("空关键字展示历史，Delete 删除高亮项，清空按钮在 listbox 之外", async () => {
    localStorage.setItem(
      HISTORY_KEY,
      JSON.stringify([
        { title: "角色管理", path: "/system/roles" },
        { title: "用户管理", path: "/system/users" },
      ])
    );
    mountMenuSearch();
    const input = getInput();

    await input.trigger("focus");
    expect(input.attributes("aria-expanded")).toBe("true");
    expect(getListbox().attributes("aria-label")).toBe("搜索历史");
    expect(optionTitles()).toEqual(["角色管理", "用户管理"]);
    expect(getListbox().find("button").exists()).toBe(false);
    expect(wrapper!.find('[role="option"] [tabindex]').exists()).toBe(false);

    await press("ArrowDown");
    await press("Delete");
    expect(optionTitles()).toEqual(["用户管理"]);
    expect(input.attributes("aria-activedescendant")).toBe(
      wrapper!.get('[role="option"]').attributes("id")
    );

    const clearButton = wrapper!.get(".menu-search__footer button");
    expect(clearButton.text()).toBe("清空历史");
    await clearButton.trigger("click");

    expect(localStorage.getItem(HISTORY_KEY)).toBeNull();
    expect(input.attributes("aria-expanded")).toBe("false");
    expect(wrapper!.find(".menu-search__panel").isVisible()).toBe(false);
  });

  it("鼠标删除历史项不会触发跳转", async () => {
    localStorage.setItem(
      HISTORY_KEY,
      JSON.stringify([{ title: "角色管理", path: "/system/roles" }])
    );
    mountMenuSearch();

    await getInput().trigger("focus");
    const remove = wrapper!.get(".menu-search__remove");
    expect(remove.attributes("aria-hidden")).toBe("true");
    await remove.trigger("click");

    expect(mocks.push).not.toHaveBeenCalled();
    expect(localStorage.getItem(HISTORY_KEY)).toBe("[]");
  });

  it("⌘/Ctrl+K 聚焦输入框，组字中或有可见遮罩时忽略", async () => {
    mountMenuSearch();
    const input = getInput();
    const dispatch = (init: KeyboardEventInit) =>
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "k", bubbles: true, cancelable: true, ...init })
      );

    dispatch({ ctrlKey: true, isComposing: true });
    expect(document.activeElement).not.toBe(input.element);

    const overlay = document.createElement("div");
    overlay.className = "el-overlay";
    document.body.appendChild(overlay);
    dispatch({ metaKey: true });
    expect(document.activeElement).not.toBe(input.element);

    overlay.style.display = "none";
    dispatch({ metaKey: true });
    await nextTick();
    expect(document.activeElement).toBe(input.element);
  });
});
