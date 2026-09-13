<template>
  <PageShell class="ff-role-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item prop="search" :label="t('common.keyword')">
        <el-input
          v-model="queryParams.search"
          :placeholder="t('system.roleName')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      :title="t('system.roleData')"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:roles:add']"
            type="primary"
            :icon="resolveAppIcon('plus')"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            {{ t("system.addRole") }}
          </el-button>
          <el-button
            v-hasPerm="['system:roles:delete']"
            type="danger"
            plain
            :loading="loading"
            :disabled="ids.length === 0 || loading"
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
        <el-table-column :label="t('common.sort')" align="center" width="80" prop="sort">
          <template #default="{ row }">
            <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">
              {{ row.sort }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="t('system.roleName')" prop="name" min-width="100" />
        <el-table-column :label="t('common.status')" align="center" width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === 1 ? 'success' : 'info'"
              class="ff-status-tag"
              :class="scope.row.status === 1 ? 'success' : 'info'"
            >
              {{ scope.row.status === 1 ? t("common.normal") : t("common.disabled") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('system.defaultRole')" align="center" width="120">
          <template #default="scope">
            <el-tag
              :type="scope.row.isDefault ? 'success' : 'info'"
              class="ff-status-tag"
              :class="scope.row.isDefault ? 'success' : 'info'"
            >
              {{ scope.row.isDefault ? t("common.yes") : t("common.no") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('system.roleRemark')" prop="desc" min-width="200" />
        <el-table-column fixed="right" :label="t('common.actions')" width="280">
          <template #default="scope">
            <el-button
              v-hasPerm="'system:roles:edit'"
              type="primary"
              link
              :icon="resolveAppIcon('position')"
              size="small"
              @click="handleOpenAssignPermDialog(scope.row)"
            >
              {{ t("system.assignPermission") }}
            </el-button>
            <el-button
              v-hasPerm="'system:roles:edit'"
              type="primary"
              link
              :icon="resolveAppIcon('edit')"
              size="small"
              @click="handleOpenDialog(scope.row.id)"
            >
              {{ t("common.edit") }}
            </el-button>
            <el-button
              v-hasPerm="'system:roles:delete'"
              type="danger"
              link
              :icon="resolveAppIcon('delete')"
              :loading="loading"
              :disabled="loading"
              size="small"
              @click="handleDelete(scope.row.id)"
            >
              {{ t("common.delete") }}
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>

    <RoleFormDrawer ref="roleFormDrawerRef" @success="handleQuery" />

    <RolePermissionDrawer ref="rolePermissionDrawerRef" @success="handleQuery" />

    <BatchDeleteResultDialog
      ref="batchDeleteResultDialogRef"
      :retry-action="RoleAPI.retryBatchDelete"
      @changed="handleQuery"
    />
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
import BatchDeleteResultDialog from "@/components/BatchDeleteResultDialog/index.vue";
import PageShell from "@/components/PageShell/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import { runExclusive } from "@/utils/exclusive-action";
import { createLogger } from "@/utils/logger";

import RoleAPI, { RolePageQuery, RolePageVO } from "@/api/system/role-api";
import type { BatchDeleteResult } from "@/api/system/batch-delete";
import RoleFormDrawer from "./components/RoleFormDrawer.vue";
import RolePermissionDrawer from "./components/RolePermissionDrawer.vue";

const roleBatchDeleteLogger = createLogger("RoleBatchDelete");
defineOptions({
  name: "Role",
  inheritAttrs: false,
});

const queryFormRef = ref<InstanceType<typeof ProSearch> | null>(null);
const roleFormDrawerRef = ref<InstanceType<typeof RoleFormDrawer> | null>(null);
const rolePermissionDrawerRef = ref<InstanceType<typeof RolePermissionDrawer> | null>(null);
const batchDeleteResultDialogRef = ref<InstanceType<typeof BatchDeleteResultDialog> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const loading = ref(false);
const ids = ref<number[]>([]);

const queryParams = reactive<Omit<RolePageQuery, "pageNum" | "pageSize">>({});

const requestTableData = createPageRequest<RolePageQuery, RolePageVO>(RoleAPI.getPage);

// 查询（重置页码后获取数据）
function handleQuery() {
  tableRef.value?.reload(true);
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  tableRef.value?.reload(true);
}

// 行复选框选中
function handleSelectionChange(selection: unknown[]) {
  const rows = selection as RolePageVO[];
  ids.value = rows.map((item) => Number(item.id)).filter((id) => !Number.isNaN(id));
}

async function handleOpenDialog(roleId?: string) {
  if (roleId) {
    await roleFormDrawerRef.value?.openEdit(roleId);
    return;
  }

  await roleFormDrawerRef.value?.openCreate();
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

// 删除角色
function handleDelete(roleId?: number) {
  const roleIds = roleId !== undefined ? [roleId] : ids.value;
  if (roleIds.length === 0) {
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
      presentBatchDeleteResult(await RoleAPI.deleteByIds(roleIds));
    } catch (error: unknown) {
      // 请求拦截器负责用户提示，这里保留页面侧错误上下文并消费拒绝。
      roleBatchDeleteLogger.error("批量删除失败:", error);
    }
  });
}

async function handleOpenAssignPermDialog(row: RolePageVO) {
  await rolePermissionDrawerRef.value?.open(row);
}
</script>
