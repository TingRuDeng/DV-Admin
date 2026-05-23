/* eslint-disable vue/one-component-per-file */
import { defineComponent, nextTick, type PropType } from "vue";
import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import TableSelect from "@/components/TableSelect/index.vue";

const pageRows = [
  { id: 1, name: "admin" },
  { id: 2, name: "visitor" },
];

const globalConfig = {
  directives: {
    loading: () => undefined,
  },
  stubs: {
    ArrowDown: true,
    ElIcon: {
      template: "<span><slot /></span>",
    },
    ElInput: {
      props: ["modelValue", "placeholder", "readonly"],
      emits: ["update:modelValue"],
      template: "<input class='el-input-stub' :value='modelValue' />",
    },
    "el-date-picker": true,
    "el-option": true,
    "el-select": true,
    "el-tree-select": true,
    ElPopover: defineComponent({
      name: "ElPopover",
      props: {
        visible: {
          type: Boolean,
          default: false,
        },
      },
      emits: ["show"],
      template: "<section class='el-popover-stub'><slot name='reference' /><slot /></section>",
    }),
    Pagination: {
      emits: ["pagination", "update:page", "update:limit", "update:total"],
      template:
        "<button class='pagination-trigger' @click=\"$emit('pagination')\">pagination</button>",
    },
  },
};

const ElTableStub = defineComponent({
  props: {
    data: {
      type: Array as PropType<Record<string, unknown>[]>,
      default: () => [],
    },
  },
  emits: ["select", "select-all"],
  setup(_, { expose }) {
    const clearSelection = vi.fn();
    const toggleRowSelection = vi.fn();
    const setCurrentRow = vi.fn();
    expose({ clearSelection, toggleRowSelection, setCurrentRow });
    return {};
  },
  template:
    "<section class='el-table-stub'><button class='select-first' @click=\"$emit('select', [data[0]])\">select</button><slot /></section>",
});

function mountTableSelect(indexAction = vi.fn().mockResolvedValue({ list: pageRows, total: 2 })) {
  return mount(TableSelect, {
    props: {
      selectConfig: {
        indexAction,
        formItems: [
          {
            label: "关键字",
            prop: "keyword",
            initialValue: "admin",
          },
        ],
        tableColumns: [
          { type: "selection", width: 48 },
          { label: "名称", prop: "name" },
        ],
      },
      text: "请选择用户",
    },
    global: {
      ...globalConfig,
      stubs: {
        ...globalConfig.stubs,
        ElButton: {
          emits: ["click"],
          template: "<button @click=\"$emit('click')\"><slot /></button>",
        },
        ElForm: {
          setup(_, { expose, slots }) {
            expose({ resetFields: vi.fn() });
            return { slots };
          },
          template: "<form><slot /></form>",
        },
        ElFormItem: {
          template: "<label><slot /></label>",
        },
        ElTable: ElTableStub,
        ElTableColumn: {
          template: "<span><slot /></span>",
        },
      },
    },
  });
}

describe("TableSelect behavior", () => {
  it("loads data on first popover show and keeps later shows idempotent", async () => {
    const indexAction = vi.fn().mockResolvedValue({ list: pageRows, total: 2 });
    const wrapper = mountTableSelect(indexAction);

    await wrapper.findComponent({ name: "ElPopover" }).vm.$emit("show");
    await flushPromises();
    await wrapper.findComponent({ name: "ElPopover" }).vm.$emit("show");
    await flushPromises();

    expect(indexAction).toHaveBeenCalledTimes(1);
    expect(indexAction).toHaveBeenCalledWith(
      expect.objectContaining({ keyword: "admin", pageNum: 1, pageSize: 10 })
    );
    expect(wrapper.find(".pagination-trigger").exists()).toBe(true);
  });

  it("reloads from page one when search form submits", async () => {
    const indexAction = vi.fn().mockResolvedValue({ list: pageRows, total: 2 });
    const wrapper = mountTableSelect(indexAction);

    await wrapper.findComponent({ name: "ElPopover" }).vm.$emit("show");
    await flushPromises();
    await wrapper
      .findAll("button")
      .find((button) => button.text() === "搜索")
      ?.trigger("click");
    await flushPromises();

    expect(indexAction).toHaveBeenCalledTimes(2);
    expect(indexAction).toHaveBeenLastCalledWith(
      expect.objectContaining({ keyword: "admin", pageNum: 1, pageSize: 10 })
    );
  });

  it("emits selected rows on confirm and clears local selection", async () => {
    const wrapper = mountTableSelect();

    await wrapper.findComponent({ name: "ElPopover" }).vm.$emit("show");
    await flushPromises();
    await wrapper.find(".select-first").trigger("click");
    await nextTick();
    await wrapper
      .findAll("button")
      .find((button) => button.text() === "已选(1)")
      ?.trigger("click");

    expect(wrapper.emitted("confirmClick")?.[0]).toEqual([[pageRows[0]]]);

    await wrapper
      .findAll("button")
      .find((button) => button.text() === "清 空")
      ?.trigger("click");
    await nextTick();

    expect(wrapper.text()).toContain("确 定");
  });
});
