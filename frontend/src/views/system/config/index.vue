<!-- 系统配置 -->
<template>
  <PageShell class="ff-config-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item label="关键字" prop="keywords" class="mb-0">
        <el-input
          v-model="queryParams.keywords"
          placeholder="请输入配置键\配置名称"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      title="系统配置"
      :request="requestTableData"
      :params="{ keywords: queryParams.keywords }"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['sys:config:add']"
            type="primary"
            icon="plus"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            新增配置
          </el-button>
          <el-button
            v-hasPerm="['sys:config:refresh']"
            color="#626aef"
            icon="RefreshLeft"
            class="ff-button-primary"
            @click="handleRefreshCache"
          >
            刷新缓存
          </el-button>
        </div>
      </template>

      <template #default>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column key="configName" label="配置名称" prop="configName" min-width="100" />
        <el-table-column key="configKey" label="配置键" prop="configKey" min-width="100" />
        <el-table-column key="configValue" label="配置值" prop="configValue" min-width="100" />
        <el-table-column key="remark" label="描述" prop="remark" min-width="100" />
        <el-table-column fixed="right" label="操作" width="150" align="center">
          <template #default="scope">
            <el-button
              v-hasPerm="['sys:config:update']"
              type="primary"
              link
              icon="edit"
              @click="handleOpenDialog(scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['sys:config:delete']"
              type="danger"
              link
              icon="delete"
              @click="handleDelete(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>

    <!-- 系统配置表单弹窗 -->
    <ProFormDrawer
      ref="dataFormRef"
      v-model="dialog.visible"
      :title="dialog.title"
      :model="formData"
      :rules="rules"
      :loading="loading"
      size="500px"
      label-width="100px"
      :form-attrs="{ labelSuffix: ':' }"
      @submit="handleSubmit"
      @close="handleCloseDialog"
    >
      <el-form-item label="配置名称" prop="configName">
        <el-input v-model="formData.configName" placeholder="请输入配置名称" :maxlength="50" />
      </el-form-item>
      <el-form-item label="配置键" prop="configKey">
        <el-input v-model="formData.configKey" placeholder="请输入配置键" :maxlength="50" />
      </el-form-item>
      <el-form-item label="配置值" prop="configValue">
        <el-input v-model="formData.configValue" placeholder="请输入配置值" :maxlength="100" />
      </el-form-item>
      <el-form-item label="描述" prop="remark">
        <el-input
          v-model="formData.remark"
          :rows="4"
          :maxlength="100"
          show-word-limit
          type="textarea"
          placeholder="请输入描述"
        />
      </el-form-item>
    </ProFormDrawer>
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "Config",
  inheritAttrs: false,
});

import ConfigAPI, { ConfigForm, ConfigPageQuery, ConfigPageVO } from "@/api/system/config-api";
import PageShell from "@/components/PageShell/index.vue";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import { createPageRequest } from "@/utils/pro-table-request";
import { ElMessage, ElMessageBox } from "element-plus";
import { useDebounceFn } from "@vueuse/core";

const queryFormRef = ref();
const dataFormRef = ref();
const tableRef = ref<{ reload: (resetPage?: boolean) => Promise<void> } | null>(null);

const loading = ref(false);

const queryParams = reactive({
  keywords: "",
});

const dialog = reactive({
  title: "",
  visible: false,
});

const formData = reactive<ConfigForm>({
  id: undefined,
  configName: "",
  configKey: "",
  configValue: "",
  remark: "",
});

const rules = reactive({
  configName: [{ required: true, message: "请输入系统配置名称", trigger: "blur" }],
  configKey: [{ required: true, message: "请输入系统配置编码", trigger: "blur" }],
  configValue: [{ required: true, message: "请输入系统配置值", trigger: "blur" }],
});

const requestTableData = createPageRequest<ConfigPageQuery, ConfigPageVO>(ConfigAPI.getPage);

// 查询（重置页码后获取数据）
function handleQuery() {
  tableRef.value?.reload(true);
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value.resetFields();
  tableRef.value?.reload(true);
}

// 打开系统配置弹窗
function handleOpenDialog(id?: string) {
  dialog.visible = true;
  if (id) {
    dialog.title = "修改系统配置";
    ConfigAPI.getFormData(id).then((data) => {
      Object.assign(formData, data);
    });
  } else {
    dialog.title = "新增系统配置";
    formData.id = undefined;
  }
}

// 刷新缓存(防抖)
const handleRefreshCache = useDebounceFn(() => {
  ConfigAPI.refreshCache().then(() => {
    ElMessage.success("刷新成功");
  });
}, 1000);

// 系统配置表单提交
function handleSubmit() {
  dataFormRef.value.validate((valid: any) => {
    if (valid) {
      loading.value = true;
      const id = formData.id;
      if (id) {
        ConfigAPI.update(id, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            tableRef.value?.reload(true);
          })
          .finally(() => (loading.value = false));
      } else {
        ConfigAPI.create(formData)
          .then(() => {
            ElMessage.success("新增成功");
            handleCloseDialog();
            tableRef.value?.reload(true);
          })
          .finally(() => (loading.value = false));
      }
    }
  });
}

// 重置表单
function resetForm() {
  dataFormRef.value.resetFields();
  dataFormRef.value.clearValidate();
  formData.id = undefined;
}

// 关闭系统配置弹窗
function handleCloseDialog() {
  dialog.visible = false;
  resetForm();
}

// 删除系统配置
function handleDelete(id: string) {
  ElMessageBox.confirm("确认删除该项配置?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    loading.value = true;
    ConfigAPI.deleteById(id)
      .then(() => {
        ElMessage.success("删除成功");
        tableRef.value?.reload(true);
      })
      .finally(() => (loading.value = false));
  });
}
</script>
