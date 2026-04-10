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
        <el-form-item label="关键字" prop="search" class="mb-0">
          <el-input
            v-model="queryParams.search"
            placeholder="菜单名称"
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
          <span class="text-base font-semibold text-slate-700 tracking-wide">菜单数据</span>
        </div>
        <div class="flex gap-2">
          <el-button
            v-hasPerm="['system:permissions:add']"
            type="primary"
            icon="plus"
            class="minimal-btn"
            @click="handleOpenDialog('0')"
          >
            新增菜单
          </el-button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden border border-slate-100/50 rounded-xl bg-white/20">
        <el-table
          ref="dataTableRef"
          v-loading="loading"
          highlight-current-row
          row-key="id"
          :data="menuTableData"
          :tree-props="{
            children: 'children',
            hasChildren: 'hasChildren',
          }"
          class="minimal-table"
          @row-click="handleRowClick"
        >
          <el-table-column label="菜单名称" min-width="200">
            <template #default="scope">
              <template v-if="scope.row.icon && scope.row.icon.startsWith('el-icon')">
                <el-icon style="vertical-align: -0.15em">
                  <component :is="scope.row.icon.replace('el-icon-', '')" />
                </el-icon>
              </template>
              <template v-else-if="scope.row.icon">
                <div :class="`i-svg:${scope.row.icon}`" />
              </template>
              {{ scope.row.name }}
            </template>
          </el-table-column>

          <el-table-column label="类型" align="center" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.type === 'CATALOG'" class="minimal-tag warning">目录</el-tag>
              <el-tag v-if="scope.row.type === 'MENU'" class="minimal-tag success">菜单</el-tag>
              <el-tag v-if="scope.row.type === 'BUTTON'" class="minimal-tag danger">按钮</el-tag>
              <el-tag v-if="scope.row.type === 'EXTLINK'" class="minimal-tag info">外链</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="路由名称" align="left" width="150" prop="routeName" />
          <el-table-column label="路由路径" align="left" width="150" prop="routePath" />
          <el-table-column label="组件路径" align="left" width="250" prop="component" />
          <el-table-column label="权限标识" align="center" width="200" prop="perm" />
          <el-table-column label="状态" align="center" width="80">
            <template #default="scope">
              <el-tag v-if="scope.row.visible === 1" class="minimal-tag success">显示</el-tag>
              <el-tag v-else class="minimal-tag info">隐藏</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="排序" align="center" width="80" prop="sort">
            <template #default="{ row }">
              <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">
                {{ row.sort }}
              </span>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" width="280">
            <template #default="scope">
              <el-button
                v-if="scope.row.type === 'CATALOG' || scope.row.type === 'MENU'"
                v-hasPerm="['system:permissions:add']"
                type="primary"
                link
                icon="plus"
                size="small"
                @click.stop="handleOpenDialog(scope.row.id)"
              >
                新增
              </el-button>

              <el-button
                v-hasPerm="['system:permissions:edit']"
                type="primary"
                link
                icon="edit"
                @click.stop="handleOpenDialog(undefined, scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['system:permissions:delete']"
                type="danger"
                link
                icon="delete"
                @click.stop="handleDelete(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <el-drawer
      v-model="dialog.visible"
      :title="dialog.title"
      :size="drawerSize"
      class="minimal-drawer"
      @close="handleCloseDialog"
    >
      <el-form
        ref="menuFormRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        class="minimal-form pt-4"
      >
        <el-form-item label="父级菜单" prop="parent">
          <el-tree-select
            v-model="formData.parent"
            placeholder="选择上级菜单"
            :data="menuOptions"
            node-key="id"
            filterable
            check-strictly
            :render-after-expand="false"
            class="minimal-input w-full"
          />
        </el-form-item>

        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入菜单名称" class="minimal-input" />
        </el-form-item>

        <el-form-item label="菜单类型" prop="type">
          <el-radio-group v-model="formData.type" @change="handleMenuTypeChange">
            <el-radio :value="'CATALOG'">根目录</el-radio>
            <el-radio :value="'MENU'">子菜单</el-radio>
            <el-radio :value="'BUTTON'">按钮</el-radio>
            <el-radio :value="'EXTLINK'">外链</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="formData.type === 'EXTLINK'" label="外链地址" prop="path">
          <el-input
            v-model="formData.routePath"
            placeholder="请输入外链完整路径"
            class="minimal-input"
          />
        </el-form-item>

        <el-form-item v-if="formData.type === 'MENU'" prop="routeName">
          <template #label>
            <div class="flex items-center">
              路由名称
              <el-tooltip placement="bottom" effect="light">
                <template #content>
                  如果需要开启缓存，需保证页面 defineOptions 中的 name 与此处一致，建议使用驼峰。
                </template>
                <el-icon class="ml-1 cursor-pointer text-primary">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </template>
          <el-input v-model="formData.routeName" placeholder="User" class="minimal-input" />
        </el-form-item>

        <el-form-item
          v-if="formData.type === 'CATALOG' || formData.type === 'MENU'"
          prop="routePath"
        >
          <template #label>
            <div class="flex items-center">
              路由路径
              <el-tooltip placement="bottom" effect="light">
                <template #content>
                  定义应用中不同页面对应的 URL 路径，目录需以 / 开头，菜单项不用。例如：系统管理目录
                  /system，系统管理下的用户管理菜单 user。
                </template>
                <el-icon class="ml-1 cursor-pointer text-primary">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </template>
          <el-input
            v-if="formData.type === 'CATALOG'"
            v-model="formData.routePath"
            placeholder="system"
            class="minimal-input"
          />
          <el-input v-else v-model="formData.routePath" placeholder="user" class="minimal-input" />
        </el-form-item>

        <el-form-item v-if="formData.type === 'MENU'" prop="component">
          <template #label>
            <div class="flex items-center">
              组件路径
              <el-tooltip placement="bottom" effect="light">
                <template #content>
                  组件页面完整路径，相对于 src/views/，如 system/user/index，缺省后缀 .vue
                </template>
                <el-icon class="ml-1 cursor-pointer text-primary">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </template>

          <el-input
            v-model="formData.component"
            placeholder="system/user/index"
            class="minimal-input"
          >
            <template v-if="formData.type === 'MENU'" #prepend>src/views/</template>
            <template v-if="formData.type === 'MENU'" #append>.vue</template>
          </el-input>
        </el-form-item>

        <el-form-item v-if="formData.type === 'MENU'">
          <template #label>
            <div class="flex items-center">
              路由参数
              <el-tooltip placement="bottom" effect="light">
                <template #content>
                  组件页面使用 `useRoute().query.参数名` 获取路由参数值。
                </template>
                <el-icon class="ml-1 cursor-pointer text-primary">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </template>

          <div v-if="!formData.params || formData.params.length === 0">
            <el-button
              type="success"
              plain
              class="minimal-btn"
              @click="formData.params = [{ key: '', value: '' }]"
            >
              添加路由参数
            </el-button>
          </div>

          <div v-else>
            <div
              v-for="(item, index) in formData.params"
              :key="index"
              class="flex items-center gap-2 mb-2"
            >
              <el-input
                v-model="item.key"
                placeholder="参数名"
                style="width: 100px"
                class="minimal-input"
              />

              <span class="text-slate-400">=</span>

              <el-input
                v-model="item.value"
                placeholder="参数值"
                style="width: 100px"
                class="minimal-input"
              />

              <el-icon
                v-if="formData.params.indexOf(item) === formData.params.length - 1"
                class="cursor-pointer text-success"
                style="vertical-align: -0.15em"
                @click="formData.params.push({ key: '', value: '' })"
              >
                <CirclePlusFilled />
              </el-icon>
              <el-icon
                class="cursor-pointer text-danger"
                style="vertical-align: -0.15em"
                @click="formData.params.splice(formData.params.indexOf(item), 1)"
              >
                <DeleteFilled />
              </el-icon>
            </div>
          </div>
        </el-form-item>

        <el-form-item v-if="formData.type !== 'BUTTON'" prop="visible" label="显示状态">
          <el-radio-group v-model="formData.visible">
            <el-radio :value="1">显示</el-radio>
            <el-radio :value="0">隐藏</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="formData.type === 'CATALOG' || formData.type === 'MENU'">
          <template #label>
            <div class="flex items-center">
              始终显示
              <el-tooltip placement="bottom" effect="light">
                <template #content>
                  选择"是"，即使目录或菜单下只有一个子节点，也会显示父节点。
                  <br />
                  选择"否"，如果目录或菜单下只有一个子节点，则只显示该子节点，隐藏父节点。
                  <br />
                  如果是叶子节点，请选择"否"。
                </template>
                <el-icon class="ml-1 cursor-pointer text-primary">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </template>

          <el-radio-group v-model="formData.alwaysShow">
            <el-radio :value="1">是</el-radio>
            <el-radio :value="0">否</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="formData.type === 'MENU'" label="缓存页面">
          <el-radio-group v-model="formData.keepAlive">
            <el-radio :value="1">开启</el-radio>
            <el-radio :value="0">关闭</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="排序" prop="sort">
          <el-input-number
            v-model="formData.sort"
            style="width: 100px"
            controls-position="right"
            :min="0"
            class="minimal-input"
          />
        </el-form-item>

        <!-- 权限标识 -->
        <el-form-item v-if="formData.type === 'BUTTON'" label="权限标识" prop="perm">
          <el-input v-model="formData.perm" placeholder="sys:user:add" class="minimal-input" />
        </el-form-item>

        <el-form-item v-if="formData.type !== 'BUTTON'" label="图标" prop="icon">
          <!-- 图标选择器 -->
          <icon-select v-model="formData.icon" />
        </el-form-item>

        <el-form-item v-if="formData.type === 'CATALOG'" label="跳转路由">
          <el-input v-model="formData.redirect" placeholder="跳转路由" class="minimal-input" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="handleCloseDialog">取 消</el-button>
          <el-button type="primary" class="minimal-btn" @click="handleSubmit">确 定</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from "@/store/modules/app-store";
