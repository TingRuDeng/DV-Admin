import { ref } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { usePageContentFileActions } from "@/components/CURD/usePageContentFileActions";
import { READ_XLSX_FILE_ERROR } from "@/components/CURD/pageContentExcel";
import type { IContentConfig, IObject } from "@/components/CURD/types";

const excelMocks = vi.hoisted(() => ({
  readXlsxRows: vi.fn(),
  saveXlsx: vi.fn(),
  writeXlsxBuffer: vi.fn(),
}));

vi.mock("@/components/CURD/pageContentExcel", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/components/CURD/pageContentExcel")>();
  return {
    ...actual,
    readXlsxRows: excelMocks.readXlsxRows,
    saveXlsx: excelMocks.saveXlsx,
    writeXlsxBuffer: excelMocks.writeXlsxBuffer,
  };
});

function flushPromises() {
  return Promise.resolve().then(() => Promise.resolve());
}

function createActions(contentConfig: Partial<IContentConfig> = {}) {
  const pageData = ref<IObject[]>([{ id: 1, name: "当前数据" }]);
  const selectionData = ref<IObject[]>([{ id: 2, name: "选中数据" }]);
  const getLastFormData = vi.fn(() => ({ keyword: "admin" }));
  const handleRefresh = vi.fn();
  const actions = usePageContentFileActions({
    contentConfig: {
      indexAction: vi.fn(),
      permPrefix: "system:user",
      cols: [
        { label: "姓名", prop: "name" },
        { label: "状态", prop: "status" },
      ],
      ...contentConfig,
    },
    cols: ref([
      { label: "姓名", prop: "name" },
      { label: "状态", prop: "status" },
    ]),
    pageData,
    selectionData,
    getLastFormData,
    handleRefresh,
  });

  actions.importDialogRef.value = {
    open: vi.fn(),
    close: vi.fn(),
  };

  return { actions, pageData, selectionData, getLastFormData, handleRefresh };
}

function createFile() {
  return new File(["test"], "users.xlsx");
}

function createExportResponse() {
  return {
    data: "file-data",
    headers: { "content-disposition": "attachment; filename=users.xlsx" },
  };
}

