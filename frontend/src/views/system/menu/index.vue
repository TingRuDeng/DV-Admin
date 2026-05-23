<template>
  <PageShell class="ff-menu-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item label="关键字" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          placeholder="菜单名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      title="菜单数据"
      :request="requestTableData"
      :params="queryParams"
      :show-pagination="false"
      :tree-props="{
        children: 'children',
        hasChildren: 'hasChildren',
      }"
      @row-click="handleRowClick"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:permissions:add']"
            type="primary"
            icon="plus"
            class="ff-button-primary"
            @click="handleOpenDialog('0')"
          >
            新增菜单
          </el-button>
        </div>
      </template>

      <template #default>
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
            <el-tag v-if="scope.row.type === 'CATALOG'" class="ff-status-tag warning">目录</el-tag>
            <el-tag v-if="scope.row.type === 'MENU'" class="ff-status-tag success">菜单</el-tag>
            <el-tag v-if="scope.row.type === 'BUTTON'" class="ff-status-tag danger">按钮</el-tag>
            <el-tag v-if="scope.row.type === 'EXTLINK'" class="ff-status-tag info">外链</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="路由名称" align="left" width="150" prop="routeName" />
        <el-table-column label="路由路径" align="left" width="150" prop="routePath" />
        <el-table-column label="组件路径" align="left" width="250" prop="component" />
        <el-table-column label="权限标识" align="center" width="200" prop="perm" />
        <el-table-column label="状态" align="center" width="80">
          <template #default="scope">
            <el-tag v-if="scope.row.visible === 1" class="ff-status-tag success">显示</el-tag>
            <el-tag v-else class="ff-status-tag info">隐藏</el-tag>
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
      </template>
    </ProTable>

    <MenuFormDrawer ref="menuFormDrawerRef" @success="handleQuery" />
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createListRequest } from "@/utils/pro-table-request";

import MenuAPI, { MenuQuery, MenuVO } from "@/api/system/menu-api";
import MenuFormDrawer from "./components/MenuFormDrawer.vue";

defineOptions({
  name: "SysMenu",
  inheritAttrs: false,
});

const queryFormRef = ref<InstanceType<typeof ProSearch> | null>(null);
const menuFormDrawerRef = ref<InstanceType<typeof MenuFormDrawer> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const loading = ref(false);
// 查询参数
const queryParams = reactive<MenuQuery>({});

// 选择表格的行菜单ID
const selectedMenuId = ref<string | undefined>();

const requestTableData = createListRequest<MenuQuery, MenuVO>(MenuAPI.getList);

// 查询菜单
function handleQuery() {
  tableRef.value?.reload(true);
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  tableRef.value?.reload(true);
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
async function handleOpenDialog(parent?: string, menuId?: string) {
  if (menuId) {
    await menuFormDrawerRef.value?.openEdit(menuId);
    return;
  }

  await menuFormDrawerRef.value?.openCreate(parent);
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
          tableRef.value?.reload(true);
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
</script>