import { DeviceEnum } from "@/enums/settings/device-enum";

import MenuAPI, { MenuQuery, MenuForm, MenuVO } from "@/api/system/menu-api";

defineOptions({
  name: "SysMenu",
  inheritAttrs: false,
});

const appStore = useAppStore();

const queryFormRef = ref();
const menuFormRef = ref();

const loading = ref(false);
const dialog = reactive({
  title: "新增菜单",
  visible: false,
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));
// 查询参数
const queryParams = reactive<MenuQuery>({});
// 菜单表格数据
const menuTableData = ref<MenuVO[]>([]);
// 顶级目录下拉选项
const menuOptions = ref<OptionType[]>([]);
// 初始菜单表单数据
const initialMenuFormData = ref<MenuForm>({
  id: undefined,
  parent: "0",
  visible: 1,
  sort: 1,
  type: "MENU", // 默认菜单
  alwaysShow: 0,
  keepAlive: 1,
  params: [],
});
// 菜单表单数据
const formData = ref({ ...initialMenuFormData.value });
// 表单验证规则
const rules = reactive({
  parent: [{ required: true, message: "请选择父级菜单", trigger: "blur" }],
  name: [{ required: true, message: "请输入菜单名称", trigger: "blur" }],
  type: [{ required: true, message: "请选择菜单类型", trigger: "blur" }],
  routeName: [{ required: true, message: "请输入路由名称", trigger: "blur" }],
  routePath: [{ required: true, message: "请输入路由路径", trigger: "blur" }],
  component: [{ required: true, message: "请输入组件路径", trigger: "blur" }],
  visible: [{ required: true, message: "请选择显示状态", trigger: "change" }],
});

