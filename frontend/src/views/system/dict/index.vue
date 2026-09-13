<!-- 字典 -->
<template>
  <PageShell class="ff-dict-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item :label="t('common.keyword')" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          :placeholder="t('system.dictSearchPlaceholder')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      :title="t('system.dictData')"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:dicts:add']"
            type="primary"
            :icon="resolveAppIcon('plus')"
            class="ff-button-primary"
            @click="handleAddClick()"
          >
            {{ t("system.addDict") }}
          </el-button>
          <el-button
            v-hasPerm="['system:dicts:delete']"
            type="danger"
            plain
            :disabled="ids.length === 0"
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
        <el-table-column :label="t('system.dictName')" prop="name" min-width="150" />
        <el-table-column :label="t('system.dictCode')" prop="dictCode" min-width="150" />
        <el-table-column :label="t('common.status')" prop="status" width="100" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === 1 ? 'success' : 'info'"
              class="ff-status-tag"
              :class="scope.row.status === 1 ? 'success' : 'info'"
            >
              {{ scope.row.status === 1 ? t("common.enabled") : t("common.disabled") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column fixed="right" :label="t('common.actions')" width="280">
          <template #default="scope">
            <el-button
              v-hasPerm="['system:dictitems:query']"
              type="primary"
              link
              size="small"
              @click.stop="handleOpenDictData(scope.row)"
            >
              <template #icon><AppIcon name="book-open" :size="14" /></template>
              {{ t("system.dictData") }}
            </el-button>
            <el-button
              v-hasPerm="['system:dicts:edit']"
              type="primary"
              link
              :icon="resolveAppIcon('edit')"
              size="small"
              @click.stop="handleEditClick(scope.row.id)"
            >
              {{ t("common.edit") }}
            </el-button>
            <el-button
              v-hasPerm="['system:dicts:delete']"
              type="danger"
              link
              :icon="resolveAppIcon('delete')"
              size="small"
              @click.stop="handleDelete(scope.row.id)"
            >
              {{ t("common.delete") }}
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>

    <DictFormDrawer ref="dictFormDrawerRef" @success="handleQuery" />
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
import AppIcon from "@/components/AppIcon/index.vue";
defineOptions({
  name: "Dict",
  inheritAttrs: false,
});

import DictAPI, { DictPageQuery, DictPageVO } from "@/api/system/dict-api";
import PageShell from "@/components/PageShell/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";

import router from "@/router";
import DictFormDrawer from "./components/DictFormDrawer.vue";

const queryFormRef = ref<InstanceType<typeof ProSearch> | null>(null);
const dictFormDrawerRef = ref<InstanceType<typeof DictFormDrawer> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const ids = ref<number[]>([]);

const queryParams = reactive<Omit<DictPageQuery, "pageNum" | "pageSize">>({});

const requestTableData = createPageRequest<DictPageQuery, DictPageVO>(DictAPI.getPage);

// 查询（重置页码后获取数据）
function handleQuery() {
  tableRef.value?.reload(true);
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  tableRef.value?.reload(true);
}

// 行选择
function handleSelectionChange(selection: unknown[]) {
  const rows = selection as DictPageVO[];
  ids.value = rows.map((item) => Number(item.id)).filter((id) => !Number.isNaN(id));
}

// 新增字典
async function handleAddClick() {
  await dictFormDrawerRef.value?.openCreate();
}

/**
 * 编辑字典
 *
 * @param id 字典ID
 */
async function handleEditClick(id: string) {
  await dictFormDrawerRef.value?.openEdit(id);
}
/**
 * 删除字典
 *
 * @param id 字典ID
 */
function handleDelete(id?: number) {
  const attrGroupIds = id !== undefined ? [id] : ids.value;
  if (!attrGroupIds) {
    ElMessage.warning(t("system.selectDelete"));
    return;
  }
  ElMessageBox.confirm(t("system.confirmDelete"), t("common.warning"), {
    confirmButtonText: t("common.confirm"),
    cancelButtonText: t("common.cancel"),
    type: "warning",
  }).then(
    () => {
      DictAPI.deleteByIds(attrGroupIds).then(() => {
        ElMessage.success(t("system.deleteSuccess"));
        tableRef.value?.reload(true);
      });
    },
    () => {
      ElMessage.info(t("system.cancelDelete"));
    }
  );
}

// 打开字典项
function handleOpenDictData(row: DictPageVO) {
  if (!row || !row.id || !row.name) {
    ElMessage.warning(t("system.dictInvalid"));
    return;
  }

  router.push({
    path: "dict-item",
    query: {
      dict: row.id,
    },
  });
}
</script>
