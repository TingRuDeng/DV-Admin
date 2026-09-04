<template>
  <PageShell class="ff-role-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item prop="search" label="关键字">
        <el-input
          v-model="queryParams.search"
          placeholder="角色名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      title="角色数据"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:roles:add']"
            type="primary"
            icon="plus"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            新增角色
          </el-button>
          <el-button
            v-hasPerm="['system:roles:delete']"
            type="danger"
            plain
            :loading="loading"
            :disabled="ids.length === 0 || loading"
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
        <el-table-column label="排序" align="center" width="80" prop="sort">
          <template #default="{ row }">
            <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">
              {{ row.sort }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="角色名称" prop="name" min-width="100" />
        <el-table-column label="状态" align="center" width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === 1 ? 'success' : 'info'"
              class="ff-status-tag"
              :class="scope.row.status === 1 ? 'success' : 'info'"
            >
              {{ scope.row.status === 1 ? "正常" : "禁用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="是否默认角色" align="center" width="120">
          <template #default="scope">
            <el-tag
              :type="scope.row.isDefault ? 'success' : 'info'"
              class="ff-status-tag"
              :class="scope.row.isDefault ? 'success' : 'info'"
            >
              {{ scope.row.isDefault ? "是" : "否" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" prop="desc" min-width="200" />
        <el-table-column fixed="right" label="操作" width="280">
          <template #default="scope">
            <el-button
              v-hasPerm="'system:roles:edit'"
              type="primary"
              link
              icon="position"
              size="small"
              @click="handleOpenAssignPermDialog(scope.row)"
            >
              分配权限
            </el-button>
            <el-button
              v-hasPerm="'system:roles:edit'"
              type="primary"
              link
              icon="edit"
              size="small"
              @click="handleOpenDialog(scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="'system:roles:delete'"
              type="danger"
              link
              icon="delete"
              :loading="loading"
              :disabled="loading"
              size="small"
              @click="handleDelete(scope.row.id)"
            >
              删除
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
    ElMessage.success(`删除成功，共 ${result.successCount} 条`);
    return;
  }

  const message = `删除完成：成功 ${result.successCount} 条，失败 ${result.failedCount} 条`;
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
    ElMessage.warning("请勾选删除项");
    return;
  }

  void runExclusive(loading, async () => {
    try {
      await ElMessageBox.confirm("确认删除已选中的数据项?", "警告", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      });
    } catch {
      ElMessage.info("已取消删除");
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
