<template>
  <ProDialog
    v-model="dialogVisible"
    title="批量删除结果"
    width="min(760px, calc(100vw - 32px))"
    :show-confirm-button="false"
    cancel-text="关闭"
    append-to-body
    @close="handleDialogClose"
  >
    <template v-if="currentResult">
      <el-alert :title="summaryText" :type="summaryType" :closable="false" show-icon class="mb-4" />

      <el-table
        v-if="currentResult.failures.length > 0"
        :data="currentResult.failures"
        max-height="360"
        style="width: 100%"
      >
        <el-table-column label="对象" min-width="150">
          <template #default="scope">
            {{ scope.row.objectName || scope.row.objectId }}
          </template>
        </el-table-column>
        <el-table-column label="失败原因" min-width="240">
          <template #default="scope">
            <span>{{ scope.row.message }}</span>
            <span class="ml-2 text-xs text-slate-400">{{ scope.row.errorCode }}</span>
          </template>
        </el-table-column>
        <el-table-column label="处理" width="110" align="center">
          <template #default="scope">
            <el-button
              v-if="scope.row.retryable === true"
              type="primary"
              link
              size="small"
              icon="RefreshRight"
              :loading="isRetrying(scope.row.objectId)"
              @click="handleRetry(scope.row)"
            >
              重试
            </el-button>
            <el-tag v-else type="info" size="small">不可重试</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-else description="失败项已处理" :image-size="72" />
    </template>
  </ProDialog>
</template>

<script setup lang="ts">
import type {
  BatchDeleteFailure,
  BatchDeleteObjectId,
  BatchDeleteResult,
} from "@/api/system/batch-delete";
import ProDialog from "@/components/ProDialog/index.vue";
import { createLogger } from "@/utils/logger";
import {
  isCurrentBatchToken,
  isRetryableBatchDeleteFailure,
  mergeBatchDeleteRetryResult,
  shouldNotifyBatchDeleteRetrySuccess,
} from "./batch-delete-result";

const logger = createLogger("BatchDeleteResultDialog");

const props = defineProps<{
  retryAction: (ids: readonly BatchDeleteObjectId[]) => Promise<BatchDeleteResult>;
}>();

const emit = defineEmits<{
  changed: [];
}>();

const dialogVisible = ref(false);
const currentResult = ref<BatchDeleteResult | null>(null);
const retryingIds = ref<string[]>([]);
let currentBatchToken = Symbol("batch-delete-result");

const summaryText = computed(() => {
  if (!currentResult.value) return "";
  return `已删除 ${currentResult.value.successCount} 条，失败 ${currentResult.value.failedCount} 条`;
});

const summaryType = computed<"success" | "warning" | "error">(() => {
  if (!currentResult.value || currentResult.value.failedCount === 0) return "success";
  return currentResult.value.successCount > 0 ? "warning" : "error";
});

function open(result: BatchDeleteResult) {
  currentBatchToken = Symbol("batch-delete-result");
  currentResult.value = {
    ...result,
    successItems: [...result.successItems],
    failures: [...result.failures],
  };
  retryingIds.value = [];
  dialogVisible.value = true;
}

function handleDialogClose() {
  // 关闭后仍可能有未完成的重试请求，令牌失效可阻止其回写下一次打开前的状态。
  currentBatchToken = Symbol("batch-delete-result");
  retryingIds.value = [];
}

function isRetrying(objectId: string) {
  return retryingIds.value.includes(objectId);
}

function addRetrying(objectId: string) {
  if (!isRetrying(objectId)) retryingIds.value = [...retryingIds.value, objectId];
}

function removeRetrying(objectId: string) {
  retryingIds.value = retryingIds.value.filter((item) => item !== objectId);
}

async function handleRetry(failure: BatchDeleteFailure) {
  if (!isRetryableBatchDeleteFailure(failure) || isRetrying(failure.objectId)) return;

  const requestToken = currentBatchToken;
  addRetrying(failure.objectId);
  try {
    const retryResult = await props.retryAction([failure.objectId]);
    if (!currentResult.value || !isCurrentBatchToken(requestToken, currentBatchToken)) return;

    currentResult.value = mergeBatchDeleteRetryResult(
      currentResult.value,
      failure.objectId,
      retryResult
    );
    if (shouldNotifyBatchDeleteRetrySuccess(currentResult.value, failure.objectId)) {
      ElMessage.success(`${failure.objectName || "对象"}删除成功`);
      emit("changed");
    } else {
      const latestFailure = currentResult.value.failures.find(
        (item) => item.objectId === failure.objectId
      );
      ElMessage.warning(latestFailure?.message || "删除仍未成功");
    }
  } catch (error: unknown) {
    logger.error("批量删除重试失败:", error);
    // 请求拦截器会展示服务端错误；网络异常在此补充明确的可观察反馈。
    ElMessage.error(error instanceof Error ? `重试失败：${error.message}` : "重试失败");
  } finally {
    if (isCurrentBatchToken(requestToken, currentBatchToken)) {
      removeRetrying(failure.objectId);
    }
  }
}

defineExpose({ open });
</script>
