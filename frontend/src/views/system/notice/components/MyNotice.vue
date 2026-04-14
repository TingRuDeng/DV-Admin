<template>
  <PageShell class="ff-my-notice-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item label="通知标题" prop="title">
        <el-input
          v-model="queryParams.title"
          placeholder="关键字"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable ref="tableRef" title="我的通知" :request="requestTableData" :params="queryParams">
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column label="通知标题" prop="title" min-width="200" />
      <el-table-column align="center" label="通知类型" width="150">
        <template #default="scope">
          <DictLabel v-model="scope.row.type" code="notice_type" />
        </template>
      </el-table-column>
      <el-table-column align="center" label="发布人" prop="publisherName" width="100" />
      <el-table-column align="center" label="通知等级" width="100">
        <template #default="scope">
          <DictLabel v-model="scope.row.level" code="notice_level" />
        </template>
      </el-table-column>
      <el-table-column
        key="releaseTime"
        align="center"
        label="发布时间"
        prop="publishTime"
        width="150"
      />

      <el-table-column align="center" label="发布人" prop="publisherName" width="150" />
      <el-table-column align="center" label="状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.isRead == 1" type="success" class="ff-status-tag success">
            已读
          </el-tag>
          <el-tag v-else type="info" class="ff-status-tag info">未读</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" fixed="right" label="操作" width="80">
        <template #default="scope">
          <el-button type="primary" size="small" link @click="handleReadNotice(scope.row.id)">
            查看
          </el-button>
        </template>
      </el-table-column>
    </ProTable>

    <ProDialog
      v-model="noticeDialogVisible"
      :title="noticeDetail?.title ?? '通知详情'"
      width="800px"
      class="ff-my-notice-detail-dialog"
      :show-footer="false"
      @close="handleCloseNoticeDialog"
    >
      <div v-if="noticeDetail" class="ff-my-notice-detail__wrapper">
        <div class="ff-my-notice-detail__meta">
          <span>
            <el-icon><User /></el-icon>
            {{ noticeDetail.publisherName }}
          </span>
          <span class="ml-2">
            <el-icon><Timer /></el-icon>
            {{ noticeDetail.publishTime }}
          </span>
        </div>

        <div class="ff-my-notice-detail__content">
          <div v-html="noticeDetail.content"></div>
        </div>
      </div>
    </ProDialog>
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "MyNotice",
  inheritAttrs: false,
});

import ProDialog from "@/components/ProDialog/index.vue";
import NoticeAPI, { NoticePageQuery, NoticeDetailVO } from "@/api/system/notice-api";

const queryFormRef = ref();
const tableRef = ref<{ reload: (resetPage?: boolean) => Promise<void> } | null>(null);

const queryParams = reactive<Omit<NoticePageQuery, "pageNum" | "pageSize">>({});

const noticeDialogVisible = ref(false);
const noticeDetail = ref<NoticeDetailVO | null>(null);

// 查询通知公告
function handleQuery() {
  tableRef.value?.reload(true);
}

function requestTableData(params: Record<string, unknown>) {
  return NoticeAPI.getMyNoticePage(params as unknown as NoticePageQuery);
}

// 重置通知公告查询
function handleResetQuery() {
  queryFormRef.value!.resetFields();
  tableRef.value?.reload(true);
}

// 阅读通知公告
function handleReadNotice(id: string) {
  NoticeAPI.getDetail(id).then((data) => {
    noticeDialogVisible.value = true;
    noticeDetail.value = data;
  });
}

function handleCloseNoticeDialog() {
  noticeDialogVisible.value = false;
}
</script>
