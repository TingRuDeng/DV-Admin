<template>
  <PageShell class="ff-notice-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item label="标题" prop="title" class="mb-0">
        <el-input
          v-model="queryParams.title"
          placeholder="标题"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item label="发布状态" prop="publishStatus" class="mb-0">
        <el-select
          v-model="queryParams.publishStatus"
          clearable
          placeholder="全部"
          style="width: 100px"
        >
          <el-option :value="0" label="未发布" />
          <el-option :value="1" label="已发布" />
          <el-option :value="-1" label="已撤回" />
        </el-select>
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      title="通知公告"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:notices:add']"
            type="primary"
            icon="plus"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            新增通知
          </el-button>
          <el-button
            v-hasPerm="['system:notices:delete']"
            type="danger"
            plain
            :disabled="selectIds.length === 0"
            icon="delete"
            class="ff-button-danger"
            @click="handleDelete()"
          >
            批量删除
          </el-button>
        </div>
      </template>
      <template #default>
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column label="通知标题" prop="title" min-width="200" />
        <el-table-column align="center" label="通知类型" width="150">
          <template #default="scope">
            <DictLabel v-model="scope.row.type" :code="'notice_type'" />
          </template>
        </el-table-column>
        <el-table-column align="center" label="发布人" prop="publisherName" width="150" />
        <el-table-column align="center" label="通知等级" width="100">
          <template #default="scope">
            <DictLabel v-model="scope.row.level" code="notice_level" />
          </template>
        </el-table-column>
        <el-table-column align="center" label="通告目标类型" prop="targetType" width="120">
          <template #default="scope">
            <el-tag
              v-if="scope.row.targetType == 1"
              type="warning"
              effect="light"
              class="ff-status-tag warning"
            >
              全体
            </el-tag>
            <el-tag
              v-if="scope.row.targetType == 2"
              type="success"
              effect="light"
              class="ff-status-tag success"
            >
              指定
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column align="center" label="发布状态" width="100">
          <template #default="scope">
            <el-tag
              v-if="scope.row.publishStatus == 0"
              type="info"
              effect="light"
              class="ff-status-tag info"
            >
              未发布
            </el-tag>
            <el-tag
              v-if="scope.row.publishStatus == 1"
              type="success"
              effect="light"
              class="ff-status-tag success"
            >
              已发布
            </el-tag>
            <el-tag
              v-if="scope.row.publishStatus == -1"
              type="warning"
              effect="light"
              class="ff-status-tag warning"
            >
              已撤回
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作时间" width="250">
          <template #default="scope">
            <div class="flex items-center gap-1 text-sm">
              <span class="text-slate-400">创建：</span>
              <span>{{ scope.row.createTime || "-" }}</span>
            </div>

            <div v-if="scope.row.publishStatus === 1" class="flex items-center gap-1 text-sm">
              <span class="text-slate-400">发布：</span>
              <span>{{ scope.row.publishTime || "-" }}</span>
            </div>
            <div v-else-if="scope.row.publishStatus === -1" class="flex items-center gap-1 text-sm">
              <span class="text-slate-400">撤回：</span>
              <span>{{ scope.row.revokeTime || "-" }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column align="center" fixed="right" label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" link @click="openDetailDialog(scope.row.id)">查看</el-button>
            <el-button
              v-if="scope.row.publishStatus != 1"
              v-hasPerm="['system:notices:publish']"
              type="primary"
              link
              @click="handlePublish(scope.row.id)"
            >
              发布
            </el-button>
            <el-button
              v-if="scope.row.publishStatus == 1"
              v-hasPerm="['system:notices:revoke']"
              type="primary"
              link
              @click="handleRevoke(scope.row.id)"
            >
              撤回
            </el-button>
            <el-button
              v-if="scope.row.publishStatus != 1"
              v-hasPerm="['system:notices:edit']"
              type="primary"
              link
              icon="edit"
              @click="handleOpenDialog(scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-if="scope.row.publishStatus != 1"
              v-hasPerm="['system:notices:delete']"
              type="danger"
              link
              icon="delete"
              @click="handleDelete(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>

    <NoticeFormDrawer ref="noticeFormDrawerRef" @success="handleQuery" />

    <NoticeDetailDialog ref="noticeDetailDialogRef" />
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "Notice",
  inheritAttrs: false,
});

import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import NoticeAPI, { NoticePageQuery, NoticePageVO } from "@/api/system/notice-api";
import NoticeDetailDialog from "./components/NoticeDetailDialog.vue";
import NoticeFormDrawer from "./components/NoticeFormDrawer.vue";

const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const noticeDetailDialogRef = ref<InstanceType<typeof NoticeDetailDialog> | null>(null);
const noticeFormDrawerRef = ref<InstanceType<typeof NoticeFormDrawer> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const loading = ref(false);
const selectIds = ref<string[]>([]);

const queryParams = reactive<Omit<NoticePageQuery, "pageNum" | "pageSize">>({});

// 查询通知公告
function handleQuery() {
  tableRef.value?.reload(true);
}

const requestTableData = createPageRequest<NoticePageQuery, NoticePageVO>(NoticeAPI.getPage);

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  tableRef.value?.reload(true);
}

// 行复选框选中项变化
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

// 发布通知公告
function handlePublish(id: string) {
  NoticeAPI.publish(id).then(() => {
    ElMessage.success("发布成功");
    tableRef.value?.reload(true);
  });
}

// 撤回通知公告
function handleRevoke(id: string) {
  NoticeAPI.revoke(id).then(() => {
    ElMessage.success("撤回成功");
    tableRef.value?.reload(true);
  });
}

// 删除通知公告
function handleDelete(id?: string) {
  const deleteIds = [id || selectIds.value].join(",");
  if (!deleteIds) {
    ElMessage.warning("请勾选删除项");
    return;
  }

  ElMessageBox.confirm("确认删除已选中的数据项?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(
    () => {
      loading.value = true;
      NoticeAPI.deleteByIds(deleteIds)
        .then(() => {
          ElMessage.success("删除成功");
          tableRef.value?.reload(true);
        })
        .finally(() => (loading.value = false));
    },
    () => {
      ElMessage.info("已取消删除");
    }
  );
}

const openDetailDialog = async (id: string) => {
  await noticeDetailDialogRef.value?.open(id);
};
</script>
