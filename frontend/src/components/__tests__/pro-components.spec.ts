import { defineComponent } from "vue";
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";

const ElFormStub = defineComponent({
  props: ["model"],
  setup(_, { expose }) {
    expose({
      resetFields: () => undefined,
      clearValidate: () => undefined,
      validate: () => true,
    });

    return {};
  },
  template: "<form class='el-form-stub'><slot /></form>",
});

const ElFormItemStub = defineComponent({
  template: "<div class='el-form-item-stub'><slot /></div>",
});

const ElButtonStub = defineComponent({
  emits: ["click"],
  template: "<button @click=\"$emit('click')\"><slot /></button>",
});

const ElTableStub = defineComponent({
  emits: ["selection-change"],
  template: "<div class='ff-table'><slot /></div>",
});

const ElTableColumnStub = defineComponent({
  template: "<div class='el-table-column-stub'><slot /></div>",
});

const ElDrawerStub = defineComponent({
  props: ["modelValue", "title"],
  emits: ["update:modelValue", "close"],
  template:
    "<section class='el-drawer-stub'><header>{{ title }}</header><div><slot /></div><footer><slot name='footer' /></footer></section>",
});

const testGlobal = {
  stubs: {
    "el-form": ElFormStub,
    "el-form-item": ElFormItemStub,
    "el-input": true,
    "el-button": ElButtonStub,
    "el-table": ElTableStub,
    "el-table-column": ElTableColumnStub,
    "el-drawer": ElDrawerStub,
  },
  directives: {
    loading: () => undefined,
  },
};

describe("pro components", () => {
  it("renders ProSearch and emits submit/reset", async () => {
    const wrapper = mount(ProSearch, {
      props: {
        model: {
          keyword: "",
        },
      },
      slots: {
        default: "<el-form-item label='关键字'><el-input /></el-form-item>",
      },
      global: testGlobal,
    });

    expect(wrapper.find(".ff-filter-panel").exists()).toBe(true);
    expect(wrapper.find(".ff-toolbar").exists()).toBe(true);

    const buttons = wrapper.findAll("button");
    await buttons[0]?.trigger("click");
    await buttons[1]?.trigger("click");

    expect(wrapper.emitted("submit")).toHaveLength(1);
    expect(wrapper.emitted("reset")).toHaveLength(1);
  });

  it("renders ProTable and forwards selection/pagination events", async () => {
    const wrapper = mount(ProTable, {
      props: {
        title: "用户数据",
        data: [{ id: 1, name: "admin" }],
        total: 20,
        page: 1,
        limit: 10,
      },
      slots: {
        actions: "<button class='create-btn'>新增</button>",
        default:
          "<el-table-column type='selection' width='50' /><el-table-column label='昵称' prop='name' />",
      },
      global: {
        ...testGlobal,
        stubs: {
          ...testGlobal.stubs,
          Pagination: {
            template:
              "<button class='pagination-trigger' @click=\"$emit('pagination')\">pagination</button>",
          },
        },
      },
    });

    expect(wrapper.find(".ff-data-panel__title").text()).toContain("用户数据");
    expect(wrapper.find(".create-btn").exists()).toBe(true);
    expect(wrapper.find(".ff-table").exists()).toBe(true);

    await wrapper.find(".pagination-trigger").trigger("click");
    expect(wrapper.emitted("pagination")).toHaveLength(1);
  });

  it("renders ProFormDrawer and emits submit/cancel", async () => {
    const wrapper = mount(ProFormDrawer, {
      props: {
        modelValue: true,
        title: "新增用户",
        model: {
          username: "",
        },
      },
      slots: {
        default: "<el-form-item label='用户名'><el-input /></el-form-item>",
      },
      global: testGlobal,
    });

    expect(wrapper.find(".el-drawer-stub").exists()).toBe(true);

    const buttons = wrapper.findAll("button");
    await buttons[0]?.trigger("click");
    await buttons[1]?.trigger("click");

    expect(wrapper.emitted("submit")).toHaveLength(1);
    expect(wrapper.emitted("cancel")).toHaveLength(1);
  });
});
