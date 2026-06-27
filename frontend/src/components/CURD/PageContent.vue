<template>
  <div
    class="rounded bg-[var(--el-bg-color)] border border-[var(--el-border-color)] p-5 h-full md:flex flex-1 flex-col md:overflow-auto"
  >
    <PageContentToolbar
      :toolbar-left-btn="toolbarLeftBtn"
      :toolbar-right-btn="toolbarRightBtn"
      :cols="cols"
      :disable-delete="removeIds.length === 0"
      @toolbar="handleToolbar"
      @column-show-change="handleColumnShowChange"
    />

    <!-- 列表 -->
    <el-table
      ref="tableRef"
      v-loading="loading"
      v-bind="contentConfig.table"
      :data="pageData"
      :row-key="pk"
      class="flex-1"
      @selection-change="handleSelectionChange"
      @filter-change="handleFilterChange"
    >
      <template v-for="col in cols" :key="col.prop">
        <el-table-column v-if="col.show" v-bind="col">
          <template #default="scope">
            <!-- 自定义 -->
            <template v-if="col.templet === 'custom'">
              <slot :name="col.slotName ?? col.prop" :prop="col.prop" v-bind="scope" />
            </template>
            <PageContentTableCell
              v-else
              :col="col"
              :row="scope.row"
              :column="scope.column"
              :row-index="scope.$index"
              :page-data-length="pageData.length"
              :table-toolbar-btn="tableToolbarBtn"
              :has-button-perm="hasButtonPerm"
              @modify="handleModify"
              @operate="handleOperate"
            />
          </template>
        </el-table-column>
      </template>
    </el-table>

    <!-- 分页 -->
    <div v-if="showPagination" class="mt-4">
      <el-scrollbar :class="['h-8!', { 'flex-x-end': contentConfig?.pagePosition === 'right' }]">
        <el-pagination
          v-bind="pagination"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </el-scrollbar>
    </div>

    <PageContentExportDialog
      v-model="exportsModalVisible"
      :cols="cols"
      :selection-count="selectionData.length"
      :has-remote-action="contentConfig.exportsAction !== undefined"
      @submit="handleExports"
    />

    <PageContentImportDialog
      ref="importDialogRef"
      v-model="importModalVisible"
      :has-import-template="contentConfig.importTemplate !== undefined"
      @submit="handleImportSubmit"
      @download-template="handleDownloadTemplate"
    />
  </div>
</template>

<script setup lang="ts">
import PageContentExportDialog from "@/components/CURD/PageContentExportDialog.vue";
import PageContentImportDialog from "@/components/CURD/PageContentImportDialog.vue";
import PageContentTableCell from "@/components/CURD/PageContentTableCell.vue";
import PageContentToolbar from "@/components/CURD/PageContentToolbar.vue";
import {
  READ_XLSX_FILE_ERROR,
  readXlsxRows,
  saveXlsx,
  writeXlsxBuffer,
  type PageContentExcelColumn,
} from "@/components/CURD/pageContentExcel";
import { usePageContentData } from "@/components/CURD/usePageContentData";
import { usePageContentFilters } from "@/components/CURD/usePageContentFilters";
import { usePageContentToolbarConfig } from "@/components/CURD/usePageContentToolbarConfig";
import type { TableInstance } from "element-plus";
import { ref } from "vue";
import { createLogger } from "@/utils/logger";
import type { IContentConfig, IObject, IOperateData } from "./types";
import type { PageContentExportPayload } from "@/components/CURD/PageContentExportDialog.vue";
import type { PageContentImportPayload } from "@/components/CURD/PageContentImportDialog.vue";

const pageContentLogger = createLogger("PageContent");

// 定义接收的属性
const props = defineProps<{ contentConfig: IContentConfig }>();
// 定义自定义事件
const emit = defineEmits<{
  addClick: [];
  exportClick: [];
  searchClick: [];
  toolbarClick: [name: string];
  editClick: [row: IObject];
  filterChange: [data: IObject];
  operateClick: [data: IOperateData];
}>();

// 主键
const pk = props.contentConfig.pk ?? "id";
const { toolbarLeftBtn, toolbarRightBtn, tableToolbarBtn, hasButtonPerm } =
  usePageContentToolbarConfig(props.contentConfig);

// 表格列
const cols = ref(
  props.contentConfig.cols.map((col) => {
    if (col.initFn) {
      col.initFn(col);
    }
    if (col.show === undefined) {
      col.show = true;
    }
    if (col.prop !== undefined && col.columnKey === undefined && col["column-key"] === undefined) {
      col.columnKey = col.prop;
    }
    if (
      col.type === "selection" &&
      col.reserveSelection === undefined &&
      col["reserve-selection"] === undefined
    ) {
      // 配合表格row-key实现跨页多选
      col.reserveSelection = true;
    }
    return col;
  })
);
function handleColumnShowChange(col: IContentConfig["cols"][number], show: boolean) {
  col.show = show;
}
const {
  loading,
  pageData,
  showPagination,
  pagination,
  fetchPageData,
  getLastFormData,
  handleRefresh,
  handleSizeChange,
  handleCurrentChange,
} = usePageContentData(props.contentConfig);
const { handleFilterChange, getFilterParams } = usePageContentFilters(cols.value, (data) => {
  emit("filterChange", data);
});

const tableRef = ref<TableInstance>();

