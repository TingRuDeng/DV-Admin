<template>
  <PageShell class="ff-log-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item prop="keywords" label="关键字" class="mb-0">
        <el-input
          v-model="queryParams.keywords"
          placeholder="日志内容"
          clearable
          @keyup.enter="handleQuery"
        />
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
      <el-table-column label="操作时间" prop="createTime" width="180" />
      <el-table-column label="操作人" prop="operator" width="120" />
      <el-table-column label="日志模块" prop="module" width="100" />
      <el-table-column label="日志内容" prop="content" min-width="200" />
      <el-table-column label="IP 地址" prop="ip" width="150" />
      <el-table-column label="地区" prop="region" width="150" />
      <el-table-column label="浏览器" prop="browser" width="150" />
      <el-table-column label="终端系统" prop="os" width="200" show-overflow-tooltip />
      <el-table-column label="执行时间(ms)" prop="executionTime" width="150" align="center" />
    </ProTable>
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

const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const queryParams = reactive<Omit<LogPageQuery, "pageNum" | "pageSize">>({
  keywords: "",
  createTime: undefined,
});

const requestTableData = createPageRequest<LogPageQuery, LogPageVO>(LogAPI.getPage);

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
</script>
