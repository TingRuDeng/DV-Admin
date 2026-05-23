<!-- 用户管理 -->
<template>
  <PageShell class="ff-user-page">
    <div class="ff-user-page__grid">
      <aside class="ff-side-panel">
        <DeptTree
          v-model="queryParams.deptId"
          class="ff-user-page__dept-tree"
          @node-click="handleQuery"
        />
      </aside>

      <section class="ff-user-page__main">
        <ProSearch
          ref="queryFormRef"
          :model="queryParams"
          @submit="handleQuery"
          @reset="handleResetQuery"
        >
          <el-form-item label="关键字" prop="search">
            <el-input
              v-model="queryParams.search"
              placeholder="用户名/昵称/手机号"
              clearable
              @keyup.enter="handleQuery"
            />
          </el-form-item>

          <el-form-item label="状态" prop="isActive">
            <el-select
              v-model="queryParams.isActive"
              placeholder="全部"
              clearable
              style="width: 100px"
            >
              <el-option label="正常" :value="1" />
              <el-option label="禁用" :value="0" />
            </el-select>
          </el-form-item>
        </ProSearch>

        <ProTable
          ref="tableRef"
          title="用户数据"
          :request="requestTableData"
          :params="queryParams"
          @selection-change="handleSelectionChange"
        >
          <template #actions>
            <div class="ff-button-group">
              <el-button
                v-hasPerm="['system:users:add']"
                type="primary"
                icon="plus"
                class="ff-button-primary"
                @click="handleOpenDialog()"
              >
                新增用户
              </el-button>
              <el-button
                v-hasPerm="['system:users:delete']"
                type="danger"
                plain
                icon="delete"
                class="ff-button-danger"
                :disabled="selectIds.length === 0"
                @click="handleDelete()"
              >
                批量删除
              </el-button>
            </div>
          </template>

          <template #default>
            <el-table-column type="selection" width="50" align="center" />
            <el-table-column label="用户名" prop="username" />
            <el-table-column label="昵称" width="150" align="center" prop="name" />
            <el-table-column label="部门" width="120" align="center" prop="deptName" />
            <el-table-column label="手机号码" align="center" prop="mobile" width="120" />
            <el-table-column label="邮箱" align="center" prop="email" min-width="160" />
            <el-table-column label="状态" align="center" prop="isActive" width="80">
              <template #default="scope">
                <el-tag
                  :type="scope.row.isActive === 1 ? 'success' : 'info'"
                  class="ff-status-tag"
                  :class="scope.row.isActive === 1 ? 'success' : 'info'"
                >
                  {{ scope.row.isActive === 1 ? "正常" : "禁用" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="280">
              <template #default="scope">
                <el-button
                  v-hasPerm="'system:users:password:reset'"
                  type="primary"
                  icon="RefreshLeft"
                  size="small"
                  link
                  @click="hancleResetPassword(scope.row)"
                >
                  重置密码
                </el-button>
                <el-button
                  v-hasPerm="'system:users:edit'"
                  type="primary"
                  icon="edit"
                  link
                  size="small"
                  @click="handleOpenDialog(scope.row.id)"
                >
                  编辑
                </el-button>
                <el-button
                  v-hasPerm="'system:users:delete'"
                  type="danger"
                  icon="delete"
                  link
                  size="small"
                  @click="handleDelete(scope.row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </template>
        </ProTable>
      </section>
    </div>

    <UserFormDrawer ref="userFormDrawerRef" @success="handleQuery" />

    <UserImport v-model="importDialogVisible" @import-success="handleQuery()" />
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";

import type { UserInfo } from "@/api/auth-api";
import UserAPI, { UserPageQuery, UserPageVO } from "@/api/system/user-api";

import DeptTree from "./components/DeptTree.vue";
import UserImport from "./components/UserImport.vue";
import UserFormDrawer from "./components/UserFormDrawer.vue";
import { useUserStore } from "@/store";
const userStore = useUserStore();
defineOptions({
  name: "User",
  inheritAttrs: false,
});

const queryFormRef = ref<InstanceType<typeof ProSearch> | null>(null);
const userFormDrawerRef = ref<InstanceType<typeof UserFormDrawer> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const queryParams = reactive<Omit<UserPageQuery, "pageNum" | "pageSize">>({});

const loading = ref(false);

// 选中的用户ID
const selectIds = ref<string[]>([]);
// 导入弹窗显示状态
const importDialogVisible = ref(false);

const requestTableData = createPageRequest<UserPageQuery, UserPageVO>(UserAPI.getPage);

// 查询（重置页码后获取数据）
function handleQuery() {
  tableRef.value?.reload(true);
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  queryParams.deptId = undefined;
  tableRef.value?.reload(true);
}

// 选中项发生变化
function handleSelectionChange(selection: unknown[]) {
  const rows = selection as UserPageVO[];
  selectIds.value = rows.map((item) => item.id).filter((id): id is string => Boolean(id));
}

// 重置密码
function hancleResetPassword(row: UserPageVO) {
  ElMessageBox.prompt("请输入用户【" + row.username + "】的新密码", "重置密码", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
  }).then(
    ({ value }) => {
      if (!value || value.length < 6) {
        ElMessage.warning("密码至少需要6位字符，请重新输入");
        return false;
      }
      UserAPI.resetPassword(row.id, value, value).then(() => {
        ElMessage.success("密码重置成功，新密码是：" + value);
      });
    },
    () => {
      ElMessage.info("已取消重置密码");
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

/**
 * 删除用户
 *
 * @param id  用户ID
 */
function handleDelete(id?: string) {
  const userIds = id !== undefined ? [id] : selectIds.value;
  if (!userIds) {
    ElMessage.warning("请勾选删除项");
    return;
  }

  // 安全检查：防止删除当前登录用户
  const currentUserInfo = userStore.userInfo;
  if (isDeletingCurrentUser(id, selectIds.value, currentUserInfo)) {
    ElMessage.error("不能删除当前登录用户");
    return;
  }

  ElMessageBox.confirm("确认删除用户?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(
    () => {
      loading.value = true;
      UserAPI.deleteByIds(userIds)
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
</script>
