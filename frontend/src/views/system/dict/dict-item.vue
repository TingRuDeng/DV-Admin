<!-- 字典项 -->
<template>
  <PageShell class="ff-dict-item-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item :label="t('common.keyword')" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          :placeholder="t('system.dictItemSearchPlaceholder')"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item :label="t('system.dictOwner')" prop="dictSelect" class="mb-0">
        <el-select
          v-model="queryParams.dict"
          :placeholder="t('system.dictRequired')"
          clearable
          filterable
        >
          <el-option v-for="item in dictList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      :title="t('system.dictItemData')"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:dictitems:add']"
            type="primary"
            :icon="resolveAppIcon('plus')"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            {{ t("system.addDictItem") }}
          </el-button>
          <el-button
            v-hasPerm="['system:dictitems:delete']"
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
        <el-table-column :label="t('system.dictOwner')" prop="dictName" min-width="120" />
        <el-table-column :label="t('system.dictItemLabel')" prop="label" min-width="120" />
        <el-table-column :label="t('system.dictItemValue')" prop="value" min-width="100" />
        <el-table-column :label="t('system.labelType')" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.tagType" :type="scope.row.tagType" effect="light">
              {{ scope.row.tagType }}
            </el-tag>
            <span v-else class="text-slate-400">{{ t("common.none") }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="100" align="center">
          <template #default="scope">
            <el-tag
              v-if="scope.row.status === 1"
              type="success"
              effect="light"
              class="ff-status-tag success"
            >
              {{ t("common.enabled") }}
            </el-tag>
            <el-tag v-else type="info" effect="light" class="ff-status-tag info">
              {{ t("common.disabled") }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column fixed="right" :label="t('common.actions')" width="200">
          <template #default="scope">
            <el-button
              v-hasPerm="['system:dictitems:edit']"
              type="primary"
              link
              :icon="resolveAppIcon('edit')"
              @click.stop="handleOpenDialog(scope.row.id)"
            >
              {{ t("common.edit") }}
            </el-button>
            <el-button
              v-hasPerm="['system:dictitems:delete']"
              type="danger"
              link
              :icon="resolveAppIcon('delete')"
              @click.stop="handleDelete(scope.row.id)"
            >
              {{ t("common.delete") }}
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>

    <DictItemFormDrawer ref="dictItemFormDrawerRef" :dict-list="dictList" @success="handleQuery" />
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import DictAPI, { DictPageVO } from "@/api/system/dict-api";
import DictItemAPI, { DictItemPageQuery, DictItemPageVO } from "@/api/system/dict-items-api";
import DictItemFormDrawer from "./components/DictItemFormDrawer.vue";

const route = useRoute();

const dict = route.query.dict as string;
const dictItemFormDrawerRef = ref<InstanceType<typeof DictItemFormDrawer> | null>(null);
const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const tableRef = ref<ProTableExpose | null>(null);
const dictList = ref<DictPageVO[]>([]);

const ids = ref<number[]>([]);
const queryParams = reactive<Omit<DictItemPageQuery, "pageNum" | "pageSize">>({});

const requestTableData = createPageRequest<DictItemPageQuery, DictItemPageVO>(
  DictItemAPI.getDictItemPage
);

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
function handleSelectionChange(selection: DictItemPageVO[]) {
  ids.value = selection.map((item) => Number(item.id)).filter((id) => !Number.isNaN(id));
}

// 打开弹窗
async function handleOpenDialog(id?: number) {
  if (id) {
    await dictItemFormDrawerRef.value?.openEdit(id);
    return;
  }
  await dictItemFormDrawerRef.value?.openCreate(queryParams.dict);
}
/**
 * 删除字典
 *
 * @param id 字典ID
 */
function handleDelete(id?: number) {
  const itemIds = id !== undefined ? [id] : ids.value;
  if (!itemIds) {
    ElMessage.warning(t("system.selectDelete"));
    return;
  }
  ElMessageBox.confirm(t("system.confirmDelete"), t("common.warning"), {
    confirmButtonText: t("common.confirm"),
    cancelButtonText: t("common.cancel"),
    type: "warning",
  }).then(
    () => {
      DictItemAPI.deleteDictItems(itemIds).then(() => {
        ElMessage.success(t("system.deleteSuccess"));
        tableRef.value?.reload(true);
      });
    },
    () => {
      ElMessage.info(t("system.cancelDelete"));
    }
  );
}

onMounted(() => {
  DictAPI.getPage().then((data) => {
    dictList.value = data.list;
    // 如果dict存在，设置为下拉框的选中值
    if (dict) {
      queryParams.dict = parseInt(dict, 10);
    }
  });
});
</script>
