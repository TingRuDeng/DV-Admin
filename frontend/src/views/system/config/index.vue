<!-- 系统配置 -->
<template>
  <div class="app-container p-6 bg-[#f8fafc] min-h-screen flex flex-col gap-4">
    <!-- 搜索区域 -->
    <div class="bg-white p-5 rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.02)] border border-slate-100 transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]">
      <el-form ref="queryFormRef" :model="queryParams" :inline="true" class="minimal-form">
        <el-form-item label="关键字" prop="keywords">
          <el-input
            v-model="queryParams.keywords"
            placeholder="请输入配置键\配置名称"
            clearable
            class="minimal-input"
            @keyup.enter="handleQuery"
          />
        </el-form-item>

        <el-form-item class="ml-auto mb-0">
          <el-button type="primary" icon="search" class="minimal-btn" @click="handleQuery">搜索</el-button>
          <el-button icon="refresh" class="minimal-btn-plain" @click="handleResetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="bg-white p-6 flex-1 rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.02)] border border-slate-100 flex flex-col transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]">
      <div class="flex justify-between items-center mb-5">
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-4 bg-primary rounded-full"></div>
          <span class="text-base font-semibold text-slate-700 tracking-wide">系统配置</span>
        </div>
        <div class="flex gap-2">
          <el-button
            v-hasPerm="['sys:config:add']"
            type="primary"
            icon="plus"
            class="minimal-btn"
            @click="handleOpenDialog()"
          >
            新增配置
          </el-button>
          <el-button
            v-hasPerm="['sys:config:refresh']"
            color="#626aef"
            icon="RefreshLeft"
            class="minimal-btn"
            @click="handleRefreshCache"
          >
            刷新缓存
          </el-button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden border border-slate-100/50 rounded-xl bg-white/20">
        <el-table
          ref="dataTableRef"
          v-loading="loading"
          :data="pageData"
          highlight-current-row
          class="minimal-table"
          @selection-change="handleSelectionChange"
        >
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
              >编辑</el-button>
              <el-button
                v-hasPerm="['sys:config:delete']"
                type="danger"
                link
                icon="delete"
                @click="handleDelete(scope.row.id)"
              >删除</el-button>
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

    <!-- 系统配置表单弹窗 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.title"
      width="500px"
      class="minimal-dialog"
      @close="handleCloseDialog"
    >
      <el-form
        ref="dataFormRef"
        :model="formData"
        :rules="rules"
        label-suffix=":"
        label-width="100px"
        class="minimal-form pt-4"
      >
        <el-form-item label="配置名称" prop="configName">
          <el-input v-model="formData.configName" placeholder="请输入配置名称" :maxlength="50" class="minimal-input" />
        </el-form-item>
        <el-form-item label="配置键" prop="configKey">
          <el-input v-model="formData.configKey" placeholder="请输入配置键" :maxlength="50" class="minimal-input" />
        </el-form-item>
        <el-form-item label="配置值" prop="configValue">
          <el-input v-model="formData.configValue" placeholder="请输入配置值" :maxlength="100" class="minimal-input" />
        </el-form-item>
        <el-form-item label="描述" prop="remark">
          <el-input
            v-model="formData.remark"
            :rows="4"
            :maxlength="100"
            show-word-limit
            type="textarea"
            placeholder="请输入描述"
            class="minimal-input"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="handleCloseDialog">取消</el-button>
          <el-button type="primary" class="minimal-btn" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Config",
  inheritAttrs: false,
});

import ConfigAPI, { ConfigPageVO, ConfigForm, ConfigPageQuery } from "@/api/system/config-api";
import { ElMessage, ElMessageBox } from "element-plus";
import { useDebounceFn } from "@vueuse/core";

const queryFormRef = ref();
const dataFormRef = ref();

const loading = ref(false);
const selectIds = ref<number[]>([]);
const total = ref(0);

const queryParams = reactive<ConfigPageQuery>({
  pageNum: 1,
  pageSize: 10,
  keywords: "",
});

// 系统配置表格数据
const pageData = ref<ConfigPageVO[]>([]);

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

// 获取数据
function fetchData() {
  loading.value = true;
  ConfigAPI.getPage(queryParams)
    .then((data) => {
      pageData.value = data.list;
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

// 行复选框选中项变化
function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
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
            handleResetQuery();
          })
          .finally(() => (loading.value = false));
      } else {
        ConfigAPI.create(formData)
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
        handleResetQuery();
      })
      .finally(() => (loading.value = false));
  });
}

onMounted(() => {
  handleQuery();
});
</script>
