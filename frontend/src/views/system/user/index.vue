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
          title="用户数据"
          :loading="loading"
          :data="pageData"
          :total="total"
          :page="queryParams.pageNum"
          :limit="queryParams.pageSize"
          @update:page="queryParams.pageNum = $event"
          @update:limit="queryParams.pageSize = $event"
          @pagination="fetchData"
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

    <ProFormDrawer
      ref="userFormRef"
      v-model="dialog.visible"
      :title="dialog.title"
      :model="formData"
      :rules="rules"
      :loading="formLoading"
      :size="drawerSize"
      @submit="handleSubmitWrapper"
      @close="handleCloseDialog"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="formData.username"
          :readonly="!!formData.id"
          placeholder="请输入用户名"
        />
      </el-form-item>
      <el-form-item label="用户昵称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入用户昵称" />
      </el-form-item>
      <el-form-item label="所属部门" prop="deptId">
        <el-tree-select
          v-model="formData.deptId"
          placeholder="请选择所属部门"
          :data="deptOptions"
          node-key="id"
          filterable
          check-strictly
          :render-after-expand="false"
          class="w-full"
        />
      </el-form-item>
      <el-form-item label="角色" prop="roles">
        <el-select v-model="formData.roles" multiple placeholder="请选择" class="w-full">
          <el-option
            v-for="item in roleOptions"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="手机号码" prop="mobile">
        <el-input v-model="formData.mobile" placeholder="请输入手机号码" maxlength="11" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="formData.email" placeholder="请输入邮箱" maxlength="50" />
      </el-form-item>
      <el-form-item label="状态" prop="isActive">
        <el-switch
          v-model="formData.isActive"
          inline-prompt
          active-text="正常"
          inactive-text="禁用"
          :active-value="1"
          :inactive-value="0"
        />
      </el-form-item>
    </ProFormDrawer>

    <UserImport v-model="importDialogVisible" @import-success="handleQuery()" />
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import { useAppStore } from "@/store/modules/app-store";
import { DeviceEnum } from "@/enums/settings/device-enum";

import UserAPI, { UserForm, UserPageQuery, UserPageVO } from "@/api/system/user-api";
import DeptAPI from "@/api/system/dept-api";
import RoleAPI from "@/api/system/role-api";

import DeptTree from "./components/DeptTree.vue";
import UserImport from "./components/UserImport.vue";
import { useUserStore } from "@/store";
const userStore = useUserStore();
defineOptions({
  name: "User",
  inheritAttrs: false,
});

const appStore = useAppStore();

const queryFormRef = ref();
const userFormRef = ref();

const queryParams = reactive<UserPageQuery>({
  pageNum: 1,
  pageSize: 10,
});

const pageData = ref<UserPageVO[]>();
const total = ref(0);
const loading = ref(false);
const formLoading = ref(false);

const dialog = reactive({
  visible: false,
  title: "新增用户",
});
const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const formData = reactive<UserForm>({
  isActive: 1,
});

const rules = reactive({
  username: [{ required: true, message: "用户名不能为空", trigger: "blur" }],
  name: [{ required: true, message: "用户昵称不能为空", trigger: "blur" }],
  deptId: [{ required: true, message: "所属部门不能为空", trigger: "blur" }],
  roles: [{ required: true, message: "用户角色不能为空", trigger: "blur" }],
  email: [
    {
      pattern: /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/,
      message: "请输入正确的邮箱地址",
      trigger: "blur",
    },
  ],
  mobile: [
    {
      pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/,
      message: "请输入正确的手机号码",
      trigger: "blur",
    },
  ],
});

// 选中的用户ID
const selectIds = ref<number[]>([]);
// 部门下拉数据源
const deptOptions = ref<OptionType[]>();
// 角色下拉数据源
const roleOptions = ref<OptionType[]>();
// 导入弹窗显示状态
const importDialogVisible = ref(false);

// 获取数据
async function fetchData() {
  loading.value = true;
  try {
    const data = await UserAPI.getPage(queryParams);
    pageData.value = data.list;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

// 查询（重置页码后获取数据）
function handleQuery() {
  queryParams.pageNum = 1;
  fetchData();
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryParams.pageNum = 1;
  queryParams.deptId = undefined;
  fetchData();
}

// 选中项发生变化
function handleSelectionChange(selection: any[]) {
  selectIds.value = selection.map((item) => item.id);
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
      UserAPI.resetPassword(row.id, value).then(() => {
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
  dialog.visible = true;
  // 加载角色下拉数据源
  roleOptions.value = await RoleAPI.getOptions();
  // 加载部门下拉数据源
  deptOptions.value = await DeptAPI.getOptions();

  if (id) {
    dialog.title = "修改用户";
    UserAPI.getFormData(id).then((data) => {
      Object.assign(formData, { ...data });
    });
  } else {
    dialog.title = "新增用户";
  }
}

// 关闭弹窗
function handleCloseDialog() {
  dialog.visible = false;
  userFormRef.value.resetFields();
  userFormRef.value.clearValidate();

  formData.id = undefined;
  formData.deptId = undefined;
  formData.isActive = 1;
}

// 提交用户表单（防抖）
const handleSubmit = useDebounceFn(() => {
  userFormRef.value.validate((valid: boolean) => {
    if (valid) {
      const userId = formData.id;
      if (userId) {
        UserAPI.update(userId, formData)
          .then(() => {
            ElMessage.success("修改用户成功");
            handleCloseDialog();
            handleResetQuery();
          })
          .finally(() => (formLoading.value = false));
      } else {
        UserAPI.create(formData)
          .then(() => {
            ElMessage.success("新增用户成功");
            handleCloseDialog();
            handleResetQuery();
          })
          .finally(() => (formLoading.value = false));
      }
    } else {
      // 验证失败时也要重置loading状态
      formLoading.value = false;
    }
  });
}, 300);

// 立即设置loading状态的包装函数
function handleSubmitWrapper() {
  formLoading.value = true;
  handleSubmit();
}

/**
 * 检查是否删除当前登录用户
 * @param singleId 单个删除的用户ID
 * @param selectedIds 批量删除的用户ID数组
 * @param currentUserInfo 当前用户信息
 * @returns 是否包含当前用户
 */
function isDeletingCurrentUser(
  singleId?: number,
  selectedIds: number[] = [],
  currentUserInfo?: any
): boolean {
  if (!currentUserInfo?.userId) return false;

  // 单个删除检查
  if (singleId && singleId.toString() === currentUserInfo.userId) {
    return true;
  }

  // 批量删除检查
  if (!singleId && selectedIds.length > 0) {
    return selectedIds.map(String).includes(currentUserInfo.userId);
  }

  return false;
}

/**
 * 删除用户
 *
 * @param id  用户ID
 */
function handleDelete(id?: number) {
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
          handleResetQuery();
        })
        .finally(() => (loading.value = false));
    },
    () => {
      ElMessage.info("已取消删除");
    }
  );
}

onMounted(() => {
  handleQuery();
});
</script>
