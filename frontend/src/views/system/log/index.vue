<template>
  <PageShell class="ff-log-page">
    <FilterPanel>
      <el-form
        ref="queryFormRef"
        :model="queryParams"
        :inline="true"
        class="ff-form ff-toolbar"
        @submit.prevent
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

        <el-form-item class="ff-toolbar__actions">
          <el-button type="primary" icon="search" class="ff-button-primary" @click="handleQuery">
            搜索
          </el-button>
          <el-button icon="refresh" class="ff-button-secondary" @click="handleResetQuery">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </FilterPanel>

    <DataPanel title="操作日志">
      <div class="ff-table-wrap">
        <el-table v-loading="loading" :data="pageData" highlight-current-row class="ff-table">
          <el-table-column label="操作时间" prop="createTime" width="180" />
          <el-table-column label="操作人" prop="operator" width="120" />
          <el-table-column label="日志模块" prop="module" width="100" />
          <el-table-column label="日志内容" prop="content" min-width="200" />
          <el-table-column label="IP 地址" prop="ip" width="150" />
          <el-table-column label="地区" prop="region" width="150" />
          <el-table-column label="浏览器" prop="browser" width="150" />
          <el-table-column label="终端系统" prop="os" width="200" show-overflow-tooltip />
          <el-table-column label="执行时间(ms)" prop="executionTime" width="150" align="center" />
        </el-table>
      </div>

      <template #footer>
        <pagination
          v-if="total > 0"
          v-model:total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          class="mt-4"
          @pagination="fetchData"
        />
      </template>
    </DataPanel>
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "Log",
  inheritAttrs: false,
});

import LogAPI, { LogPageVO, LogPageQuery } from "@/api/system/log-api";

const queryFormRef = ref();

const loading = ref(false);
const total = ref(0);

const queryParams = reactive<LogPageQuery>({
  pageNum: 1,
  pageSize: 10,
  keywords: "",
  createTime: ["", ""],
});

// 日志表格数据
const pageData = ref<LogPageVO[]>();

/** 获取数据 */
function fetchData() {
  loading.value = true;
  LogAPI.getPage(queryParams)
    .then((data) => {
      pageData.value = data.list;
      total.value = data.total;
    })
    .finally(() => {
      loading.value = false;
    });
}

/** 查询（重置页码后获取数据） */
function handleQuery() {
  queryParams.pageNum = 1;
  fetchData();
}

/** 重置查询 */
function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryParams.pageNum = 1;
  queryParams.createTime = undefined;
  fetchData();
}

onMounted(() => {
  handleQuery();
});
</script>
