<template>
  <PageShell class="ff-menu-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item :label="t('common.keyword')" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          :placeholder="t('system.menuName')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      :title="t('system.menuData')"
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
            class="ff-button-primary"
            @click="handleOpenDialog('0')"
          >
            <template #icon><AppIcon name="plus" :size="15" /></template>
            {{ t("system.addMenu") }}
          </el-button>
        </div>
      </template>

      <template #default>
        <el-table-column :label="t('system.menuName')" min-width="200">
          <template #default="scope">
            <AppIcon v-if="scope.row.icon" :name="scope.row.icon" :size="16" />
            {{ scope.row.name }}
          </template>
        </el-table-column>

        <el-table-column :label="t('system.menuType')" align="center" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.type === 'CATALOG'" class="ff-status-tag warning">
              {{ t("system.catalog") }}
            </el-tag>
            <el-tag v-if="scope.row.type === 'MENU'" class="ff-status-tag success">
              {{ t("system.menu") }}
            </el-tag>
            <el-tag v-if="scope.row.type === 'BUTTON'" class="ff-status-tag danger">
              {{ t("system.button") }}
            </el-tag>
            <el-tag v-if="scope.row.type === 'EXTLINK'" class="ff-status-tag info">
              {{ t("system.externalLink") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('system.routeName')" align="left" width="150" prop="routeName" />
        <el-table-column :label="t('system.routePath')" align="left" width="150" prop="routePath" />
        <el-table-column
          :label="t('system.componentPath')"
          align="left"
          width="250"
          prop="component"
        />
        <el-table-column
          :label="t('system.permissionKey')"
          align="center"
          width="200"
          prop="perm"
        />
        <el-table-column :label="t('common.status')" align="center" width="80">
          <template #default="scope">
            <el-tag v-if="scope.row.visible === 1" class="ff-status-tag success">
              {{ t("system.display") }}
            </el-tag>
            <el-tag v-else class="ff-status-tag info">{{ t("system.hidden") }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.sort')" align="center" width="80" prop="sort">
          <template #default="{ row }">
            <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">
              {{ row.sort }}
            </span>
          </template>
        </el-table-column>
        <el-table-column fixed="right" :label="t('common.actions')" width="280">
          <template #default="scope">
            <el-button
              v-if="scope.row.type === 'CATALOG' || scope.row.type === 'MENU'"
              v-hasPerm="['system:permissions:add']"
              type="primary"
              link
              size="small"
              @click.stop="handleOpenDialog(scope.row.id)"
            >
              <template #icon><AppIcon name="plus" :size="14" /></template>
              {{ t("common.add") }}
            </el-button>

            <el-button
              v-hasPerm="['system:permissions:edit']"
              type="primary"
              link
              @click.stop="handleOpenDialog(undefined, scope.row.id)"
            >
              <template #icon><AppIcon name="pencil" :size="14" /></template>
              {{ t("common.edit") }}
            </el-button>
            <el-button
              v-hasPerm="['system:permissions:delete']"
              type="danger"
              link
              @click.stop="handleDelete(scope.row.id)"
            >
              <template #icon><AppIcon name="delete" :size="14" /></template>
              {{ t("common.delete") }}
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>

    <MenuFormDrawer ref="menuFormDrawerRef" @success="handleQuery" />
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import AppIcon from "@/components/AppIcon/index.vue";
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
    ElMessage.warning(t("system.selectDelete"));
    return false;
  }

  ElMessageBox.confirm(t("system.confirmDelete"), t("common.warning"), {
    confirmButtonText: t("common.confirm"),
    cancelButtonText: t("common.cancel"),
    type: "warning",
  }).then(
    () => {
      loading.value = true;
      MenuAPI.deleteById(menuId)
        .then(() => {
          ElMessage.success(t("system.deleteSuccess"));
          tableRef.value?.reload(true);
        })
        .finally(() => {
          loading.value = false;
        });
    },
    () => {
      ElMessage.info(t("system.cancelDelete"));
    }
  );
}
</script>
