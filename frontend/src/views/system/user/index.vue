<!-- 用户管理 -->
<template>
  <div class="app-container p-4 md:p-6 flex flex-col gap-4">
    <el-row :gutter="16" class="flex-1 h-full">
      <el-col :lg="4" :xs="24" class="mb-4 lg:mb-0">
        <div class="glass-panel h-full p-4">
          <DeptTree v-model="queryParams.deptId" @node-click="handleQuery" class="transparent-tree" />
        </div>
      </el-col>

      <el-col :lg="20" :xs="24" class="flex flex-col gap-4 h-full">
        <div class="glass-panel p-5">
          <el-form ref="queryFormRef" :model="queryParams" :inline="true" class="minimal-form mb-0">
            <el-form-item label="关键字" prop="search" class="mb-0">
              <el-input
                v-model="queryParams.search"
                placeholder="用户名/昵称/手机号"
                clearable
                class="minimal-input"
                @keyup.enter="handleQuery"
              />
            </el-form-item>

            <el-form-item label="状态" prop="isActive" class="mb-0">
              <el-select
                v-model="queryParams.isActive"
                placeholder="全部"
                clearable
                class="minimal-input"
                style="width: 100px"
              >
                <el-option label="正常" :value="1" />
                <el-option label="禁用" :value="0" />
              </el-select>
            </el-form-item>

            <el-form-item class="search-buttons mb-0 ml-auto">
              <el-button type="primary" icon="search" class="minimal-btn" @click="handleQuery">搜索</el-button>
              <el-button icon="refresh" class="minimal-btn-plain" @click="handleResetQuery">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="glass-panel p-5 flex-1 flex flex-col overflow-hidden">
          <div class="flex justify-between items-center mb-4">
            <div class="flex items-center gap-2">
              <div class="w-1.5 h-4 bg-primary rounded-full"></div>
              <span class="text-base font-semibold text-slate-700 tracking-wide">用户数据</span>
            </div>
            <div class="flex gap-2">
              <el-button
                v-hasPerm="['system:users:add']"
                type="primary"
                icon="plus"
                class="minimal-btn"
                @click="handleOpenDialog()"
              >新增用户</el-button>
              <el-button
                v-hasPerm="['system:users:delete']"
                type="danger"
                plain
                icon="delete"
                class="minimal-btn-danger"
                :disabled="selectIds.length === 0"
                @click="handleDelete()"
              >批量删除</el-button>
            </div>
          </div>

          <div class="flex-1 overflow-hidden border border-slate-100/50 rounded-xl bg-white/20">
            <el-table
              v-loading="loading"
              :data="pageData"
              highlight-current-row
              class="minimal-table"
              @selection-change="handleSelectionChange"
            >
              <el-table-column type="selection" width="50" align="center" />
              <el-table-column label="用户名" prop="username" />
              <el-table-column label="昵称" width="150" align="center" prop="name" />
              <el-table-column label="部门" width="120" align="center" prop="deptName" />
              <el-table-column label="手机号码" align="center" prop="mobile" width="120" />
              <el-table-column label="邮箱" align="center" prop="email" min-width="160" />
              <el-table-column label="状态" align="center" prop="isActive" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.isActive === 1 ? 'success' : 'info'" class="minimal-tag" :class="scope.row.isActive === 1 ? 'success' : 'info'">
                    {{ scope.row.isActive === 1 ? "正常" : "禁用" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" fixed="right" width="280">
                <template #default="scope">
                  <el-button v-hasPerm="'system:users:password:reset'" type="primary" icon="RefreshLeft" size="small" link @click="hancleResetPassword(scope.row)">重置密码</el-button>
                  <el-button v-hasPerm="'system:users:edit'" type="primary" icon="edit" link size="small" @click="handleOpenDialog(scope.row.id)">编辑</el-button>
                  <el-button v-hasPerm="'system:users:delete'" type="danger" icon="delete" link size="small" @click="handleDelete(scope.row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <pagination
            v-if="total > 0"
            v-model:total="total"
            v-model:page="queryParams.pageNum"
            v-model:limit="queryParams.pageSize"
            class="minimal-pagination mt-4"
            @pagination="fetchData"
          />
        </div>
      </el-col>
    </el-row>

    <el-drawer
      v-model="dialog.visible"
      :title="dialog.title"
      append-to-body
      class="glass-drawer"
      :size="drawerSize"
      @close="handleCloseDialog"
    >
      <el-form ref="userFormRef" v-loading="formLoading" :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" :readonly="!!formData.id" placeholder="请输入用户名" class="minimal-input" />
        </el-form-item>
        <el-form-item label="用户昵称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入用户昵称" class="minimal-input" />
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
            class="minimal-input w-full"
          />
        </el-form-item>
        <el-form-item label="角色" prop="roles">
          <el-select v-model="formData.roles" multiple placeholder="请选择" class="minimal-input w-full">
            <el-option v-for="item in roleOptions" :key="item.id" :label="item.label" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号码" prop="mobile">
          <el-input v-model="formData.mobile" placeholder="请输入手机号码" maxlength="11" class="minimal-input" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" maxlength="50" class="minimal-input" />
        </el-form-item>
        <el-form-item label="状态" prop="isActive">
          <el-switch v-model="formData.isActive" inline-prompt active-text="正常" inactive-text="禁用" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="handleCloseDialog">取 消</el-button>
          <el-button type="primary" class="minimal-btn" :loading="formLoading" @click="handleSubmitWrapper">确 定</el-button>
        </div>
      </template>
    </el-drawer>

    <UserImport v-model="importDialogVisible" @import-success="handleQuery()" />
  </div>
</template>

<script setup lang="ts">
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

<style scoped lang="scss">
/* stylelint-disable no-descending-specificity no-duplicate-selectors */
/* 玻璃面板样式 */
.glass-panel {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px) saturate(110%);
  -webkit-backdrop-filter: blur(12px) saturate(110%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.glass-panel:hover {
  box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.08);
}

/* 透明树组件 */
.transparent-tree {
  :deep(.el-tree) {
    background: transparent !important;
  }
}

/* 玻璃抽屉样式 */
:deep(.glass-drawer) {
  .el-drawer__header {
    border-bottom: 1px solid #f1f5f9;
    margin-bottom: 0;
    padding: 16px 20px;
  }

  .el-drawer__title {
    font-weight: 600;
    color: #1e293b;
  }

  .el-drawer__body {
    padding: 20px;
  }

  .el-drawer__footer {
    border-top: 1px solid #f1f5f9;
    padding: 16px 20px;
  }
}

/* 深色模式 */
html.dark {
  .glass-panel {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.3);
  }

  :deep(.glass-drawer) {
    .el-drawer__header {
      border-bottom-color: #334155;
    }

    .el-drawer__title {
      color: #f1f5f9;
    }

    .el-drawer__footer {
      border-top-color: #334155;
    }
  }
}

/* ==================== 浮岛式毛玻璃面板 ==================== */
.glass-panel {
  background: rgba(255, 255, 255, 0.6) !important; /* 半透明白底，透出底色的冷岩灰 */
  backdrop-filter: blur(16px) saturate(120%);
  -webkit-backdrop-filter: blur(16px) saturate(120%);
  border: 1px solid rgba(255, 255, 255, 0.8) !important; /* 玻璃高光边缘 */
  box-shadow: 0 8px 32px -8px rgba(0, 0, 0, 0.05) !important;
  border-radius: 16px;
  transition: all 0.3s ease;
}
.glass-panel:hover {
  box-shadow: 0 12px 48px -12px rgba(0, 0, 0, 0.08) !important;
}

/* ==================== 强行穿透左侧部门树 ==================== */
/* 去除原生 el-card / el-tree 的自带白底，让它融入毛玻璃 */
:deep(.transparent-tree),
:deep(.transparent-tree .el-tree),
:deep(.transparent-tree .el-card) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
:deep(.transparent-tree .el-tree-node__content) {
  border-radius: 8px;
  margin-bottom: 2px;
  transition: all 0.2s;
}
:deep(.transparent-tree .el-tree-node__content:hover) {
  background-color: rgba(64, 128, 255, 0.08) !important;
}
:deep(.transparent-tree .el-tree-node.is-current > .el-tree-node__content) {
  background-color: rgba(64, 128, 255, 0.15) !important;
  color: var(--el-color-primary);
  font-weight: 600;
}

/* ==================== 极简 SaaS 风深度定制 ==================== */
/* 1. 表格净化 */
:deep(.minimal-table) {
  background: transparent !important;
  --el-table-border-color: rgba(0,0,0,0.04);
  --el-table-header-bg-color: rgba(0,0,0,0.02);
  --el-table-header-text-color: #475569;
  --el-table-row-hover-bg-color: rgba(255,255,255,0.6);
  --el-table-tr-bg-color: transparent;
}
:deep(.minimal-table th.el-table__cell) {
  font-weight: 600;
  border-bottom: 2px solid rgba(0,0,0,0.06) !important;
}
:deep(.minimal-table td.el-table__cell) {
  border-bottom: 1px dashed rgba(0,0,0,0.04) !important;
}
:deep(.minimal-table .el-table__inner-wrapper::before) {
  display: none; /* 隐藏底部死黑边线 */
}

/* 2. 表单输入框圆润化 */
:deep(.minimal-input .el-input__wrapper),
:deep(.minimal-input.el-select .el-select__wrapper) {
  box-shadow: 0 0 0 1px #cbd5e1 inset !important;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.6); /* 搜索框也做半透明 */
  transition: all 0.2s ease;
}
:deep(.minimal-input .el-input__wrapper.is-focus),
:deep(.minimal-input.el-select .el-select__wrapper.is-focus) {
  background-color: #ffffff;
  box-shadow: 0 0 0 1px var(--el-color-primary) inset, 0 0 0 3px rgba(64, 128, 255, 0.1) !important;
}

/* 3. 按钮与标签高级感 */
.minimal-btn {
  border-radius: 8px;
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 4px rgba(64, 128, 255, 0.2);
  transition: all 0.2s ease;
}
.minimal-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(64, 128, 255, 0.3);
}
.minimal-btn-plain {
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  color: #64748b;
  background: rgba(255, 255, 255, 0.6);
}
.minimal-btn-plain:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: #ffffff;
}

