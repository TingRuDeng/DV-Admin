<template>
  <ProDialog
    v-model="dialogVisible"
    title="操作日志详情"
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
        title="操作执行失败"
        :description="currentLog.errorMsg || `请求返回 HTTP ${currentLog.responseStatus}`"
        type="error"
        :closable="false"
        show-icon
        class="mb-4"
      />

      <el-descriptions :column="1" border>
        <el-descriptions-item label="操作时间">
          {{ currentLog.createdAt || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="操作人">
          {{ currentLog.name || currentLog.username || "-" }}
          <span v-if="currentLog.name && currentLog.username">（{{ currentLog.username }}）</span>
        </el-descriptions-item>
        <el-descriptions-item label="执行状态">
          <el-tag :type="currentLog.status === 1 ? 'success' : 'danger'" effect="light">
            {{ currentLog.status === 1 ? "成功" : "失败" }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="请求信息">
          <span class="font-mono">{{ currentLog.method }} {{ currentLog.path }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="响应码">
          {{ currentLog.responseStatus || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="执行时间">
          {{ currentLog.executionTime }} ms
        </el-descriptions-item>
        <el-descriptions-item label="来源终端">
          {{ currentLog.ip || "-" }} / {{ currentLog.browser || "-" }} / {{ currentLog.os || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="日志内容">
          {{ currentLog.operation || "-" }}
        </el-descriptions-item>
        <el-descriptions-item label="查询参数">
          <pre class="ff-log-detail-payload">{{ formatLogPayload(currentLog.queryParams) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="请求体">
          <pre class="ff-log-detail-payload">{{ formatLogPayload(currentLog.requestBody) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="响应体">
          <pre class="ff-log-detail-payload">{{ formatLogPayload(currentLog.responseBody) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="错误摘要">
          <pre class="ff-log-detail-payload">{{ currentLog.errorMsg || "-" }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </template>
  </ProDialog>
</template>

<script setup lang="ts">
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
