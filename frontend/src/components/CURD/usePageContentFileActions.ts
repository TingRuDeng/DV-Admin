import {
  READ_XLSX_FILE_ERROR,
  readXlsxRows,
  saveXlsx,
  writeXlsxBuffer,
  type PageContentExcelColumn,
} from "@/components/CURD/pageContentExcel";
import { createLogger } from "@/utils/logger";
import { ref, shallowRef, type Ref } from "vue";
import type { PageContentExportPayload } from "@/components/CURD/PageContentExportDialog.vue";
import type { PageContentImportPayload } from "@/components/CURD/PageContentImportDialog.vue";
import type { IContentConfig, IObject } from "./types";

interface PageContentImportDialogController {
  open: (isFile?: boolean) => void;
  close: () => void;
}

interface UsePageContentFileActionsOptions {
  contentConfig: IContentConfig;
  cols: Ref<IContentConfig["cols"]>;
  pageData: Ref<IObject[]>;
  selectionData: Ref<IObject[]>;
  getLastFormData: () => IObject;
  handleRefresh: (isRestart?: boolean) => void;
}

const pageContentLogger = createLogger("PageContent");

export function usePageContentFileActions(options: UsePageContentFileActionsOptions) {
  const { contentConfig, cols, pageData, selectionData, getLastFormData, handleRefresh } = options;
  const exportsModalVisible = shallowRef(false);
  const importModalVisible = shallowRef(false);
  const importDialogRef = ref<PageContentImportDialogController>();

  function handleOpenExportsModal() {
    exportsModalVisible.value = true;
  }

  function handleOpenImportModal(isFile = false) {
    importDialogRef.value?.open(isFile);
  }

  function handleExports(exportData: PageContentExportPayload) {
    const filename = exportData.filename
      ? exportData.filename
      : contentConfig.permPrefix || "export";
    const sheetname = exportData.sheetname ? exportData.sheetname : "sheet";
    const columns = buildExportColumns(exportData.fields);
    if (exportData.origin === "remote") {
      handleRemoteExport({ filename, sheetname, columns });
      return;
    }

    writeXlsxBuffer({
      sheetname,
      columns,
      rows: exportData.origin === "selected" ? selectionData.value : pageData.value,
    })
      .then((buffer) => {
        saveXlsx(buffer, filename);
      })
      .catch((error) => pageContentLogger.error("本地导出文件生成失败:", error));
  }

  function handleDownloadTemplate() {
    const importTemplate = contentConfig.importTemplate;
    if (typeof importTemplate === "string") {
      window.open(importTemplate);
      return;
    }
    if (typeof importTemplate === "function") {
      importTemplate().then((response) => {
        saveResponseFile(response);
      });
      return;
    }
    ElMessage.error("未配置importTemplate");
  }

  function handleImportSubmit(importData: PageContentImportPayload) {
    if (importData.isFileImport) {
      handleImport(importData.file);
      return;
    }
    handleImports(importData.file);
  }

  function exportPageData(formData: IObject = {}) {
    if (!contentConfig.exportAction) {
      ElMessage.error("未配置exportAction");
      return;
    }
    contentConfig.exportAction(formData).then((response) => {
      saveResponseFile(response);
    });
  }

  function buildExportColumns(fields: string[]) {
    const columns: PageContentExcelColumn[] = [];
    cols.value.forEach((col) => {
      if (col.label && col.prop && fields.includes(col.prop)) {
        columns.push({ header: col.label, key: col.prop });
      }
    });
    return columns;
  }

  function handleRemoteExport(options: {
    filename: string;
    sheetname: string;
    columns: PageContentExcelColumn[];
  }) {
    if (!contentConfig.exportsAction) {
      ElMessage.error("未配置exportsAction");
      return;
    }

    contentConfig.exportsAction(getLastFormData()).then((res) => {
      writeXlsxBuffer({ sheetname: options.sheetname, columns: options.columns, rows: res })
        .then((buffer) => {
          saveXlsx(buffer, options.filename);
        })
        .catch((error) => pageContentLogger.error("远程导出文件生成失败:", error));
    });
  }

  function handleImport(file: File) {
    const importAction = contentConfig.importAction;
    if (importAction === undefined) {
      ElMessage.error("未配置importAction");
      return;
    }
    importAction(file).then(() => {
      ElMessage.success("导入数据成功");
      importDialogRef.value?.close();
      handleRefresh(true);
    });
  }

  function handleImports(file: File) {
    const importsAction = contentConfig.importsAction;
    if (importsAction === undefined) {
      ElMessage.error("未配置importsAction");
      return;
    }
    readXlsxRows(file)
      .then((data) => {
        if (data.length === 0) {
          ElMessage.error("未解析到数据");
          return;
        }
        importsAction(data).then(() => {
          ElMessage.success("导入数据成功");
          importDialogRef.value?.close();
          handleRefresh(true);
        });
      })
      .catch((error) => {
        if (error instanceof Error && error.message === READ_XLSX_FILE_ERROR) {
          ElMessage.error("读取文件失败");
          return;
        }
        pageContentLogger.error("导入文件解析失败:", error);
      });
  }

  function saveResponseFile(response: { data: BlobPart; headers: Record<string, string> }) {
    const fileName = decodeURI(response.headers["content-disposition"].split(";")[1].split("=")[1]);
    saveXlsx(response.data, fileName);
  }

  return {
    exportsModalVisible,
    importModalVisible,
    importDialogRef,
    handleOpenExportsModal,
    handleOpenImportModal,
    handleExports,
    handleDownloadTemplate,
    handleImportSubmit,
    exportPageData,
  };
}