// 行选中
const selectionData = ref<IObject[]>([]);
// 删除ID集合 用于批量删除
const removeIds = ref<(number | string)[]>([]);
function handleSelectionChange(selection: any[]) {
  selectionData.value = selection;
  removeIds.value = selection.map((item) => item[pk]);
}

// 获取行选中
function getSelectionData() {
  return selectionData.value;
}

// 删除
function handleDelete(id?: number | string) {
  const ids = [id || removeIds.value].join(",");
  if (!ids) {
    ElMessage.warning("请勾选删除项");
    return;
  }

  ElMessageBox.confirm("确认删除?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(function () {
      if (props.contentConfig.deleteAction) {
        props.contentConfig
          .deleteAction(ids)
          .then(() => {
            ElMessage.success("删除成功");
            removeIds.value = [];
            //清空选中项
            tableRef.value?.clearSelection();
            handleRefresh(true);
          })
          .catch(() => {});
      } else {
        ElMessage.error("未配置deleteAction");
      }
    })
    .catch(() => {});
}

const exportsModalVisible = ref(false);
// 打开导出弹窗
function handleOpenExportsModal() {
  exportsModalVisible.value = true;
}
// 导出
function handleExports(exportData: PageContentExportPayload) {
  const filename = exportData.filename
    ? exportData.filename
    : props.contentConfig.permPrefix || "export";
  const sheetname = exportData.sheetname ? exportData.sheetname : "sheet";
  const columns: PageContentExcelColumn[] = [];
  cols.value.forEach((col) => {
    if (col.label && col.prop && exportData.fields.includes(col.prop)) {
      columns.push({ header: col.label, key: col.prop });
    }
  });
  if (exportData.origin === "remote") {
    if (props.contentConfig.exportsAction) {
      props.contentConfig.exportsAction(getLastFormData()).then((res) => {
        writeXlsxBuffer({ sheetname, columns, rows: res })
          .then((buffer) => {
            saveXlsx(buffer, filename as string);
          })
          .catch((error) => pageContentLogger.error("远程导出文件生成失败:", error));
      });
    } else {
      ElMessage.error("未配置exportsAction");
    }
  } else {
    writeXlsxBuffer({
      sheetname,
      columns,
      rows: exportData.origin === "selected" ? selectionData.value : pageData.value,
    })
      .then((buffer) => {
        saveXlsx(buffer, filename as string);
      })
      .catch((error) => pageContentLogger.error("本地导出文件生成失败:", error));
  }
}

const importModalVisible = ref(false);
const importDialogRef = ref<InstanceType<typeof PageContentImportDialog>>();
// 打开导入弹窗
function handleOpenImportModal(isFile: boolean = false) {
  importDialogRef.value?.open(isFile);
}
// 下载导入模板
function handleDownloadTemplate() {
  const importTemplate = props.contentConfig.importTemplate;
  if (typeof importTemplate === "string") {
    window.open(importTemplate);
  } else if (typeof importTemplate === "function") {
    importTemplate().then((response) => {
      const fileData = response.data;
      const fileName = decodeURI(
        response.headers["content-disposition"].split(";")[1].split("=")[1]
      );
      saveXlsx(fileData, fileName);
    });
  } else {
    ElMessage.error("未配置importTemplate");
  }
}
// 导入确认
function handleImportSubmit(importData: PageContentImportPayload) {
  if (importData.isFileImport) {
    handleImport(importData.file);
    return;
  }
  handleImports(importData.file);
}
// 文件导入
function handleImport(file: File) {
  const importAction = props.contentConfig.importAction;
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
// 导入
function handleImports(file: File) {
  const importsAction = props.contentConfig.importsAction;
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

// 操作栏
function handleToolbar(name: string) {
  switch (name) {
    case "refresh":
      handleRefresh();
      break;
    case "exports":
      handleOpenExportsModal();
      break;
    case "imports":
      handleOpenImportModal();
      break;
    case "search":
      emit("searchClick");
      break;
    case "add":
      emit("addClick");
      break;
    case "delete":
      handleDelete();
      break;
    case "import":
      handleOpenImportModal(true);
      break;
    case "export":
      emit("exportClick");
      break;
    default:
      emit("toolbarClick", name);
      break;
  }
}

// 操作列
function handleOperate(data: IOperateData) {
  switch (data.name) {
    case "delete":
      if (props.contentConfig?.deleteAction) {
        handleDelete(data.row[pk]);
      } else {
        emit("operateClick", data);
      }
      break;
    default:
      emit("operateClick", data);
      break;
  }
}

// 属性修改
function handleModify(field: string, value: boolean | string | number, row: Record<string, any>) {
  if (props.contentConfig.modifyAction) {
    props.contentConfig.modifyAction({
      [pk]: row[pk],
      field,
      value,
    });
  } else {
    ElMessage.error("未配置modifyAction");
  }
}

fetchPageData();

// 导出Excel
function exportPageData(formData: IObject = {}) {
  if (props.contentConfig.exportAction) {
    props.contentConfig.exportAction(formData).then((response) => {
      const fileData = response.data;
      const fileName = decodeURI(
        response.headers["content-disposition"].split(";")[1].split("=")[1]
      );
      saveXlsx(fileData, fileName);
    });
  } else {
    ElMessage.error("未配置exportAction");
  }
}

// 暴露的属性和方法
defineExpose({ fetchPageData, exportPageData, getFilterParams, getSelectionData, handleRefresh });
</script>