.minimal-tag {
  border: none !important;
  border-radius: 6px;
  padding: 0 12px;
  font-weight: 500;
}
.minimal-tag.success { background-color: #dcfce7 !important; color: #16a34a !important; }
.minimal-tag.info { background-color: #f1f5f9 !important; color: #64748b !important; }

/* 4. 分页组件融化 */
:deep(.minimal-pagination) {
  justify-content: flex-end;
}
:deep(.minimal-pagination button), :deep(.minimal-pagination li) {
  background: transparent !important;
}
:deep(.minimal-pagination li.is-active) {
  background: var(--el-color-primary) !important;
  color: white !important;
  border-radius: 6px;
}

/* ==================== 5. 表格内操作按钮"软徽章化" ==================== */
:deep(.minimal-table .el-button.is-link) {
  padding: 6px 10px !important; /* 撑开点击热区，操作更舒服 */
  border-radius: 8px !important; /* 呼应全局的胶囊圆角 */
  font-weight: 500 !important;
  height: auto !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Primary 按钮（编辑、重置密码）的悬浮效果 */
:deep(.minimal-table .el-button--primary.is-link) {
  color: #64748b !important; /* 默认状态下稍微降低一点存在感，用深蓝灰色 */
}
:deep(.minimal-table .el-button--primary.is-link:hover) {
  background-color: rgba(64, 128, 255, 0.1) !important; /* 浮现极淡的主题色底色 */
  color: var(--el-color-primary) !important; /* 文字亮起 */
}

/* Danger 按钮（删除）的悬浮效果 */
:deep(.minimal-table .el-button--danger.is-link) {
  color: #94a3b8 !important; /* 默认状态下隐藏杀机 */
}
:deep(.minimal-table .el-button--danger.is-link:hover) {
  background-color: rgba(239, 68, 68, 0.1) !important; /* 浮现极淡的危险红底色 */
  color: #ef4444 !important; /* 文字变红警示 */
}

/* 调整按钮之间的间距 */
:deep(.minimal-table .el-table__cell .cell) {
  display: flex;
  align-items: center;
  gap: 4px; /* 让按钮之间有均匀的呼吸缝隙 */
}
</style>
