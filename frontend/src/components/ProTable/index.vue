<template>
  <DataPanel :title="title">
    <template v-if="$slots.actions" #actions>
      <slot name="actions" />
    </template>

    <div class="ff-table-wrap">
      <el-table
        v-loading="loading"
        :data="data"
        :row-key="rowKey"
        highlight-current-row
        class="ff-table"
        v-bind="$attrs"
        @selection-change="handleSelectionChange"
      >
        <slot />
      </el-table>
    </div>

    <template #footer>
      <slot name="footer">
        <Pagination
          v-if="showPagination && total > 0"
          v-model:page="pageProxy"
          v-model:limit="limitProxy"
          :total="totalProxy"
          class="mt-4"
          @pagination="handlePagination"
        />
      </slot>
    </template>
  </DataPanel>
</template>

<script setup lang="ts">
import { computed } from "vue";
import DataPanel from "@/components/DataPanel/index.vue";
import Pagination from "@/components/Pagination/index.vue";

defineOptions({
  inheritAttrs: false,
});

const props = withDefaults(
  defineProps<{
    title: string;
    data?: unknown[];
    total?: number;
    page?: number;
    limit?: number;
    loading?: boolean;
    rowKey?: string | ((row: unknown) => string);
    showPagination?: boolean;
  }>(),
  {
    data: () => [],
    total: 0,
    page: 1,
    limit: 10,
    loading: false,
    rowKey: "id",
    showPagination: true,
  }
);

const emit = defineEmits<{
  "update:page": [value: number];
  "update:limit": [value: number];
  pagination: [{ page: number; limit: number }];
  selectionChange: [value: unknown[]];
}>();

const totalProxy = computed(() => props.total);
const pageProxy = computed({
  get: () => props.page,
  set: (value: number) => emit("update:page", value),
});
const limitProxy = computed({
  get: () => props.limit,
  set: (value: number) => emit("update:limit", value),
});

function handleSelectionChange(value: unknown[]) {
  emit("selectionChange", value);
}

function handlePagination(payload: { page: number; limit: number }) {
  emit("pagination", payload);
}
</script>
