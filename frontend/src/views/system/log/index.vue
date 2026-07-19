<template>
  <PageShell class="ff-log-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item prop="operation" label="关键字" class="mb-0">
        <el-input
          v-model="queryParams.operation"
          placeholder="日志内容"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item prop="username" label="操作人" class="mb-0">
        <el-input
          v-model="queryParams.username"
          placeholder="用户名"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item prop="method" label="请求方法" class="mb-0">
        <el-select v-model="queryParams.method" placeholder="全部" clearable style="width: 120px">
          <el-option v-for="method in HTTP_METHODS" :key="method" :label="method" :value="method" />
        </el-select>
      </el-form-item>

      <el-form-item prop="status" label="执行状态" class="mb-0">
        <el-select v-model="queryParams.status" placeholder="全部" clearable style="width: 120px">
          <el-option label="成功" :value="1" />
          <el-option label="失败" :value="0" />
        </el-select>
      </el-form-item>

      <el-form-item prop="createTime" label="操作时间" class="mb-0">
        <el-date-picker
          v-model="queryParams.createTime"
          :editable="false"
          type="daterange"
          range-separator="~"
          start-placeholder="开始时间"
          end-placeholder="截止时间"
          value-format="YYYY-MM-DD"
          style="width: 200px"
        />
      </el-form-item>
    </ProSearch>

    <ProTable ref="tableRef" title="操作日志" :request="requestTableData" :params="queryParams">
      <el-table-column label="操作时间" prop="createdAt" width="180" />
      <el-table-column label="操作人" prop="username" width="120" />
      <el-table-column label="请求方法" prop="method" width="100" />
      <el-table-column label="执行状态" prop="status" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="light">
            {{ row.status === 1 ? "成功" : "失败" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="响应码" prop="responseStatus" width="100" align="center" />
      <el-table-column label="日志内容" prop="operation" min-width="180" />
      <el-table-column label="请求路径" prop="path" min-width="220" show-overflow-tooltip />
      <el-table-column label="IP 地址" prop="ip" width="150" />
      <el-table-column label="浏览器" prop="browser" width="150" />
      <el-table-column label="终端系统" prop="os" width="200" show-overflow-tooltip />
      <el-table-column label="执行时间(ms)" prop="executionTime" width="150" align="center" />
      <el-table-column label="操作" fixed="right" width="100" align="center">
        <template #default="{ row }">
          <el-button type="primary" link :icon="View" @click="openDetailDialog(row.id)">
            查看
          </el-button>
        </template>
      </el-table-column>
    </ProTable>

    <LogDetailDialog ref="logDetailDialogRef" />
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "Log",
  inheritAttrs: false,
});

import LogAPI, { LogPageQuery, LogPageVO } from "@/api/system/log-api";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import { View } from "@element-plus/icons-vue";
import LogDetailDialog from "./components/LogDetailDialog.vue";

const HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"] as const;

interface LogPageRequestParams extends PageQuery {
  operation?: string;
  username?: string;
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
  method: undefined,
  status: undefined,
  createTime: undefined,
});

/** 将页面筛选状态转换为 FastAPI 日志分页接口契约。 */
function buildLogPageQuery(params: LogPageRequestParams): LogPageQuery {
  const { createTime, method, operation, pageNum, pageSize, status, username } = params;
  return {
    pageNum,
    pageSize,
    operation: operation || undefined,
    username: username || undefined,
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
