<!-- 用户管理 -->
<template>
  <PageShell class="ff-user-page">
    <div class="ff-user-page__grid">
      <aside class="ff-side-panel">
        <button
          v-if="isCompact"
          type="button"
          class="ff-user-page__dept-toggle"
          :aria-expanded="deptFilterOpen"
          aria-controls="user-department-filter"
          @click="deptFilterOpen = !deptFilterOpen"
        >
          <span>{{ selectedDepartment || t("user.department") }}</span>
          <AppIcon :name="deptFilterOpen ? 'chevron-up' : 'chevron-down'" :size="18" />
        </button>
        <DeptTree
          v-show="!isCompact || deptFilterOpen"
          id="user-department-filter"
          v-model="queryParams.deptId"
          class="ff-user-page__dept-tree"
          @node-click="handleDepartmentQuery"
        />
      </aside>

      <section class="ff-user-page__main">
        <ProSearch
          ref="queryFormRef"
          :model="queryParams"
          @submit="handleQuery"
          @reset="handleResetQuery"
        >
          <el-form-item :label="t('user.keyword')" prop="search">
            <el-input
              v-model="queryParams.search"
              :placeholder="t('user.searchPlaceholder')"
              clearable
              @keyup.enter="handleQuery"
            />
          </el-form-item>

          <el-form-item :label="t('user.status')" prop="isActive">
            <el-select
              v-model="queryParams.isActive"
              :placeholder="t('user.all')"
              clearable
              style="width: 100px"
            >
              <el-option :label="t('user.active')" :value="1" />
              <el-option :label="t('user.inactive')" :value="0" />
            </el-select>
          </el-form-item>
        </ProSearch>

        <ProTable
          ref="tableRef"
          :title="t('user.title')"
          :request="requestTableData"
          :params="queryParams"
          @selection-change="handleSelectionChange"
        >
          <template #actions>
            <div class="ff-button-group">
              <el-button
                v-hasPerm="['system:users:add']"
                type="primary"
                :icon="resolveAppIcon('plus')"
                class="ff-button-primary"
                @click="handleOpenDialog()"
              >
                {{ t("user.create") }}
              </el-button>
              <el-button
                v-hasPerm="['system:users:import']"
                :icon="resolveAppIcon('upload')"
                @click="importDialogVisible = true"
              >
                {{ t("user.import") }}
              </el-button>
              <el-button
                v-hasPerm="['system:users:export']"
                :icon="resolveAppIcon('download')"
                :loading="exporting"
                @click="handleExport"
              >
                {{ t("user.export") }}
              </el-button>
              <el-button
                v-hasPerm="['system:users:delete']"
                type="danger"
                plain
                :icon="resolveAppIcon('delete')"
                class="ff-button-danger"
                :loading="loading"
                :disabled="selectIds.length === 0 || loading"
                @click="handleDelete()"
              >
                {{ t("user.batchDelete") }}
              </el-button>
            </div>
          </template>

          <template #default>
            <el-table-column v-if="canDelete" type="selection" width="50" align="center" />
            <el-table-column
              :label="t('user.username')"
              prop="username"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column
              :label="t('user.name')"
              width="120"
              align="center"
              prop="name"
              show-overflow-tooltip
            />
            <el-table-column
              :label="t('user.department')"
              width="120"
              align="center"
              prop="deptName"
              show-overflow-tooltip
            />
            <el-table-column :label="t('user.mobile')" align="center" prop="mobile" width="120" />
            <el-table-column
              :label="t('user.email')"
              align="center"
              prop="email"
              min-width="190"
              show-overflow-tooltip
            />
            <el-table-column :label="t('user.status')" align="center" prop="isActive" width="80">
              <template #default="scope">
                <UserStatusTag :value="scope.row.isActive" />
              </template>
            </el-table-column>
            <el-table-column
              v-if="canManageUser"
              :label="t('user.actions')"
              fixed="right"
              width="280"
            >
              <template #default="scope">
                <el-button
                  v-hasPerm="'system:users:password:reset'"
                  type="primary"
                  :icon="resolveAppIcon('RefreshLeft')"
                  size="small"
                  link
                  @click="hancleResetPassword(scope.row)"
                >
                  {{ t("user.resetPassword") }}
                </el-button>
                <el-button
                  v-hasPerm="'system:users:edit'"
                  type="primary"
                  :icon="resolveAppIcon('edit')"
                  link
                  size="small"
                  @click="handleOpenDialog(scope.row.id)"
                >
                  {{ t("user.edit") }}
                </el-button>
                <el-button
                  v-hasPerm="'system:users:delete'"
                  type="danger"
                  :icon="resolveAppIcon('delete')"
                  link
                  :loading="loading"
                  :disabled="loading"
                  size="small"
                  @click="handleDelete(scope.row.id)"
                >
                  {{ t("user.delete") }}
                </el-button>
              </template>
            </el-table-column>
          </template>
        </ProTable>
      </section>
    </div>

    <UserFormDrawer ref="userFormDrawerRef" @success="handleQuery" />

    <UserImport
      v-model="importDialogVisible"
      :dept-id="queryParams.deptId"
      @import-success="handleQuery()"
    />

    <BatchDeleteResultDialog
      ref="batchDeleteResultDialogRef"
      :retry-action="UserAPI.retryBatchDelete"
      @changed="handleQuery"
    />
  </PageShell>
