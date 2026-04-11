<template>
  <div class="app-container p-4 md:p-6 flex flex-col gap-4">
    <!-- 搜索区域 -->
    <div class="glass-panel p-5">
      <el-form
        ref="queryFormRef"
        :model="queryParams"
        :inline="true"
        class="minimal-form mb-0"
        @submit.prevent
      >
        <el-form-item prop="search" label="关键字" class="mb-0">
          <el-input
            v-model="queryParams.search"
            placeholder="角色名称"
            clearable
            class="minimal-input"
            @keyup.enter="handleQuery"
          />
        </el-form-item>

        <el-form-item class="search-buttons mb-0 ml-auto">
          <el-button type="primary" icon="search" class="minimal-btn" @click="handleQuery">
            搜索
          </el-button>
          <el-button icon="refresh" class="minimal-btn-plain" @click="handleResetQuery">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="glass-panel p-5 flex-1 flex flex-col overflow-hidden">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-4 bg-primary rounded-full"></div>
          <span class="text-base font-semibold text-slate-700 tracking-wide">角色数据</span>
        </div>
        <div class="flex gap-2">
          <el-button type="primary" icon="plus" class="minimal-btn" @click="handleOpenDialog()">
            新增角色
          </el-button>
          <el-button
            type="danger"
            plain
            :disabled="ids.length === 0"
            icon="delete"
            class="minimal-btn-danger"
            @click="handleDelete()"
          >
            批量删除
          </el-button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden border border-slate-100/50 rounded-xl bg-white/20">
        <el-table
          ref="dataTableRef"
          v-loading="loading"
          :data="roleList"
          highlight-current-row
          class="minimal-table"
          @selection-change="handleSelectionChange"
        >
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
                class="minimal-tag"
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
                class="minimal-tag"
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
                type="primary"
                link
                icon="position"
                size="small"
                @click="handleOpenAssignPermDialog(scope.row)"
              >
                分配权限
              </el-button>
              <el-button
                type="primary"
                link
                icon="edit"
                size="small"
                @click="handleOpenDialog(scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                icon="delete"
                size="small"
                @click="handleDelete(scope.row.id)"
              >
                删除
              </el-button>
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

    <!-- 角色表单弹窗 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.title"
      width="500px"
      class="minimal-dialog"
      @close="handleCloseDialog"
    >
      <el-form
        ref="roleFormRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        class="minimal-form pt-4"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" class="minimal-input" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="是否默认" prop="isDefault">
          <el-radio-group v-model="formData.isDefault">
            <el-radio :value="1">是</el-radio>
            <el-radio :value="0">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number
            v-model="formData.sort"
            controls-position="right"
            :min="0"
            style="width: 100px"
            class="minimal-input"
          />
        </el-form-item>
        <el-form-item label="备注" prop="desc">
          <el-input
            v-model="formData.desc"
            placeholder="请输入角色备注"
            type="textarea"
            :rows="2"
            class="minimal-input"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="handleCloseDialog">取 消</el-button>
          <el-button type="primary" class="minimal-btn" @click="handleSubmit">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 分配权限弹窗 -->
    <el-drawer
      v-model="assignPermDialogVisible"
      :title="'【' + checkedRole.name + '】权限分配'"
      :size="drawerSize"
      class="glass-drawer"
    >
      <div class="flex justify-between items-center mb-5">
        <el-input
          v-model="permKeywords"
          clearable
          class="minimal-input w-[150px]"
          placeholder="菜单权限名称"
        >
          <template #prefix>
            <Search />
          </template>
        </el-input>

        <div class="flex items-center gap-3">
          <el-button type="primary" size="small" plain class="minimal-btn" @click="togglePermTree">
            <template #icon>
              <Switch />
            </template>
            {{ isExpanded ? "收缩" : "展开" }}
          </el-button>
          <el-checkbox v-model="parentChildLinked" @change="handleparentChildLinkedChange">
            父子联动
          </el-checkbox>
          <el-tooltip placement="bottom">
            <template #content>
              如果只需勾选菜单权限，不需要勾选子菜单或者按钮权限，请关闭父子联动
            </template>
            <el-icon class="text-primary cursor-pointer">
              <QuestionFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </div>

      <el-tree
        ref="permTreeRef"
        node-key="id"
        show-checkbox
        :data="menuPermOptions"
        :filter-node-method="handlePermFilter"
        :default-expand-all="true"
        :check-strictly="!parentChildLinked"
        class="permission-tree"
      >
        <template #default="{ data }">
          {{ data.label }}
        </template>
      </el-tree>
      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="assignPermDialogVisible = false">
            取 消
          </el-button>
          <el-button type="primary" class="minimal-btn" @click="handleAssignPermSubmit">
            确 定
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from "@/store/modules/app-store";
import { DeviceEnum } from "@/enums/settings/device-enum";

