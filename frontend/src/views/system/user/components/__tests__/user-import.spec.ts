import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { defineComponent, h, type PropType } from "vue";
import { ElMessage } from "element-plus";
import UserAPI from "@/api/system/user-api";
import UserImport from "../UserImport.vue";

vi.mock("@/api/system/user-api", () => ({ default: { import: vi.fn() } }));
vi.mock("element-plus", () => ({
  ElMessage: { success: vi.fn(), warning: vi.fn(), error: vi.fn() },
}));
vi.mock("@/utils/logger", () => ({ createLogger: () => ({ error: vi.fn() }) }));

const file = new File(["test workbook"], "users.xlsx");
/* eslint-disable vue/one-component-per-file -- Local UI stubs keep the component behavior test self-contained. */
const Drawer = defineComponent({
  props: { modelValue: Boolean, loading: Boolean },
  emits: ["submit", "close"],
  setup(props, { slots, emit, expose }) {
    expose({ resetFields: () => {}, clearValidate: () => {} });
    return () =>
      h("section", { "aria-busy": props.loading }, [
        slots.default?.(),
        slots.footer?.({ submit: () => emit("submit"), cancel: () => emit("close") }),
      ]);
  },
});
const Dialog = defineComponent({
  props: { modelValue: Boolean },
  emits: ["update:modelValue"],
  setup(props, { slots, emit }) {
    return () =>
      props.modelValue
        ? h("section", { role: "dialog" }, [
            slots.default?.(),
            slots.footer?.({ cancel: () => emit("update:modelValue", false) }),
          ])
        : null;
  },
});
const Upload = defineComponent({
  emits: ["update:fileList"],
  setup(_, { emit }) {
    return () =>
      h(
        "button",
        {
          onClick: () => emit("update:fileList", [{ name: file.name, raw: file }]),
        },
        "选择文件"
      );
  },
});
const Alert = defineComponent({
  props: { title: { type: String, default: "" } },
  setup: (props) => () => h("p", props.title),
});
const Table = defineComponent({
  props: { data: { type: Array as PropType<string[]>, default: () => [] } },
  setup: (props) => () =>
    h(
      "ul",
      props.data.map((message: string) => h("li", message))
    ),
});
/* eslint-enable vue/one-component-per-file */

function renderImport() {
  return mount(UserImport, {
    props: { modelValue: true, deptId: "42" },
    global: {
      stubs: {
        ProFormDrawer: Drawer,
        ProDialog: Dialog,
        ElUpload: Upload,
        ElAlert: Alert,
        ElTable: Table,
        ElTableColumn: true,
        ElFormItem: { template: "<div><slot /></div>" },
        ElButton: { template: "<button><slot /></button>" },
        ElIcon: true,
        UploadFilled: true,
        ElLink: true,
      },
    },
  });
}

let wrapper: ReturnType<typeof renderImport>;
async function submit() {
  await wrapper.get("button").trigger("click");
  const confirm = wrapper.findAll("button").find((button) => button.text() === "确 定");
  await confirm!.trigger("click");
  await flushPromises();
}

beforeEach(() => {
  vi.clearAllMocks();
  wrapper = renderImport();
});
afterEach(() => wrapper.unmount());

describe("用户导入结果反馈", () => {
  it("全部成功时刷新一次并关闭导入抽屉", async () => {
    vi.mocked(UserAPI.import).mockResolvedValue({
      validCount: 2,
      invalidCount: 0,
      messageList: [],
    });
    await submit();
    expect(UserAPI.import).toHaveBeenCalledWith("42", file);
    expect(ElMessage.success).toHaveBeenCalledWith("导入成功，导入数据：2条");
    expect(wrapper.emitted("import-success")).toHaveLength(1);
    expect(wrapper.emitted("update:modelValue")).toEqual([[false]]);
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
  });

  it("部分成功时警告并刷新一次，保留失败明细", async () => {
    vi.mocked(UserAPI.import).mockResolvedValue({
      validCount: 1,
      invalidCount: 1,
      messageList: ["第3行：用户名已存在"],
    });
    await submit();
    expect(ElMessage.warning).toHaveBeenCalledWith("部分导入成功：成功1条，失败1条");
    expect(ElMessage.error).not.toHaveBeenCalled();
    expect(wrapper.emitted("import-success")).toHaveLength(1);
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
    expect(wrapper.get('[role="dialog"]').text()).toContain("成功1条，失败1条");
    expect(wrapper.get('[role="dialog"]').text()).toContain("第3行：用户名已存在");
    await wrapper.get('[role="dialog"] button').trigger("click");
    await wrapper
      .findAll("button")
      .find((button) => button.text() === "错误信息")!
      .trigger("click");
    expect(wrapper.get('[role="dialog"]').text()).toContain("第3行：用户名已存在");
    expect(wrapper.emitted("import-success")).toHaveLength(1);
  });

  it("全部失败时显示失败结果且不刷新", async () => {
    vi.mocked(UserAPI.import).mockResolvedValue({
      validCount: 0,
      invalidCount: 2,
      messageList: ["第2行：无权限", "第3行：用户名已存在"],
    });
    await submit();
    expect(ElMessage.error).toHaveBeenCalledWith("导入失败：成功0条，失败2条");
    expect(wrapper.emitted("import-success")).toBeUndefined();
    expect(wrapper.get('[role="dialog"]').text()).toContain("第2行：无权限");
    expect(wrapper.get('[role="dialog"]').text()).toContain("第3行：用户名已存在");
  });

  it("零条记录提示没有数据且不刷新或关闭", async () => {
    vi.mocked(UserAPI.import).mockResolvedValue({
      validCount: 0,
      invalidCount: 0,
      messageList: [],
    });
    await submit();
    expect(ElMessage.warning).toHaveBeenCalledWith("未导入任何数据，请检查文件内容");
    expect(ElMessage.success).not.toHaveBeenCalled();
    expect(wrapper.emitted("import-success")).toBeUndefined();
    expect(wrapper.emitted("update:modelValue")).toBeUndefined();
  });

  it("请求异常不触发刷新或伪造结果", async () => {
    vi.mocked(UserAPI.import).mockRejectedValue(new Error("网络异常"));
    await submit();
    expect(ElMessage.error).toHaveBeenCalledWith("上传失败：网络异常");
    expect(wrapper.emitted("import-success")).toBeUndefined();
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
    expect(wrapper.get("section").attributes("aria-busy")).toBe("false");
  });

  it("再次提交遇到异常时不残留上一次失败明细，也不重复刷新", async () => {
    vi.mocked(UserAPI.import)
      .mockResolvedValueOnce({ validCount: 1, invalidCount: 1, messageList: ["上次失败行"] })
      .mockRejectedValueOnce(new Error("网络异常"));
    await submit();
    await wrapper.get('[role="dialog"] button').trigger("click");
    await submit();
    expect(wrapper.emitted("import-success")).toHaveLength(1);
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
    expect(wrapper.text()).not.toContain("错误信息");
    expect(ElMessage.error).toHaveBeenCalledWith("上传失败：网络异常");
  });
});