</template>

<script setup lang="ts">
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
import AppIcon from "@/components/AppIcon/index.vue";
import { useMediaQuery } from "@vueuse/core";
import { hasPerm } from "@/utils/auth";
import BatchDeleteResultDialog from "@/components/BatchDeleteResultDialog/index.vue";
import PageShell from "@/components/PageShell/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import { runExclusive } from "@/utils/exclusive-action";
import { downloadEncodedFile } from "@/utils/file-download";
import { createLogger } from "@/utils/logger";
import { passwordLengthError } from "@/utils/password-policy";
import InformationAPI from "@/api/information-api";

import type { UserInfo } from "@/api/auth-api";
import type { BatchDeleteResult } from "@/api/system/batch-delete";
import UserAPI, { UserPageQuery, UserPageVO } from "@/api/system/user-api";

import DeptTree from "./components/DeptTree.vue";
import UserImport from "./components/UserImport.vue";
import UserFormDrawer from "./components/UserFormDrawer.vue";
import UserStatusTag from "./components/UserStatusTag.vue";
import { useUserStore } from "@/store";
const userBatchDeleteLogger = createLogger("UserBatchDelete");
const userStore = useUserStore();
const { t } = useI18n();
const isCompact = useMediaQuery("(max-width: 1023px)");
const deptFilterOpen = ref(false);
const selectedDepartment = ref("");
const canDelete = computed(() => hasPerm("system:users:delete"));
const canManageUser = computed(() =>
  hasPerm(["system:users:password:reset", "system:users:edit", "system:users:delete"])
);
defineOptions({
  name: "User",
  inheritAttrs: false,
});

const queryFormRef = ref<InstanceType<typeof ProSearch> | null>(null);
const userFormDrawerRef = ref<InstanceType<typeof UserFormDrawer> | null>(null);
const batchDeleteResultDialogRef = ref<InstanceType<typeof BatchDeleteResultDialog> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const queryParams = reactive<Omit<UserPageQuery, "pageNum" | "pageSize">>({});

const loading = ref(false);
const exporting = ref(false);

// 选中的用户ID
const selectIds = ref<string[]>([]);
// 导入弹窗显示状态
const importDialogVisible = ref(false);

async function handleExport() {
  exporting.value = true;
  try {
    downloadEncodedFile(await UserAPI.export());
    ElMessage.success(t("user.exportSuccess"));
  } finally {
    exporting.value = false;
  }
}

const requestTableData = createPageRequest<UserPageQuery, UserPageVO>(UserAPI.getPage);

// 查询（重置页码后获取数据）
function handleQuery() {
  tableRef.value?.reload(true);
}