describe("usePageContentFileActions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    excelMocks.writeXlsxBuffer.mockResolvedValue("xlsx-buffer");
    excelMocks.readXlsxRows.mockResolvedValue([{ name: "张三" }]);
    vi.stubGlobal("ElMessage", {
      error: vi.fn(),
      success: vi.fn(),
    });
    vi.stubGlobal("open", vi.fn());
  });

  it("打开导出和导入弹窗", () => {
    const { actions } = createActions();

    actions.handleOpenExportsModal();
    actions.handleOpenImportModal();
    actions.handleOpenImportModal(true);

    expect(actions.exportsModalVisible.value).toBe(true);
    expect(actions.importDialogRef.value?.open).toHaveBeenNthCalledWith(1, false);
    expect(actions.importDialogRef.value?.open).toHaveBeenNthCalledWith(2, true);
  });

  it("按当前页数据执行本地导出", async () => {
    const { actions, pageData } = createActions();

    actions.handleExports({
      filename: "当前页",
      sheetname: "用户",
      fields: ["name"],
      origin: "current",
    });
    await flushPromises();

    expect(excelMocks.writeXlsxBuffer).toHaveBeenCalledWith({
      sheetname: "用户",
      columns: [{ header: "姓名", key: "name" }],
      rows: pageData.value,
    });
    expect(excelMocks.saveXlsx).toHaveBeenCalledWith("xlsx-buffer", "当前页");
  });

  it("按选中数据执行本地导出", async () => {
    const { actions, selectionData } = createActions();

    actions.handleExports({
      filename: "",
      sheetname: "",
      fields: ["status"],
      origin: "selected",
    });
    await flushPromises();

    expect(excelMocks.writeXlsxBuffer).toHaveBeenCalledWith({
      sheetname: "sheet",
      columns: [{ header: "状态", key: "status" }],
      rows: selectionData.value,
    });
    expect(excelMocks.saveXlsx).toHaveBeenCalledWith("xlsx-buffer", "system:user");
  });

  it("执行远程导出时使用最近查询参数", async () => {
    const exportsAction = vi.fn(() => Promise.resolve([{ id: 3, name: "远程数据" }]));
    const { actions, getLastFormData } = createActions({ exportsAction });

    actions.handleExports({
      filename: "远程",
      sheetname: "全部用户",
      fields: ["name"],
      origin: "remote",
    });
    await flushPromises();

    expect(exportsAction).toHaveBeenCalledWith({ keyword: "admin" });
    expect(getLastFormData).toHaveBeenCalled();
    expect(excelMocks.writeXlsxBuffer).toHaveBeenCalledWith({
      sheetname: "全部用户",
      columns: [{ header: "姓名", key: "name" }],
      rows: [{ id: 3, name: "远程数据" }],
    });
    expect(excelMocks.saveXlsx).toHaveBeenCalledWith("xlsx-buffer", "远程");
  });

  it("未配置远程导出 action 时提示错误", () => {
    const { actions } = createActions();

    actions.handleExports({
      filename: "远程",
      sheetname: "全部用户",
      fields: ["name"],
      origin: "remote",
    });

    expect(ElMessage.error).toHaveBeenCalledWith("未配置exportsAction");
  });

  it("支持字符串和函数形式的导入模板下载", async () => {
    const importTemplate = vi.fn(() => Promise.resolve(createExportResponse()));
    const stringTemplateActions = createActions({ importTemplate: "/template.xlsx" }).actions;
    const functionTemplateActions = createActions({ importTemplate }).actions;

    stringTemplateActions.handleDownloadTemplate();
    functionTemplateActions.handleDownloadTemplate();
    await flushPromises();

    expect(window.open).toHaveBeenCalledWith("/template.xlsx");
    expect(importTemplate).toHaveBeenCalled();
    expect(excelMocks.saveXlsx).toHaveBeenCalledWith("file-data", "users.xlsx");
  });

  it("单文件导入成功后关闭弹窗并刷新列表", async () => {
    const importAction = vi.fn(() => Promise.resolve());
    const { actions, handleRefresh } = createActions({ importAction });

    actions.handleImportSubmit({ file: createFile(), isFileImport: true });
    await flushPromises();

    expect(importAction).toHaveBeenCalled();
    expect(ElMessage.success).toHaveBeenCalledWith("导入数据成功");
    expect(actions.importDialogRef.value?.close).toHaveBeenCalled();
    expect(handleRefresh).toHaveBeenCalledWith(true);
  });

  it("批量导入空表时提示未解析到数据", async () => {
    excelMocks.readXlsxRows.mockResolvedValue([]);
    const importsAction = vi.fn(() => Promise.resolve());
    const { actions } = createActions({ importsAction });

    actions.handleImportSubmit({ file: createFile(), isFileImport: false });
    await flushPromises();

    expect(importsAction).not.toHaveBeenCalled();
    expect(ElMessage.error).toHaveBeenCalledWith("未解析到数据");
  });

  it("批量导入读取失败时提示读取文件失败", async () => {
    excelMocks.readXlsxRows.mockRejectedValue(new Error(READ_XLSX_FILE_ERROR));
    const { actions } = createActions({ importsAction: vi.fn() });

    actions.handleImportSubmit({ file: createFile(), isFileImport: false });
    await flushPromises();

    expect(ElMessage.error).toHaveBeenCalledWith("读取文件失败");
  });

  it("公开导出方法使用后端响应文件名保存", async () => {
    const exportAction = vi.fn(() => Promise.resolve(createExportResponse()));
    const { actions } = createActions({ exportAction });

    actions.exportPageData({ status: "enabled" });
    await flushPromises();

    expect(exportAction).toHaveBeenCalledWith({ status: "enabled" });
    expect(excelMocks.saveXlsx).toHaveBeenCalledWith("file-data", "users.xlsx");
  });
});
