import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";
import ElementPlus, { ElFormItem } from "element-plus";
import zhCn from "@/lang/package/zh-cn.json";
import en from "@/lang/package/en.json";
import DictFormDrawer from "../dict/components/DictFormDrawer.vue";
import DictItemFormDrawer from "../dict/components/DictItemFormDrawer.vue";
import MenuFormDrawer from "../menu/components/MenuFormDrawer.vue";
import RoleFormDrawer from "../role/components/RoleFormDrawer.vue";
import NoticeFormDrawer from "../notice/components/NoticeFormDrawer.vue";

vi.mock("@/store/modules/app-store", () => ({ useAppStore: () => ({ device: "desktop" }) }));
vi.mock("@/api/system/dept-api", () => ({ default: { getOptions: async () => [] } }));
vi.mock("@/api/system/menu-api", () => ({ default: { getOptions: async () => [] } }));
vi.mock("@/api/system/user-api", () => ({ default: { getOptions: async () => [] } }));
vi.mock("@/api/system/dict-api", () => ({ default: {} }));
vi.mock("@/api/system/dict-items-api", () => ({ default: {} }));
vi.mock("@/api/system/role-api", () => ({ default: {} }));
vi.mock("@/api/system/notice-api", () => ({ default: {} }));

const cases = [
  { component: DictFormDrawer, field: "name", title: "addDict", error: "dictNameInput" },
  { component: DictItemFormDrawer, field: "label", title: "addDictItem", error: "dictLabelInput" },
  { component: MenuFormDrawer, field: "name", title: "addMenu", error: "menuNameRequired" },
  { component: RoleFormDrawer, field: "name", title: "addRole", error: "roleNameRequired" },
  {
    component: NoticeFormDrawer,
    field: "title",
    title: "addNoticeTitle",
    error: "noticeTitleRequired",
  },
] as const;

function renderForm(component: (typeof cases)[number]["component"]) {
  const i18n = createI18n({ legacy: false, locale: "zh-cn", messages: { "zh-cn": zhCn, en } });
  const wrapper = mount(component, {
    props: { dictList: [] },
    global: {
      plugins: [i18n, ElementPlus],
      stubs: {
        ElDrawer: {
          props: ["modelValue", "title"],
          template:
            '<section v-if="modelValue"><h2>{{ title }}</h2><slot /><slot name="footer" /></section>',
        },
        IconSelect: true,
        Dict: true,
        WangEditor: true,
      },
    },
  });
  return { wrapper, i18n };
}

let rendered: ReturnType<typeof renderForm> | undefined;
beforeEach(() => vi.stubGlobal("useDebounceFn", (fn: () => void) => fn));
afterEach(() => {
  rendered?.wrapper.unmount();
  vi.unstubAllGlobals();
});

describe("system forms keep language changes reactive", () => {
  for (const item of cases) {
    it(`${item.title}: updates titles without clearing input or validating untouched fields`, async () => {
      rendered = renderForm(item.component);
      const { wrapper, i18n } = rendered;
      await wrapper.vm.openCreate();
      await flushPromises();
      const input = wrapper
        .findAllComponents(ElFormItem)
        .find((field) => field.props("prop") === item.field)!
        .get("input");
      await input.setValue("Draft value");
      i18n.global.locale.value = "en";
      await flushPromises();
      expect(wrapper.get("h2").text()).toBe(i18n.global.t(`system.${item.title}`));
      expect((input.element as HTMLInputElement).value).toBe("Draft value");
      expect(wrapper.findAll(".el-form-item__error")).toHaveLength(0);

      if (item.title === "addMenu") expect(wrapper.text()).toContain("Top level");
      i18n.global.locale.value = "zh-cn";
      await flushPromises();
      expect(wrapper.get("h2").text()).toBe(i18n.global.t(`system.${item.title}`));
      expect((input.element as HTMLInputElement).value).toBe("Draft value");
      expect(wrapper.findAll(".el-form-item__error")).toHaveLength(0);
    });
  }
});
