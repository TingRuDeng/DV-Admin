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
import { usePageContentData } from "@/components/CURD/usePageContentData";
import { usePageContentFileActions } from "@/components/CURD/usePageContentFileActions";
import { usePageContentFilters } from "@/components/CURD/usePageContentFilters";
import { usePageContentTableActions } from "@/components/CURD/usePageContentTableActions";
import { usePageContentToolbarConfig } from "@/components/CURD/usePageContentToolbarConfig";
import type { TableInstance } from "element-plus";
import { ref } from "vue";
import type { IContentConfig, IObject, IOperateData } from "./types";

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
const {
  selectionData,
  removeIds,
  getSelectionData,
  handleSelectionChange,
  handleDelete,
  handleOperate,
  handleModify,
} = usePageContentTableActions({
  contentConfig: props.contentConfig,
  pk,
  handleRefresh,
  clearSelection: () => tableRef.value?.clearSelection(),
  emitOperateClick: (data) => emit("operateClick", data),
});
const {
  exportsModalVisible,
  importModalVisible,
  importDialogRef,
  handleOpenExportsModal,
  handleOpenImportModal,
  handleExports,
  handleDownloadTemplate,
  handleImportSubmit,
  exportPageData,
} = usePageContentFileActions({
  contentConfig: props.contentConfig,
  cols,
  pageData,
  selectionData,
  getLastFormData,
  handleRefresh,
});

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

fetchPageData();

// 暴露的属性和方法
defineExpose({ fetchPageData, exportPageData, getFilterParams, getSelectionData, handleRefresh });
</script>