function handleDepartmentQuery(label?: string) {
  selectedDepartment.value = label ?? "";
  deptFilterOpen.value = false;
  handleQuery();
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  queryParams.deptId = undefined;
  selectedDepartment.value = "";
  tableRef.value?.reload(true);
}

// 选中项发生变化
function handleSelectionChange(selection: unknown[]) {
  const rows = selection as UserPageVO[];
  selectIds.value = rows.map((item) => item.id).filter((id): id is string => Boolean(id));
}

// 重置密码
async function hancleResetPassword(row: UserPageVO) {
  let policy;
  try {
    policy = await InformationAPI.getPasswordPolicy();
  } catch {
    return;
  }
  ElMessageBox.prompt(
    t("user.resetPasswordPrompt", { username: row.username }),
    t("user.resetPassword"),
    {
      confirmButtonText: t("user.confirm"),
      cancelButtonText: t("user.cancel"),
      inputType: "password",
      inputValidator: (value) =>
        passwordLengthError(value ?? "", policy, {
          policyUnavailable: t("user.passwordPolicyUnavailable"),
          invalidLength: (min, max) => t("user.passwordLength", { min, max }),
        }) ?? true,
    }
  ).then(
    ({ value }) => {
      UserAPI.resetPassword(row.id, value, value).then(() => {
        ElMessage.success(t("user.resetPasswordSuccess"));
      });
    },
    () => {
      ElMessage.info(t("user.resetPasswordCanceled"));
    }
  );
}

/**
 * 打开弹窗
 *
 * @param id 用户ID
 */
async function handleOpenDialog(id?: string) {
  if (id) {
    await userFormDrawerRef.value?.openEdit(id);
  } else {
    await userFormDrawerRef.value?.openCreate();
  }
}

/**
 * 检查是否删除当前登录用户
 * @param singleId 单个删除的用户ID
 * @param selectedIds 批量删除的用户ID数组
 * @param currentUserInfo 当前用户信息
 * @returns 是否包含当前用户
 */
function isDeletingCurrentUser(
  singleId?: string,
  selectedIds: string[] = [],
  currentUserInfo?: Pick<UserInfo, "id">
): boolean {
  const currentUserId = currentUserInfo?.id;
  if (!currentUserId) return false;

  // 单个删除检查
  if (singleId && singleId === currentUserId) {
    return true;
  }

  // 批量删除检查
  if (!singleId && selectedIds.length > 0) {
    return selectedIds.includes(currentUserId);
  }

  return false;
}

function presentBatchDeleteResult(result: BatchDeleteResult) {
  if (result.successCount > 0) {
    tableRef.value?.reload(true);
  }

  if (result.failedCount === 0) {
    ElMessage.success(t("user.batchDeleteSuccess", { count: result.successCount }));
    return;
  }

  const message = t("user.batchDeleteSummary", {
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

/**
 * 删除用户
 *
 * @param id  用户ID
 */
function handleDelete(id?: string) {
  const userIds = id !== undefined ? [id] : selectIds.value;
  if (userIds.length === 0) {
    ElMessage.warning(t("user.selectDeleteItems"));
    return;
  }

  // 安全检查：防止删除当前登录用户
  const currentUserInfo = userStore.userInfo;
  if (isDeletingCurrentUser(id, selectIds.value, currentUserInfo)) {
    ElMessage.error(t("user.cannotDeleteCurrentUser"));
    return;
  }

  void runExclusive(loading, async () => {
    try {
      await ElMessageBox.confirm(t("user.deleteConfirm"), t("user.warning"), {
        confirmButtonText: t("user.confirm"),
        cancelButtonText: t("user.cancel"),
        type: "warning",
      });
    } catch {
      ElMessage.info(t("user.deleteCanceled"));
      return;
    }

    try {
      presentBatchDeleteResult(await UserAPI.deleteByIds(userIds));
    } catch (error: unknown) {
      // 请求拦截器负责用户提示，这里保留页面侧错误上下文并消费拒绝。
      userBatchDeleteLogger.error("批量删除失败:", error);
    }
  });
}
</script>
