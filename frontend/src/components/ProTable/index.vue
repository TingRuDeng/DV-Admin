<template>
  <DataPanel :title="title">
    <template v-if="$slots.actions" #actions>
      <slot name="actions" />
    </template>

    <div class="ff-table-wrap">
      <el-table
        v-loading="loadingProxy"
        :data="dataProxy"
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
          v-if="showPagination && totalProxy > 0"
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
import { computed, ref, watch } from "vue";
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
    request?: (params: Record<string, unknown>) => Promise<{ list?: unknown[]; total?: number }>;
    params?: Record<string, unknown>;
    immediate?: boolean;
    rowKey?: string | ((row: unknown) => string);
    showPagination?: boolean;
  }>(),
  {
    data: () => [],
    total: 0,
    page: 1,
    limit: 10,
    loading: false,
    params: () => ({}),
    immediate: true,
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

const innerLoading = ref(false);
const innerData = ref<unknown[]>([]);
const innerTotal = ref(0);
const innerPage = ref(props.page);
const innerLimit = ref(props.limit);

const isRequestMode = computed(() => typeof props.request === "function");
const loadingProxy = computed(() => (isRequestMode.value ? innerLoading.value : props.loading));
const dataProxy = computed(() => (isRequestMode.value ? innerData.value : props.data));
const totalProxy = computed(() => (isRequestMode.value ? innerTotal.value : props.total));

const pageProxy = computed({
  get: () => (isRequestMode.value ? innerPage.value : props.page),
  set: (value: number) => {
    if (isRequestMode.value) {
      innerPage.value = value;
      return;
    }
    emit("update:page", value);
  },
});
const limitProxy = computed({
  get: () => (isRequestMode.value ? innerLimit.value : props.limit),
  set: (value: number) => {
    if (isRequestMode.value) {
      innerLimit.value = value;
      return;
    }
    emit("update:limit", value);
  },
});

async function reload(resetPage: boolean = false) {
  if (!props.request) {
    return;
  }

  if (resetPage) {
    innerPage.value = 1;
  }

  innerLoading.value = true;
  try {
    const result = await props.request({
      ...props.params,
      pageNum: innerPage.value,
      pageSize: innerLimit.value,
    });
    innerData.value = result?.list ?? [];
    innerTotal.value = Number(result?.total ?? 0);
  } finally {
    innerLoading.value = false;
  }
}

function handleSelectionChange(value: unknown[]) {
  emit("selectionChange", value);
}

function handlePagination(payload: { page: number; limit: number }) {
  if (isRequestMode.value) {
    reload();
  }
  emit("pagination", payload);
}

watch(
  () => props.page,
  (value) => {
    if (isRequestMode.value) {
      innerPage.value = value;
    }
  }
);

watch(
  () => props.limit,
  (value) => {
    if (isRequestMode.value) {
      innerLimit.value = value;
    }
  }
);

watch(
  [isRequestMode, () => props.params, () => props.request],
  () => {
    if (!isRequestMode.value || !props.immediate) {
      return;
    }
    reload();
  },
  { immediate: true, deep: true }
);

defineExpose({
  reload,
});
</script>
