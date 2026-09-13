<template>
  <PageShell class="ff-log-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item prop="operation" :label="t('common.keyword')" class="mb-0">
        <el-input
          v-model="queryParams.operation"
          :placeholder="t('system.logContent')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item prop="username" :label="t('system.operator')" class="mb-0">
        <el-input
          v-model="queryParams.username"
          :placeholder="t('system.username')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item prop="requestId" :label="t('system.requestId')" class="mb-0">
        <el-input
          v-model="queryParams.requestId"
          :placeholder="t('system.fullRequestId')"
          maxlength="64"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item prop="objectType" :label="t('system.objectType')" class="mb-0">
        <el-input
          v-model="queryParams.objectType"
          :placeholder="t('system.objectTypePlaceholder')"
          maxlength="100"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item prop="objectId" :label="t('system.objectId')" class="mb-0">
        <el-input
          v-model="queryParams.objectId"
          :placeholder="t('system.objectIdPlaceholder')"
          maxlength="255"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item prop="method" :label="t('system.method')" class="mb-0">
        <el-select
          v-model="queryParams.method"
          :placeholder="t('common.all')"
          clearable
          style="width: 120px"
        >
          <el-option v-for="method in HTTP_METHODS" :key="method" :label="method" :value="method" />
        </el-select>
      </el-form-item>

      <el-form-item prop="status" :label="t('system.executionStatus')" class="mb-0">
        <el-select
          v-model="queryParams.status"
          :placeholder="t('common.all')"
          clearable
          style="width: 120px"
        >
          <el-option :label="t('system.successStatus')" :value="1" />
          <el-option :label="t('system.failedStatus')" :value="0" />
        </el-select>
      </el-form-item>

      <el-form-item prop="createTime" :label="t('system.operationTime')" class="mb-0">
        <el-date-picker
          v-model="queryParams.createTime"
          :editable="false"
          type="daterange"
          range-separator="~"
          :start-placeholder="t('common.startTime')"
          :end-placeholder="t('common.endTime')"
          value-format="YYYY-MM-DD"
          style="width: 200px"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      :title="t('system.logData')"
      :request="requestTableData"
      :params="queryParams"
    >
      <el-table-column :label="t('system.operationTime')" prop="createdAt" width="180" />
      <el-table-column :label="t('system.operator')" prop="username" width="120" />
      <el-table-column :label="t('system.method')" prop="method" width="100" />
      <el-table-column
        :label="t('system.objectType')"
        prop="objectType"
        width="150"
        show-overflow-tooltip
      />
      <el-table-column
        :label="t('system.objectId')"
        prop="objectId"
        width="150"
        show-overflow-tooltip
      />
      <el-table-column
        :label="t('system.executionStatus')"
        prop="status"
        width="100"
        align="center"
      >
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="light">
            {{ row.status === 1 ? t("system.successStatus") : t("system.failedStatus") }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        :label="t('system.responseCode')"
        prop="responseStatus"
        width="100"
        align="center"
      />
      <el-table-column :label="t('system.logContent')" prop="operation" min-width="180" />
      <el-table-column
        :label="t('system.requestPath')"
        prop="path"
        min-width="220"
        show-overflow-tooltip
      />
      <el-table-column :label="t('system.ipAddress')" prop="ip" width="150" />
      <el-table-column :label="t('system.browser')" prop="browser" width="150" />
      <el-table-column :label="t('system.os')" prop="os" width="200" show-overflow-tooltip />
      <el-table-column
        :label="t('system.executionTime')"
        prop="executionTime"
        width="150"
        align="center"
      />
      <el-table-column :label="t('common.actions')" fixed="right" width="100" align="center">
        <template #default="{ row }">
          <el-button type="primary" link @click="openDetailDialog(row.id)">
            <AppIcon name="eye" :size="16" />
            {{ t("common.view") }}
          </el-button>
        </template>
      </el-table-column>
    </ProTable>

    <LogDetailDialog ref="logDetailDialogRef" />
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
defineOptions({
  name: "Log",
  inheritAttrs: false,
});

import LogAPI, { LogPageQuery, LogPageVO } from "@/api/system/log-api";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import AppIcon from "@/components/AppIcon/index.vue";
import LogDetailDialog from "./components/LogDetailDialog.vue";

const HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"] as const;

interface LogPageRequestParams extends PageQuery {
  operation?: string;
  username?: string;
  requestId?: string;
  objectType?: string;
  objectId?: string;
  method?: string;
  status?: number;
  createTime?: [string, string];
}

const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const tableRef = ref<ProTableExpose | null>(null);
const logDetailDialogRef = ref<InstanceType<typeof LogDetailDialog> | null>(null);

const queryParams = reactive<Omit<LogPageRequestParams, "pageNum" | "pageSize">>({
  operation: "",
  username: "",
  requestId: "",
  objectType: "",
  objectId: "",
  method: undefined,
  status: undefined,
  createTime: undefined,
});

/** 将页面筛选状态转换为双后端日志分页接口契约。 */
function buildLogPageQuery(params: LogPageRequestParams): LogPageQuery {
  const {
    createTime,
    method,
    objectId,
    objectType,
    operation,
    pageNum,
    pageSize,
    requestId,
    status,
    username,
  } = params;
  return {
    pageNum,
    pageSize,
    operation: operation || undefined,
    username: username || undefined,
    requestId: requestId?.trim() || undefined,
    objectType: objectType?.trim() || undefined,
    objectId: objectId?.trim() || undefined,
    method: method || undefined,
    status,
    startTime: toDateTimeStart(createTime?.[0]),
    endTime: toDateTimeEnd(createTime?.[1]),
  };
}

/** 将日期转换为后端可解析的当天开始时间。 */
function toDateTimeStart(date?: string) {
  return date ? `${date}T00:00:00` : undefined;
}

/** 将日期转换为后端可解析的当天结束时间。 */
function toDateTimeEnd(date?: string) {
  return date ? `${date}T23:59:59` : undefined;
}

const requestTableData = createPageRequest<LogPageRequestParams, LogPageVO>((params) =>
  LogAPI.getPage(buildLogPageQuery(params))
);

/** 查询（重置页码后获取数据） */
function handleQuery() {
  tableRef.value?.reload(true);
}

/** 重置查询 */
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  queryParams.createTime = undefined;
  tableRef.value?.reload(true);
}

/** 打开日志详情。 */
async function openDetailDialog(id: number) {
  await logDetailDialogRef.value?.open(id);
}
</script>