import RoleAPI, { RoleForm, RolePageQuery, RolePageVO } from "@/api/system/role-api";
import MenuAPI from "@/api/system/menu-api";

defineOptions({
  name: "Role",
  inheritAttrs: false,
});

const appStore = useAppStore();

const queryFormRef = ref();
const roleFormRef = ref();
const permTreeRef = ref();

const loading = ref(false);
const ids = ref<number[]>([]);
const total = ref(0);

const queryParams = reactive<RolePageQuery>({
  pageNum: 1,
  pageSize: 10,
});

// 角色表格数据
const roleList = ref<RolePageVO[]>();
// 菜单权限下拉
const menuPermOptions = ref<OptionType[]>([]);

// 弹窗
const dialog = reactive({
  title: "",
  visible: false,
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

// 角色表单
const formData = reactive<RoleForm>({
  sort: 1,
  status: 1,
  isDefault: 1, // 新增：是否默认角色字段，默认值为1（是）
});

const rules = reactive({
  name: [{ required: true, message: "请输入角色名称", trigger: "blur" }],
  code: [{ required: true, message: "请输入角色编码", trigger: "blur" }],
  dataScope: [{ required: true, message: "请选择数据权限", trigger: "blur" }],
  status: [{ required: true, message: "请选择状态", trigger: "blur" }],
});

// 选中的角色
interface CheckedRole {
  id?: string;
  name?: string;
}
const checkedRole = ref<CheckedRole>({});
const assignPermDialogVisible = ref(false);

const permKeywords = ref("");
const isExpanded = ref(true);

const parentChildLinked = ref(true);

// 获取数据
function fetchData() {
  loading.value = true;
  RoleAPI.getPage(queryParams)
    .then((data) => {
      roleList.value = data.list;
      total.value = data.total;
    })
    .finally(() => {
      loading.value = false;
    });
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
  fetchData();
}

// 行复选框选中
function handleSelectionChange(selection: any) {
  ids.value = selection.map((item: any) => item.id);
}

// 打开角色弹窗
function handleOpenDialog(roleId?: string) {
  dialog.visible = true;
  if (roleId) {
    dialog.title = "修改角色";
    RoleAPI.getFormData(roleId).then((data) => {
      Object.assign(formData, data);
    });
  } else {
    dialog.title = "新增角色";
  }
}

// 提交角色表单
function handleSubmit() {
  roleFormRef.value.validate((valid: any) => {
    if (valid) {
      loading.value = true;
      const roleId = formData.id;
      if (roleId) {
        RoleAPI.update(roleId, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            handleResetQuery();
          })
          .finally(() => (loading.value = false));
      } else {
        RoleAPI.create(formData)
          .then(() => {
            ElMessage.success("新增成功");
            handleCloseDialog();
            handleResetQuery();
          })
          .finally(() => (loading.value = false));
      }
    }
  });
}

// 关闭弹窗
function handleCloseDialog() {
  dialog.visible = false;

  roleFormRef.value.resetFields();
  roleFormRef.value.clearValidate();

  formData.id = undefined;
  formData.sort = 1;
  formData.status = 1;
  formData.isDefault = 1; // 新增：重置是否默认角色字段为1（是）
}

// 删除角色
function handleDelete(roleId?: number) {
  const roleIds = roleId !== undefined ? [roleId] : ids.value;
  if (!roleIds) {
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
      RoleAPI.deleteByIds(roleIds)
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

// 打开分配菜单权限弹窗
async function handleOpenAssignPermDialog(row: RolePageVO) {
  const roleId = row.id;
  if (roleId) {
    assignPermDialogVisible.value = true;
    loading.value = true;

    checkedRole.value.id = roleId;
    checkedRole.value.name = row.name;

    // 获取所有的菜单
    menuPermOptions.value = await MenuAPI.getOptions();

    // 回显角色已拥有的菜单
    RoleAPI.getRoleMenuIds(roleId)
      .then((data) => {
        data.forEach((menuId) => permTreeRef.value!.setChecked(menuId, true, false));
      })
      .finally(() => {
        loading.value = false;
      });
  }
}

// 分配菜单权限提交
function handleAssignPermSubmit() {
  const roleId = checkedRole.value.id;
  if (roleId) {
    const checkedMenuIds: number[] = permTreeRef
      .value!.getCheckedNodes(false, true)
      .map((node: any) => node.id);

    loading.value = true;
    RoleAPI.updateRoleMenus(roleId, checkedMenuIds)
      .then(() => {
        ElMessage.success("分配权限成功");
        assignPermDialogVisible.value = false;
        handleResetQuery();
      })
      .finally(() => {
        loading.value = false;
      });
  }
}

// 展开/收缩 菜单权限树
function togglePermTree() {
  isExpanded.value = !isExpanded.value;
  if (permTreeRef.value) {
    Object.values(permTreeRef.value.store.nodesMap).forEach((node: any) => {
      if (isExpanded.value) {
        node.expand();
      } else {
        node.collapse();
      }
    });
  }
}

// 权限筛选
watch(permKeywords, (val) => {
  permTreeRef.value!.filter(val);
});

function handlePermFilter(
  value: string,
  data: {
    [key: string]: any;
  }
) {
  if (!value) return true;
  return data.label.includes(value);
}

// 父子菜单节点是否联动
function handleparentChildLinkedChange(val: any) {
  parentChildLinked.value = val;
}

onMounted(() => {
  handleQuery();
});
</script>

<style scoped lang="scss">
/* stylelint-disable no-descending-specificity */
/* 玻璃面板样式 */
.glass-panel {
  background: rgba(255, 255, 255, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.8) !important;
  border-radius: 16px;
  box-shadow: 0 8px 32px -8px rgba(0, 0, 0, 0.05) !important;
  -webkit-backdrop-filter: blur(16px) saturate(120%);
  backdrop-filter: blur(16px) saturate(120%);
  transition: all 0.3s ease;
}

.glass-panel:hover {
  box-shadow: 0 12px 48px -12px rgba(0, 0, 0, 0.08) !important;
}

/* 权限树样式 */
.permission-tree {
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: 12px;

  :deep(.el-tree-node__content) {
    height: 36px;
    padding: 0 8px;
    margin-bottom: 4px;
    border-radius: 8px;
    transition: all 0.2s ease;

    &:hover {
      background-color: #e2e8f0;
    }
  }

  :deep(.el-tree-node.is-current > .el-tree-node__content) {
    color: #6366f1;
    background-color: rgba(99, 102, 241, 0.1);
  }
}

/* 玻璃抽屉样式 */
:deep(.glass-drawer) {
  .el-drawer__header {
    padding: 16px 20px;
    margin-bottom: 0;
    border-bottom: 1px solid #f1f5f9;
  }

  .el-drawer__title {
    font-weight: 600;
    color: #1e293b;
  }

  .el-drawer__body {
    padding: 20px;
  }

  .el-drawer__footer {
    padding: 16px 20px;
    border-top: 1px solid #f1f5f9;
  }
}

/* 深色模式 */
html.dark {
  .glass-panel {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.3);
  }

  .permission-tree {
    background: #1e293b;
    border-color: #334155;

    :deep(.el-tree-node__content) {
      &:hover {
        background-color: #334155;
      }
    }

    :deep(.el-tree-node.is-current > .el-tree-node__content) {
      color: #818cf8;
      background-color: rgba(129, 140, 248, 0.15);
    }
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

/* ==================== 极简 SaaS 风深度定制 ==================== */
/* 1. 表格净化 */
:deep(.minimal-table) {
  background: transparent !important;
  --el-table-border-color: rgba(0, 0, 0, 0.04);
  --el-table-header-bg-color: rgba(0, 0, 0, 0.02);
  --el-table-header-text-color: #475569;
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.6);
  --el-table-tr-bg-color: transparent;
}
:deep(.minimal-table th.el-table__cell) {
  font-weight: 600;
  border-bottom: 2px solid rgba(0, 0, 0, 0.06) !important;
}
:deep(.minimal-table td.el-table__cell) {
  border-bottom: 1px dashed rgba(0, 0, 0, 0.04) !important;
}
:deep(.minimal-table .el-table__inner-wrapper::before) {
  display: none; /* 隐藏底部死黑边线 */
}

/* 2. 表单输入框圆润化 */
:deep(.minimal-input .el-input__wrapper),
:deep(.minimal-input.el-select .el-select__wrapper) {
  background-color: rgba(255, 255, 255, 0.6) !important;
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #cbd5e1 inset !important;
  transition: all 0.2s ease;
}
:deep(.minimal-input .el-input__wrapper.is-focus),
:deep(.minimal-input.el-select .el-select__wrapper.is-focus) {
  background-color: #ffffff !important;
  box-shadow:
    0 0 0 1px var(--el-color-primary) inset,
    0 0 0 3px rgba(64, 128, 255, 0.1) !important;
}

/* 3. 按钮与标签高级感 */
.minimal-btn {
  font-weight: 500;
  border: none;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(64, 128, 255, 0.2);
  transition: all 0.2s ease;
}
.minimal-btn:hover {
  box-shadow: 0 4px 8px rgba(64, 128, 255, 0.3);
  transform: translateY(-1px);
}
.minimal-btn-plain {
  color: #64748b;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}
.minimal-btn-plain:hover {
  color: var(--el-color-primary);
  background: #ffffff;
  border-color: var(--el-color-primary);
}

.minimal-tag {
  padding: 0 12px !important;
  font-weight: 500 !important;
  border: none !important;
  border-radius: 6px !important;
}
.minimal-tag.success {
  color: #16a34a !important;
  background-color: #dcfce7 !important;
}
.minimal-tag.info {
  color: #64748b !important;
  background-color: #f1f5f9 !important;
}

/* 4. 分页组件融化 */
:deep(.minimal-pagination) {
  justify-content: flex-end;
}
:deep(.minimal-pagination button),
:deep(.minimal-pagination li) {
  background: transparent !important;
}
:deep(.minimal-pagination li.is-active) {
  color: white !important;
  background: var(--el-color-primary) !important;
  border-radius: 6px;
}

/* 5. 表格内操作按钮"软徽章化" */
:deep(.minimal-table .el-button.is-link) {
  height: auto !important;
  padding: 6px 10px !important;
  font-weight: 500 !important;
  border-radius: 8px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Primary 按钮（编辑、分配权限）的悬浮效果 */
:deep(.minimal-table .el-button--primary.is-link) {
  color: #64748b !important;
}
:deep(.minimal-table .el-button--primary.is-link:hover) {
  color: var(--el-color-primary) !important;
  background-color: rgba(64, 128, 255, 0.1) !important;
}

/* Danger 按钮（删除）的悬浮效果 */
:deep(.minimal-table .el-button--danger.is-link) {
  color: #94a3b8 !important;
}
:deep(.minimal-table .el-button--danger.is-link:hover) {
  color: #ef4444 !important;
  background-color: rgba(239, 68, 68, 0.1) !important;
}

/* 调整按钮之间的间距 */
:deep(.minimal-table .el-table__cell .cell) {
  display: flex;
  gap: 4px;
  align-items: center;
}
</style>
