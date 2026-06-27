import { describe, expect, it, vi, beforeEach } from "vitest";
import { usePageContentTableActions } from "@/components/CURD/usePageContentTableActions";
import type { IContentConfig, IOperateData } from "@/components/CURD/types";

function createActions(contentConfig: Partial<IContentConfig> = {}) {
  const handleRefresh = vi.fn();
  const clearSelection = vi.fn();
  const emitOperateClick = vi.fn();
  const actions = usePageContentTableActions({
    contentConfig: {
      indexAction: vi.fn(),
      cols: [],
      ...contentConfig,
    },
    pk: "id",
    handleRefresh,
    clearSelection,
    emitOperateClick,
  });

  return { actions, handleRefresh, clearSelection, emitOperateClick };
}

function createOperateData(name: string, row = { id: 7 }): IOperateData {
  return {
    name,
    row,
    column: {},
    $index: 0,
  };
}

describe("usePageContentTableActions", () => {
  beforeEach(() => {
    vi.stubGlobal("ElMessage", {
      warning: vi.fn(),
      error: vi.fn(),
      success: vi.fn(),
    });
    vi.stubGlobal("ElMessageBox", {
      confirm: vi.fn(() => Promise.resolve()),
    });
  });

  it("同步表格选择数据和批量删除 ID", () => {
    const { actions } = createActions();
    const rows = [
      { id: 1, name: "张三" },
      { id: 2, name: "李四" },
    ];

    actions.handleSelectionChange(rows);

    expect(actions.selectionData.value).toEqual(rows);
    expect(actions.getSelectionData()).toEqual(rows);
    expect(actions.removeIds.value).toEqual([1, 2]);
  });

  it("批量删除确认成功后调用 deleteAction 并刷新列表", async () => {
    const deleteAction = vi.fn(() => Promise.resolve());
    const { actions, clearSelection, handleRefresh } = createActions({ deleteAction });

    actions.handleSelectionChange([{ id: 1 }, { id: 2 }]);
    actions.handleDelete();
    await Promise.resolve();
    await Promise.resolve();

    expect(ElMessageBox.confirm).toHaveBeenCalledWith("确认删除?", "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    expect(deleteAction).toHaveBeenCalledWith("1,2");
    expect(ElMessage.success).toHaveBeenCalledWith("删除成功");
    expect(actions.removeIds.value).toEqual([]);
    expect(clearSelection).toHaveBeenCalled();
    expect(handleRefresh).toHaveBeenCalledWith(true);
  });

  it("未选择数据时提示勾选删除项", () => {
    const { actions } = createActions({ deleteAction: vi.fn() });

    actions.handleDelete();

    expect(ElMessage.warning).toHaveBeenCalledWith("请勾选删除项");
    expect(ElMessageBox.confirm).not.toHaveBeenCalled();
  });

  it("指定行删除优先使用行主键", async () => {
    const deleteAction = vi.fn(() => Promise.resolve());
    const { actions } = createActions({ deleteAction });

    actions.handleSelectionChange([{ id: 1 }, { id: 2 }]);
    actions.handleDelete(9);
    await Promise.resolve();
    await Promise.resolve();

    expect(deleteAction).toHaveBeenCalledWith("9");
  });

  it("删除 action 未配置时保留确认后错误提示", async () => {
    const { actions } = createActions();

    actions.handleSelectionChange([{ id: 1 }]);
    actions.handleDelete();
    await Promise.resolve();

    expect(ElMessage.error).toHaveBeenCalledWith("未配置deleteAction");
  });

  it("操作列删除在已配置 deleteAction 时走内部删除流程", () => {
    const deleteAction = vi.fn(() => Promise.resolve());
    const { actions, emitOperateClick } = createActions({ deleteAction });

    actions.handleOperate(createOperateData("delete", { id: 12 }));

    expect(ElMessageBox.confirm).toHaveBeenCalled();
    expect(emitOperateClick).not.toHaveBeenCalled();
  });

  it("非内置操作列动作向外透传", () => {
    const { actions, emitOperateClick } = createActions();
    const data = createOperateData("detail");

    actions.handleOperate(data);

    expect(emitOperateClick).toHaveBeenCalledWith(data);
  });

  it("行内修改调用 modifyAction", () => {
    const modifyAction = vi.fn(() => Promise.resolve());
    const { actions } = createActions({ modifyAction });

    actions.handleModify("status", true, { id: 5 });

    expect(modifyAction).toHaveBeenCalledWith({
      id: 5,
      field: "status",
      value: true,
    });
  });

  it("未配置 modifyAction 时提示错误", () => {
    const { actions } = createActions();

    actions.handleModify("status", false, { id: 5 });

    expect(ElMessage.error).toHaveBeenCalledWith("未配置modifyAction");
  });
});
