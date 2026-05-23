<template>
  <el-table
    ref="tableRef"
    v-loading="loading"
    :data="pageData"
    :border="true"
    :max-height="250"
    :row-key="pk"
    :highlight-current-row="true"
    :class="{ radio: !isMultiple }"
    @select="handleSelect"
    @select-all="handleSelectAll"
  >
    <template v-for="col in tableColumns" :key="col.prop">
      <el-table-column v-if="col.templet === 'custom'" v-bind="col">
        <template #default="scope">
          <slot :name="col.slotName ?? col.prop" :prop="col.prop" v-bind="scope" />
        </template>
      </el-table-column>
      <el-table-column v-else v-bind="col" />
    </template>
  </el-table>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import type { TableInstance } from "element-plus";
import type { TableSelectColumn, TableSelectRecord } from "./types";

const props = defineProps<{
  loading: boolean;
  pageData: TableSelectRecord[];
  pk: string;
  isMultiple: boolean;
  tableColumns: TableSelectColumn[];
}>();

const emit = defineEmits<{
  selectionChange: [selection: TableSelectRecord[]];
}>();

const tableRef = ref<TableInstance>();

function handleSelect(selection: TableSelectRecord[]) {
  if (props.isMultiple || selection.length === 0) {
    emit("selectionChange", selection);
    return;
  }

  const selectedItem = selection[selection.length - 1];
  const nextSelection = selectedItem ? [selectedItem] : [];
  tableRef.value?.clearSelection();
  if (selectedItem) {
    tableRef.value?.toggleRowSelection(selectedItem, true);
    tableRef.value?.setCurrentRow(selectedItem);
  }
  emit("selectionChange", nextSelection);
}

function handleSelectAll(selection: TableSelectRecord[]) {
  if (props.isMultiple) {
    emit("selectionChange", selection);
  }
}

function clearSelection() {
  tableRef.value?.clearSelection();
}

defineExpose({
  clearSelection,
});
</script>

<style scoped lang="scss">
// 单选模式借用 selection 列实现，隐藏表头全选入口避免误导用户。
.radio :deep(.el-table__header th.el-table__cell:nth-child(1) .el-checkbox) {
  visibility: hidden;
}
</style>
