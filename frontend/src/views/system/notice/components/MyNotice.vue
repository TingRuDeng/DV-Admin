<template>
  <PageShell class="ff-my-notice-page">
    <FilterPanel>
      <el-form
        ref="queryFormRef"
        :model="queryParams"
        :inline="true"
        class="ff-form ff-toolbar"
        @submit.prevent
      >
        <el-form-item label="通知标题" prop="title">
          <el-input
            v-model="queryParams.title"
            placeholder="关键字"
            clearable
            @keyup.enter="handleQuery()"
          />
        </el-form-item>

        <el-form-item class="ff-toolbar__actions">
          <el-button type="primary" class="ff-button-primary" @click="handleQuery()">
            <template #icon>
              <Search />
            </template>
            搜索
          </el-button>
          <el-button class="ff-button-secondary" @click="handleResetQuery()">
            <template #icon>
              <Refresh />
            </template>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </FilterPanel>

    <DataPanel title="我的通知">
      <div class="ff-table-wrap">
        <el-table
          ref="dataTableRef"
          v-loading="loading"
          :data="pageData"
          highlight-current-row
          class="ff-table"
        >
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
        </el-table>
      </div>

      <template #footer>
        <pagination
          v-if="total > 0"
          v-model:total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          class="mt-4"
          @pagination="handleQuery()"
        />
      </template>
    </DataPanel>

    <el-dialog
      v-model="noticeDialogVisible"
      :title="noticeDetail?.title ?? '通知详情'"
      width="800px"
      class="ff-dialog ff-my-notice-detail-dialog"
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
    </el-dialog>
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "MyNotice",
  inheritAttrs: false,
});

import NoticeAPI, { NoticePageVO, NoticePageQuery, NoticeDetailVO } from "@/api/system/notice-api";

const queryFormRef = ref();
const pageData = ref<NoticePageVO[]>([]);

const loading = ref(false);
const total = ref(0);

const queryParams = reactive<NoticePageQuery>({
  pageNum: 1,
  pageSize: 10,
});

const noticeDialogVisible = ref(false);
const noticeDetail = ref<NoticeDetailVO | null>(null);

// 查询通知公告
function handleQuery() {
  loading.value = true;
  NoticeAPI.getMyNoticePage(queryParams)
    .then((data) => {
      pageData.value = data.list;
      total.value = data.total;
    })
    .finally(() => {
      loading.value = false;
    });
}

// 重置通知公告查询
function handleResetQuery() {
  queryFormRef.value!.resetFields();
  queryParams.pageNum = 1;
  handleQuery();
}

// 阅读通知公告
function handleReadNotice(id: string) {
  NoticeAPI.getDetail(id).then((data) => {
    noticeDialogVisible.value = true;
    noticeDetail.value = data;
  });
}

onMounted(() => {
  handleQuery();
});
</script>
