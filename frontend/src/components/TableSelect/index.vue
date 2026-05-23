<template>
  <div ref="tableSelectRef" :style="'width:' + width">
    <el-popover
      :visible="popoverVisible"
      :width="popoverWidth"
      placement="bottom-end"
      v-bind="selectConfig.popover"
      @show="handleShow"
    >
      <template #reference>
        <div @click="popoverVisible = !popoverVisible">
          <slot>
            <el-input
              class="reference"
              :model-value="text"
              :readonly="true"
              :placeholder="placeholder"
            >
              <template #suffix>
                <el-icon
                  :style="{
                    transform: popoverVisible ? 'rotate(180deg)' : 'rotate(0)',
                    transition: 'transform .5s',
                  }"
                >
                  <ArrowDown />
                </el-icon>
              </template>
            </el-input>
          </slot>
        </div>
      </template>
      <div ref="popoverContentRef">
        <TableSelectSearchForm
          :form-items="selectConfig.formItems"
          :query-params="queryParams"
          @query="handleQuery"
          @reset="handleReset"
        />
        <TableSelectDataTable
          ref="dataTableRef"
          :loading="loading"
          :page-data="pageData"
          :pk="pk"
          :is-multiple="isMultiple"
          :table-columns="tableColumns"
          @selection-change="handleSelectionChange"
        >
          <template v-for="col in customColumns" :key="col.prop" #[col.slotName??col.prop]="scope">
            <slot :name="col.slotName ?? col.prop" :prop="col.prop" v-bind="scope" />
          </template>
        </TableSelectDataTable>
        <pagination
          v-if="total > 0"
          v-model:total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="handlePagination"
        />
        <TableSelectFooter
          :confirm-text="confirmText"
          @confirm="handleConfirm"
          @clear="handleClear"
          @close="handleClose"
        />
      </div>
    </el-popover>
  </div>
</template>

<script lang="ts" setup>
import { computed, reactive, ref } from "vue";
import { useResizeObserver } from "@vueuse/core";
import TableSelectDataTable from "./TableSelectDataTable.vue";
import TableSelectFooter from "./TableSelectFooter.vue";
import TableSelectSearchForm from "./TableSelectSearchForm.vue";
import type {
  ISelectConfig,
  TableSelectColumn,
  TableSelectQueryParams,
  TableSelectRecord,
} from "./types";

const DEFAULT_PAGE_SIZE = 10;

const props = withDefaults(
  defineProps<{
    selectConfig: ISelectConfig;
    text?: string;
  }>(),
  {
    text: "",
  }
);

const emit = defineEmits<{
  confirmClick: [selection: TableSelectRecord[]];
}>();

const pk = props.selectConfig.pk ?? "id";
const isMultiple = props.selectConfig.multiple === true;
const width = props.selectConfig.width ?? "100%";
const placeholder = props.selectConfig.placeholder ?? "请选择";
const popoverVisible = ref(false);
const loading = ref(false);
const total = ref(0);
const pageData = ref<TableSelectRecord[]>([]);
const selectedItems = ref<TableSelectRecord[]>([]);
const isInit = ref(false);
const tableSelectRef = ref<HTMLElement>();
const popoverContentRef = ref<HTMLElement>();
const dataTableRef = ref<InstanceType<typeof TableSelectDataTable>>();
const popoverWidth = ref(width);
const queryParams = reactive<TableSelectQueryParams>({
  pageNum: 1,
  pageSize: DEFAULT_PAGE_SIZE,
});

for (const item of props.selectConfig.formItems) {
  queryParams[item.prop] = item.initialValue ?? "";
}

const tableColumns = computed<TableSelectColumn[]>(() => {
  return props.selectConfig.tableColumns.map((item) => {
    if (item.type === "selection") {
      return { ...item, reserveSelection: true };
    }
    return { ...item };
  });
});

const customColumns = computed(() => {
  return tableColumns.value.filter((item) => item.templet === "custom");
});

const confirmText = computed(() => {
  return selectedItems.value.length > 0 ? `已选(${selectedItems.value.length})` : "确 定";
});

useResizeObserver(tableSelectRef, (entries) => {
  popoverWidth.value = `${entries[0].contentRect.width}px`;
});

function handleReset() {
  fetchPageData(true);
}

function handleQuery() {
  fetchPageData(true);
}

function fetchPageData(isRestart = false) {
  loading.value = true;
  if (isRestart) {
    queryParams.pageNum = 1;
    queryParams.pageSize = DEFAULT_PAGE_SIZE;
  }
  props.selectConfig
    .indexAction(queryParams)
    .then((data) => {
      total.value = data.total;
      pageData.value = data.list;
    })
    .finally(() => {
      loading.value = false;
    });
}

function handleSelectionChange(selection: TableSelectRecord[]) {
  selectedItems.value = selection;
}

function handlePagination() {
  fetchPageData();
}

function handleShow() {
  if (isInit.value === false) {
    isInit.value = true;
    fetchPageData();
  }
}

function handleConfirm() {
  if (selectedItems.value.length === 0) {
    ElMessage.error("请选择数据");
    return;
  }
  popoverVisible.value = false;
  emit("confirmClick", selectedItems.value);
}

function handleClear() {
  dataTableRef.value?.clearSelection();
  selectedItems.value = [];
}

function handleClose() {
  popoverVisible.value = false;
}
</script>

<style scoped lang="scss">
.reference :deep(.el-input__wrapper),
.reference :deep(.el-input__inner) {
  cursor: pointer;
}
</style>