// 选择表格的行菜单ID
const selectedMenuId = ref<string | undefined>();

// 查询菜单
function handleQuery() {
  loading.value = true;
  MenuAPI.getList(queryParams)
    .then((data) => {
      menuTableData.value = data;
    })
    .finally(() => {
      loading.value = false;
    });
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value.resetFields();
  handleQuery();
}

// 行点击事件
function handleRowClick(row: MenuVO) {
  selectedMenuId.value = row.id;
}

/**
 * 打开表单弹窗
 *
 * @param parent 父菜单ID
 * @param menuId 菜单ID
 */
function handleOpenDialog(parent?: string, menuId?: string) {
  MenuAPI.getOptions(true)
    .then((data) => {
      // 将顶级目录的id改为字符串类型"0"
      menuOptions.value = [{ id: "0", label: "顶级目录", children: data }];
    })
    .then(() => {
      dialog.visible = true;
      if (menuId) {
        dialog.title = "编辑菜单";
        MenuAPI.getFormData(menuId).then((data) => {
          if (data.parent === null || data.parent === undefined) {
            data.parent = "0";
          }
          initialMenuFormData.value = { ...data };
          formData.value = data;
        });
      } else {
        dialog.title = "新增菜单";
        // 新增时也改为字符串类型，与menuOptions中的id保持一致
        formData.value.parent = parent || "0";
      }
    });
}

// 菜单类型切换
function handleMenuTypeChange() {
  // 如果菜单类型改变
  if (formData.value.type !== initialMenuFormData.value.type) {
    if (formData.value.type === "MENU") {
      // 目录切换到菜单时，清空组件路径
      if (initialMenuFormData.value.type === "CATALOG") {
        formData.value.component = "";
      } else {
        // 其他情况，保留原有的组件路径
        formData.value.routePath = initialMenuFormData.value.routePath;
        formData.value.component = initialMenuFormData.value.component;
      }
    }
  }
}

/**
 * 提交表单
 */
function handleSubmit() {
  menuFormRef.value.validate((isValid: boolean) => {
    if (isValid) {
      const menuId = formData.value.id;
      const submitData = { ...formData.value };

      // 如果parent值为0，则从提交数据中移除该字段
      if (submitData.parent === "0") {
        delete submitData.parent;
      }
      if (menuId) {
        //修改时父级菜单不能为当前菜单
        if (submitData.parent === menuId) {
          ElMessage.error("父级菜单不能为当前菜单");
          return;
        }
        MenuAPI.update(menuId, submitData).then(() => {
          ElMessage.success("修改成功");
          handleCloseDialog();
          handleQuery();
        });
      } else {
        MenuAPI.create(submitData).then(() => {
          ElMessage.success("新增成功");
          handleCloseDialog();
          handleQuery();
        });
      }
    }
  });
}

