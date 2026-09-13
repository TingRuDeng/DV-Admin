<template>
  <PageShell class="ff-my-notice-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item :label="t('system.noticeTitle')" prop="title">
        <el-input
          v-model="queryParams.title"
          :placeholder="t('common.keyword')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      :title="t('system.myNotice')"
      :request="requestTableData"
      :params="queryParams"
    >
      <el-table-column type="index" :label="t('system.sequence')" width="60" />
      <el-table-column :label="t('system.noticeTitle')" prop="title" min-width="200" />
      <el-table-column align="center" :label="t('system.noticeType')" width="150">
        <template #default="scope">
          <DictLabel v-model="scope.row.type" code="notice_type" />
        </template>
      </el-table-column>
      <el-table-column
        align="center"
        :label="t('system.publisher')"
        prop="publisherName"
        width="100"
      />
      <el-table-column align="center" :label="t('system.noticeLevel')" width="100">
        <template #default="scope">
          <DictLabel v-model="scope.row.level" code="notice_level" />
        </template>
      </el-table-column>
      <el-table-column
        key="releaseTime"
        align="center"
        :label="t('system.releaseTime')"
        prop="publishTime"
        width="150"
      />
      <el-table-column align="center" :label="t('common.status')" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.isRead == 1" type="success" class="ff-status-tag success">
            {{ t("system.read") }}
          </el-tag>
          <el-tag v-else type="info" class="ff-status-tag info">{{ t("system.unread") }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" fixed="right" :label="t('common.actions')" width="80">
        <template #default="scope">
          <el-button type="primary" size="small" link @click="handleReadNotice(scope.row.id)">
            {{ t("common.view") }}
          </el-button>
        </template>
      </el-table-column>
    </ProTable>

    <ProDialog
      v-model="noticeDialogVisible"
      :title="noticeDetail?.title ?? t('system.noticeDetailShort')"
      width="800px"
      class="ff-my-notice-detail-dialog"
      :show-footer="false"
      @close="handleCloseNoticeDialog"
    >
      <div v-if="noticeDetail" class="ff-my-notice-detail__wrapper">
        <div class="ff-my-notice-detail__meta">
          <span>
            <AppIcon name="user-round" :size="15" />
            {{ noticeDetail.publisherName }}
          </span>
          <span class="ml-2">
            <AppIcon name="calendar-days" :size="15" />
            {{ noticeDetail.publishTime }}
          </span>
        </div>

        <div class="ff-my-notice-detail__content">
          <SafeHtml :content="noticeDetail.content" />
        </div>
      </div>
    </ProDialog>
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import AppIcon from "@/components/AppIcon/index.vue";
defineOptions({
  name: "MyNotice",
  inheritAttrs: false,
});

import ProDialog from "@/components/ProDialog/index.vue";
import SafeHtml from "@/components/SafeHtml/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import NoticeAPI, {
  MyNoticePageQuery,
  NoticeDetailVO,
  NoticePageVO,
} from "@/api/system/notice-api";

const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const queryParams = reactive<Omit<MyNoticePageQuery, "pageNum" | "pageSize">>({});

const noticeDialogVisible = ref(false);
const noticeDetail = ref<NoticeDetailVO | null>(null);

// 查询通知公告
function handleQuery() {
  tableRef.value?.reload(true);
}

const requestTableData = createPageRequest<MyNoticePageQuery, NoticePageVO>(
  NoticeAPI.getMyNoticePage
);

// 重置通知公告查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
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
