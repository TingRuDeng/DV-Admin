<template>
  <ProDialog
    v-model="dialogVisible"
    :title="t('system.logDetail')"
    width="min(860px, calc(100vw - 32px))"
    :loading="loading"
    :show-footer="false"
    append-to-body
    class="ff-log-detail-dialog"
    @close="close"
  >
    <template v-if="currentLog">
      <el-alert
        v-if="currentLog.status === 0"
        :title="t('system.operationFailed')"
        :description="
          currentLog.errorMsg || t('system.httpResponse', { code: currentLog.responseStatus })
        "
        type="error"
        :closable="false"
        show-icon
        class="mb-4"
      />

      <el-descriptions :column="1" border>
        <el-descriptions-item :label="t('system.operationTime')">
          {{ currentLog.createdAt || "-" }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.operator')">
          {{ currentLog.name || currentLog.username || "-" }}
          <span v-if="currentLog.name && currentLog.username">（{{ currentLog.username }}）</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.executionStatus')">
          <el-tag :type="currentLog.status === 1 ? 'success' : 'danger'" effect="light">
            {{ currentLog.status === 1 ? t("system.successStatus") : t("system.failedStatus") }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.requestInfo')">
          <span class="font-mono">{{ currentLog.method }} {{ currentLog.path }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.requestId')">
          <span class="font-mono">{{ currentLog.requestId || "-" }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.relatedObjectType')">
          <span class="font-mono">{{ currentLog.objectType || "-" }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.relatedObjectId')">
          <span class="font-mono">{{ currentLog.objectId || "-" }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.responseCode')">
          {{ currentLog.responseStatus || "-" }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.executionTime')">
          {{ currentLog.executionTime }} ms
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.sourceTerminal')">
          {{ currentLog.ip || "-" }} / {{ currentLog.browser || "-" }} / {{ currentLog.os || "-" }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.logContent')">
          {{ currentLog.operation || "-" }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.queryParams')">
          <pre class="ff-log-detail-payload">{{ formatLogPayload(currentLog.queryParams) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.requestContext')">
          <pre class="ff-log-detail-payload">{{ formatLogPayload(currentLog.requestContext) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.requestBody')">
          <pre class="ff-log-detail-payload">{{ formatLogPayload(currentLog.requestBody) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.responseBody')">
          <pre class="ff-log-detail-payload">{{ formatLogPayload(currentLog.responseBody) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item :label="t('system.errorSummary')">
          <pre class="ff-log-detail-payload">{{ currentLog.errorMsg || "-" }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </template>
  </ProDialog>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import type { LogPageVO } from "@/api/system/log-api";
import LogAPI from "@/api/system/log-api";
import ProDialog from "@/components/ProDialog/index.vue";
import { formatLogPayload } from "../log-detail-utils";

const dialogVisible = ref(false);
const loading = ref(false);
const currentLog = ref<LogPageVO | null>(null);

function close() {
  dialogVisible.value = false;
  currentLog.value = null;
}

async function open(id: number) {
  dialogVisible.value = true;
  loading.value = true;
  try {
    currentLog.value = await LogAPI.getDetail(id);
  } catch {
    close();
  } finally {
    loading.value = false;
  }
}

defineExpose({
  open,
});
</script>

<style scoped>
.ff-log-detail-payload {
  max-height: 240px;
  margin: 0;
  overflow: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  line-height: 1.5;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}
</style>
