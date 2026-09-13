<template>
  <PageShell class="ff-notice-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item :label="t('system.title')" prop="title" class="mb-0">
        <el-input
          v-model="queryParams.title"
          :placeholder="t('system.title')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item :label="t('system.publishStatus')" prop="publishStatus" class="mb-0">
        <el-select
          v-model="queryParams.publishStatus"
          clearable
          :placeholder="t('common.all')"
          style="width: 100px"
        >
          <el-option :value="0" :label="t('system.unpublished')" />
          <el-option :value="1" :label="t('system.publishedStatus')" />
          <el-option :value="-1" :label="t('system.revokedStatus')" />
        </el-select>
      </el-form-item>
    </ProSearch>
    <ProTable
      ref="tableRef"
      :title="t('system.noticeData')"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:notices:add']"
            type="primary"
            :icon="resolveAppIcon('plus')"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            {{ t("system.addNotice") }}
          </el-button>
          <el-button
            v-hasPerm="['system:notices:delete']"
            type="danger"
            plain
            :loading="loading"
            :disabled="selectIds.length === 0 || loading"
            :icon="resolveAppIcon('delete')"
            class="ff-button-danger"
            @click="handleDelete()"
          >
            {{ t("system.batchDelete") }}
          </el-button>
        </div>
      </template>
      <template #default>
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" :label="t('system.sequence')" width="60" align="center" />
        <el-table-column :label="t('system.noticeTitle')" prop="title" min-width="200" />
        <el-table-column align="center" :label="t('system.noticeType')" width="150">
          <template #default="scope">
            <DictLabel v-model="scope.row.type" :code="'notice_type'" />
          </template>
        </el-table-column>
        <el-table-column
          align="center"
          :label="t('system.publisher')"
          prop="publisherName"
          width="150"
        />
        <el-table-column align="center" :label="t('system.noticeLevel')" width="100">
          <template #default="scope">
            <DictLabel v-model="scope.row.level" code="notice_level" />
          </template>
        </el-table-column>
        <el-table-column
          align="center"
          :label="t('system.targetType')"
          prop="targetType"
          width="120"
        >
          <template #default="scope">
            <NoticeStatusTag kind="target" :value="scope.row.targetType" />
          </template>
        </el-table-column>
        <el-table-column align="center" :label="t('system.publishStatus')" width="100">
          <template #default="scope">
            <NoticeStatusTag kind="publish" :value="scope.row.publishStatus" />
          </template>
        </el-table-column>
        <el-table-column :label="t('system.operationTime')" width="250">
          <template #default="scope">
            <div class="flex items-center gap-1 text-sm">
              <span class="text-slate-400">{{ t("system.created") }}</span>
              <span>{{ scope.row.createTime || "-" }}</span>
            </div>
            <div v-if="scope.row.publishStatus === 1" class="flex items-center gap-1 text-sm">
              <span class="text-slate-400">{{ t("system.published") }}</span>
              <span>{{ scope.row.publishTime || "-" }}</span>
            </div>
            <div v-else-if="scope.row.publishStatus === -1" class="flex items-center gap-1 text-sm">
              <span class="text-slate-400">{{ t("system.revoked") }}</span>
              <span>{{ scope.row.revokeTime || "-" }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column align="center" fixed="right" :label="t('common.actions')" width="200">
          <template #default="scope">
            <el-button type="primary" link @click="openDetailDialog(scope.row.id)">
              {{ t("common.view") }}
            </el-button>
            <el-button
              v-if="scope.row.publishStatus != 1"
              v-hasPerm="['system:notices:publish']"
              type="primary"
              link
              @click="handlePublish(scope.row.id)"
            >
              {{ t("common.publish") }}
            </el-button>
            <el-button
              v-if="scope.row.publishStatus == 1"
              v-hasPerm="['system:notices:revoke']"
              type="primary"
              link
              @click="handleRevoke(scope.row.id)"
            >
              {{ t("common.revoke") }}
            </el-button>
            <el-button
              v-if="scope.row.publishStatus != 1"
              v-hasPerm="['system:notices:edit']"
              type="primary"
              link
              :icon="resolveAppIcon('edit')"
              @click="handleOpenDialog(scope.row.id)"
            >
              {{ t("common.edit") }}
            </el-button>
            <el-button
              v-if="scope.row.publishStatus != 1"
              v-hasPerm="['system:notices:delete']"
              type="danger"
              link
              :icon="resolveAppIcon('delete')"
              :loading="loading"
              :disabled="loading"
              @click="handleDelete(scope.row.id)"
            >
              {{ t("common.delete") }}
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>
    <NoticeFormDrawer ref="noticeFormDrawerRef" @success="handleQuery" />

    <NoticeDetailDialog ref="noticeDetailDialogRef" />

    <BatchDeleteResultDialog
      ref="batchDeleteResultDialogRef"
      :retry-action="NoticeAPI.retryBatchDelete"
      @changed="handleQuery"
    />
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
defineOptions({
  name: "Notice",
  inheritAttrs: false,
});

import BatchDeleteResultDialog from "@/components/BatchDeleteResultDialog/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import { runExclusive } from "@/utils/exclusive-action";
import { createLogger } from "@/utils/logger";
import type { BatchDeleteResult } from "@/api/system/batch-delete";
import NoticeAPI, { NoticePageQuery, NoticePageVO } from "@/api/system/notice-api";
import NoticeDetailDialog from "./components/NoticeDetailDialog.vue";
import NoticeFormDrawer from "./components/NoticeFormDrawer.vue";
import NoticeStatusTag from "./components/NoticeStatusTag.vue";

const noticeBatchDeleteLogger = createLogger("NoticeBatchDelete");
const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const noticeDetailDialogRef = ref<InstanceType<typeof NoticeDetailDialog> | null>(null);
const noticeFormDrawerRef = ref<InstanceType<typeof NoticeFormDrawer> | null>(null);
const batchDeleteResultDialogRef = ref<InstanceType<typeof BatchDeleteResultDialog> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const loading = ref(false);
const selectIds = ref<string[]>([]);

const queryParams = reactive<Omit<NoticePageQuery, "pageNum" | "pageSize">>({});

function handleQuery() {
  tableRef.value?.reload(true);
}

const requestTableData = createPageRequest<NoticePageQuery, NoticePageVO>(NoticeAPI.getPage);

function handleResetQuery() {
  queryFormRef.value?.resetFields();
  tableRef.value?.reload(true);
}

function handleSelectionChange(selection: NoticePageVO[]) {
  selectIds.value = selection.map((item) => item.id).filter((id): id is string => Boolean(id));
}

async function handleOpenDialog(id?: string) {
  if (id) {
    await noticeFormDrawerRef.value?.openEdit(id);
    return;
  }

  await noticeFormDrawerRef.value?.openCreate();
}

function handlePublish(id: string) {
  NoticeAPI.publish(id).then(() => {
    ElMessage.success(t("system.publishSuccess"));
    tableRef.value?.reload(true);
  });
}

function handleRevoke(id: string) {
  NoticeAPI.revoke(id).then(() => {
    ElMessage.success(t("system.revokeSuccess"));
    tableRef.value?.reload(true);
  });
}

function presentBatchDeleteResult(result: BatchDeleteResult) {
  if (result.successCount > 0) {
    tableRef.value?.reload(true);
  }

  if (result.failedCount === 0) {
    ElMessage.success(t("system.deleteSummary", { count: result.successCount }));
    return;
  }

  const message = t("system.deleteComplete", {
    success: result.successCount,
    failed: result.failedCount,
  });
  if (result.successCount > 0) {
    ElMessage.warning(message);
  } else {
    ElMessage.error(message);
  }
  batchDeleteResultDialogRef.value?.open(result);
}

function handleDelete(id?: string) {
  const deleteIds = id !== undefined ? [id] : selectIds.value;
  if (deleteIds.length === 0) {
    ElMessage.warning(t("system.selectDelete"));
    return;
  }

  void runExclusive(loading, async () => {
    try {
      await ElMessageBox.confirm(t("system.confirmDelete"), t("common.warning"), {
        confirmButtonText: t("common.confirm"),
        cancelButtonText: t("common.cancel"),
        type: "warning",
      });
    } catch {
      ElMessage.info(t("system.cancelDelete"));
      return;
    }

    try {
      presentBatchDeleteResult(await NoticeAPI.deleteByIds(deleteIds));
    } catch (error: unknown) {
      noticeBatchDeleteLogger.error("批量删除失败:", error);
    }
  });
}

const openDetailDialog = async (id: string) => {
  await noticeDetailDialogRef.value?.open(id);
};
</script>
