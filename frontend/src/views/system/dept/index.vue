<template>
  <PageShell class="ff-dept-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item :label="t('common.keyword')" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          :placeholder="t('system.deptNamePlaceholder')"
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item :label="t('system.status')" prop="status" class="mb-0">
        <el-select
          v-model="queryParams.status"
          :placeholder="t('common.all')"
          clearable
          style="width: 120px"
        >
          <el-option :value="1" :label="t('common.normal')" />
          <el-option :value="0" :label="t('common.disabled')" />
        </el-select>
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      :title="t('system.deptData')"
      :request="requestTableData"
      :params="queryParams"
      :show-pagination="false"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:departments:add']"
            type="primary"
            :icon="resolveAppIcon('plus')"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            {{ t("system.addDeptAction") }}
          </el-button>
          <el-button
            v-hasPerm="['system:departments:delete']"
            type="danger"
            plain
            :disabled="selectIds.length === 0"
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
        <el-table-column prop="sort" :label="t('common.sort')" width="100" align="center">
          <template #default="{ row }">
            <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">
              {{ row.sort }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="name" :label="t('system.deptName')" min-width="200" />
        <el-table-column prop="status" :label="t('common.status')" width="120" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.status == 1 ? 'success' : 'info'"
              class="ff-status-tag"
              :class="scope.row.status == 1 ? 'success' : 'info'"
            >
              {{ scope.row.status == 1 ? t("common.normal") : t("common.disabled") }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" fixed="right" width="280">
          <template #default="scope">
            <el-button
              v-hasPerm="['system:departments:add']"
              type="primary"
              link
              :icon="resolveAppIcon('plus')"
              size="small"
              @click.stop="handleOpenDialog(scope.row.id, undefined)"
            >
              {{ t("common.add") }}
            </el-button>
            <el-button
              v-hasPerm="['system:departments:edit']"
              type="primary"
              link
              :icon="resolveAppIcon('edit')"
              size="small"
              @click.stop="handleOpenDialog(scope.row.parentId, scope.row.id)"
            >
              {{ t("common.edit") }}
            </el-button>
            <el-button
              v-hasPerm="['system:departments:delete']"
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

    <DeptFormDrawer
      ref="deptFormRef"
      v-model="dialog.visible"
      :title="t(dialog.titleKey)"
      :model="formData"
      :rules="rules"
      :loading="formLoading"
      :dept-options="deptOptions"
      @submit="handleSubmit"
      @close="handleCloseDialog"
    />
  </PageShell>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import { resolveAppIcon } from "@/components/AppIcon/icon-map";
defineOptions({
  name: "Dept",
  inheritAttrs: false,
});

import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createListRequest } from "@/utils/pro-table-request";
import DeptAPI, { DeptForm, DeptQuery, DeptVO } from "@/api/system/dept-api";
import DeptFormDrawer from "./components/DeptFormDrawer.vue";

const queryFormRef = ref<InstanceType<typeof ProSearch> | null>(null);
const deptFormRef = ref<InstanceType<typeof DeptFormDrawer> | null>(null);
const tableRef = ref<ProTableExpose | null>(null);

const formLoading = ref(false);
const selectIds = ref<string[]>([]);
const queryParams = reactive<DeptQuery>({});

const dialog = reactive({
  titleKey: "system.addDeptAction",
  visible: false,
});

const deptOptions = ref<OptionType[]>([]);
const formData = reactive<DeptForm>({
  status: 1,
  parentId: undefined,
  sort: 1,
});

const rules = reactive({
  name: [{ required: true, message: () => t("system.deptNameRequired"), trigger: "blur" }],
  sort: [{ required: true, message: () => t("system.sortRequired"), trigger: "blur" }],
});

const requestTableData = createListRequest<DeptQuery, DeptVO>(DeptAPI.getList, {
  stripPagination: true,
});

function handleQuery() {
  tableRef.value?.reload(true);
}

function handleResetQuery() {
  queryFormRef.value?.resetFields();
  tableRef.value?.reload(true);
}

function handleSelectionChange(selection: unknown[]) {
  const rows = selection as DeptVO[];
  selectIds.value = rows.map((item) => item.id).filter((id): id is string => Boolean(id));
}

async function handleOpenDialog(parentId?: string, deptId?: string) {
  deptOptions.value = await DeptAPI.getOptions();
  dialog.visible = true;
  if (deptId) {
    dialog.titleKey = "system.editDept";
    DeptAPI.getFormData(deptId).then((data) => {
      Object.assign(formData, data);
    });
  } else {
    dialog.titleKey = "system.addDeptAction";
    formData.parentId = parentId;
  }
}

function handleSubmit() {
  formLoading.value = true;
  deptFormRef.value?.validate((valid: boolean) => {
    if (valid) {
      const deptId = formData.id;
      if (deptId) {
        DeptAPI.update(deptId, formData)
          .then(() => {
            ElMessage.success(t("system.updateSuccess"));
            handleCloseDialog();
            tableRef.value?.reload(true);
          })
          .finally(() => (formLoading.value = false));
      } else {
        DeptAPI.create(formData)
          .then(() => {
            ElMessage.success(t("system.createSuccess"));
            handleCloseDialog();
            tableRef.value?.reload(true);
          })
          .finally(() => (formLoading.value = false));
      }
      return;
    }

    formLoading.value = false;
  });
}

function handleDelete(deptId?: string | number) {
  const deptIds = deptId !== undefined ? [deptId] : selectIds.value;
  if (!deptIds || (Array.isArray(deptIds) && deptIds.length === 0)) {
    ElMessage.warning(t("system.selectDelete"));
    return;
  }

  ElMessageBox.confirm(t("system.confirmDelete"), t("common.warning"), {
    confirmButtonText: t("common.confirm"),
    cancelButtonText: t("common.cancel"),
    type: "warning",
  }).then(
    () => {
      DeptAPI.deleteByIds(deptIds)
        .then(() => {
          ElMessage.success(t("system.deleteSuccess"));
          tableRef.value?.reload(true);
        })
        .finally(() => undefined);
    },
    () => {
      ElMessage.info(t("system.cancelDelete"));
    }
  );
}

function resetForm() {
  deptFormRef.value?.resetFields();
  deptFormRef.value?.clearValidate();

  formData.id = undefined;
  formData.parentId = undefined;
  formData.status = 1;
  formData.sort = 1;
}

function handleCloseDialog() {
  dialog.visible = false;
  resetForm();
}
</script>