// 删除菜单
function handleDelete(menuId: string) {
  if (!menuId) {
    ElMessage.warning("请勾选删除项");
    return false;
  }

  ElMessageBox.confirm("确认删除已选中的数据项?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(
    () => {
      loading.value = true;
      MenuAPI.deleteById(menuId)
        .then(() => {
          ElMessage.success("删除成功");
          handleQuery();
        })
        .finally(() => {
          loading.value = false;
        });
    },
    () => {
      ElMessage.info("已取消删除");
    }
  );
}

function resetForm() {
  menuFormRef.value.resetFields();
  menuFormRef.value.clearValidate();
  formData.value = {
    id: undefined,
    parent: "0",
    visible: 1,
    sort: 1,
    type: "MENU", // 默认菜单
    alwaysShow: 0,
    keepAlive: 1,
    params: [],
  };
}

// 关闭弹窗
function handleCloseDialog() {
  dialog.visible = false;
  resetForm();
}

onMounted(() => {
  handleQuery();
});
</script>

<!-- 页面特定样式 (scoped) -->
<style scoped lang="scss">
/* 抽屉样式优化 */
:deep(.minimal-drawer .el-drawer__header) {
  padding: 16px 20px;
  margin-bottom: 0;
  border-bottom: 1px solid #f1f5f9;
}

:deep(.minimal-drawer .el-drawer__title) {
  font-weight: 600;
  color: #1e293b;
}

:deep(.minimal-drawer .el-drawer__body) {
  padding: 20px;
}

:deep(.minimal-drawer .el-drawer__footer) {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
}

/* 深色模式 */
html.dark :deep(.minimal-drawer .el-drawer__header) {
  border-bottom-color: #334155;
}

html.dark :deep(.minimal-drawer .el-drawer__title) {
  color: #f1f5f9;
}

html.dark :deep(.minimal-drawer .el-drawer__footer) {
  border-top-color: #334155;
}
</style>

<!-- 全局穿透样式 (非 scoped，用于覆盖 Element Plus) -->
<style lang="scss">
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

/* 表格净化 */
.minimal-table {
  background: transparent !important;
  --el-table-border-color: rgba(0, 0, 0, 0.04);
  --el-table-header-bg-color: rgba(0, 0, 0, 0.02);
  --el-table-header-text-color: #475569;
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.6);
  --el-table-tr-bg-color: transparent;
}

.minimal-table th.el-table__cell {
  font-weight: 600;
  border-bottom: 2px solid rgba(0, 0, 0, 0.06) !important;
}

.minimal-table td.el-table__cell {
  border-bottom: 1px dashed rgba(0, 0, 0, 0.04) !important;
}

.minimal-table .el-table__inner-wrapper::before {
  display: none;
}

/* 表单输入框圆润化 */
.minimal-input .el-input__wrapper,
.minimal-input.el-select .el-select__wrapper {
  background-color: rgba(255, 255, 255, 0.6) !important;
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #cbd5e1 inset !important;
  transition: all 0.2s ease;
}

.minimal-input .el-input__wrapper.is-focus,
.minimal-input.el-select .el-select__wrapper.is-focus {
  background-color: #ffffff !important;
  box-shadow:
    0 0 0 1px var(--el-color-primary) inset,
    0 0 0 3px rgba(64, 128, 255, 0.1) !important;
}

/* 按钮与标签高级感 */
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

/* 分页组件融化 */
.minimal-pagination {
  justify-content: flex-end;
}

.minimal-pagination button,
.minimal-pagination li {
  background: transparent !important;
}

.minimal-pagination li.is-active {
  color: white !important;
  background: var(--el-color-primary) !important;
  border-radius: 6px;
}

/* 表格内操作按钮"软徽章化" */
.minimal-table .el-button.is-link {
  height: auto !important;
  padding: 6px 10px !important;
  font-weight: 500 !important;
  border-radius: 8px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.minimal-table .el-button--primary.is-link {
  color: #64748b !important;
}

.minimal-table .el-button--primary.is-link:hover {
  color: var(--el-color-primary) !important;
  background-color: rgba(64, 128, 255, 0.1) !important;
}

.minimal-table .el-button--danger.is-link {
  color: #94a3b8 !important;
}

.minimal-table .el-button--danger.is-link:hover {
  color: #ef4444 !important;
  background-color: rgba(239, 68, 68, 0.1) !important;
}

.minimal-table .el-table__cell .cell {
  display: flex;
  gap: 4px;
  align-items: center;
}

/* 深色模式 */
html.dark .glass-panel {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.3);
}
</style>
