<template>
  <PageShell class="ff-dept-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item label="关键字" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          placeholder="输入部门名称"
          @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item label="部门状态" prop="status" class="mb-0">
        <el-select v-model="queryParams.status" placeholder="全部" clearable style="width: 120px">
          <el-option :value="1" label="正常" />
          <el-option :value="0" label="禁用" />
        </el-select>
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      title="部门数据"
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
            icon="plus"
            class="ff-button-primary"
            @click="handleOpenDialog()"
          >
            新增部门
          </el-button>
          <el-button
            v-hasPerm="['system:departments:delete']"
            type="danger"
            plain
            :disabled="selectIds.length === 0"
            icon="delete"
            class="ff-button-danger"
            @click="handleDelete()"
          >
            批量删除
          </el-button>
        </div>
      </template>

      <template #default>
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="sort" label="排序" width="100" align="center">
          <template #default="{ row }">
            <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">
              {{ row.sort }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="部门名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.status == 1 ? 'success' : 'info'"
              class="ff-status-tag"
              :class="scope.row.status == 1 ? 'success' : 'info'"
            >
              {{ scope.row.status == 1 ? "正常" : "禁用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="scope">
            <el-button
              v-hasPerm="['system:departments:add']"
              type="primary"
              link
              icon="plus"
              size="small"
              @click.stop="handleOpenDialog(scope.row.id, undefined)"
            >
              新增
            </el-button>
            <el-button
              v-hasPerm="['system:departments:edit']"
              type="primary"
              link
              icon="edit"
              size="small"
              @click.stop="handleOpenDialog(scope.row.parentId, scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['system:departments:delete']"
              type="danger"
              link
              icon="delete"
              size="small"
              @click.stop="handleDelete(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </template>
    </ProTable>

    <ProFormDrawer
      ref="deptFormRef"
      v-model="dialog.visible"
      :title="dialog.title"
      :model="formData"
      :rules="rules"
      :loading="formLoading"
      size="600px"
      label-width="80px"
      @submit="handleSubmit"
      @close="handleCloseDialog"
    >
      <el-form-item label="上级部门" prop="parentId">
        <el-tree-select
          v-model="formData.parentId"
          placeholder="选择上级部门"
          :data="deptOptions"
          filterable
          node-key="id"
          check-strictly
          :render-after-expand="false"
          class="w-full"
        />
      </el-form-item>
      <el-form-item label="部门名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入部门名称" />
      </el-form-item>
      <el-form-item label="显示排序" prop="sort">
        <el-input-number
          v-model="formData.sort"
          controls-position="right"
          style="width: 120px"
          :min="0"
        />
      </el-form-item>
      <el-form-item label="部门状态">
        <el-radio-group v-model="formData.status">
          <el-radio :value="1">正常</el-radio>
          <el-radio :value="0">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
    </ProFormDrawer>
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "Dept",
  inheritAttrs: false,
});

import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";
import { createListRequest } from "@/utils/pro-table-request";
import DeptAPI, { DeptForm, DeptQuery, DeptVO } from "@/api/system/dept-api";

const queryFormRef = ref();
const deptFormRef = ref();
const tableRef = ref<{ reload: (resetPage?: boolean) => Promise<void> } | null>(null);

const formLoading = ref(false);
const selectIds = ref<string[]>([]);
const queryParams = reactive<DeptQuery>({});

const dialog = reactive({
  title: "",
  visible: false,
});

const deptOptions = ref<OptionType[]>([]);
const formData = reactive<DeptForm>({
  status: 1,
  parentId: undefined,
  sort: 1,
});

const rules = reactive({
  name: [{ required: true, message: "部门名称不能为空", trigger: "blur" }],
  sort: [{ required: true, message: "显示排序不能为空", trigger: "blur" }],
});

const requestTableData = createListRequest<DeptQuery, DeptVO>(DeptAPI.getList, {
  stripPagination: true,
});

function handleQuery() {
  tableRef.value?.reload(true);
}

function handleResetQuery() {
  queryFormRef.value.resetFields();
  tableRef.value?.reload(true);
}

function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
}

async function handleOpenDialog(parentId?: string, deptId?: string) {
  deptOptions.value = await DeptAPI.getOptions();
  dialog.visible = true;
  if (deptId) {
    dialog.title = "修改部门";
    DeptAPI.getFormData(deptId).then((data) => {
      Object.assign(formData, data);
    });
  } else {
    dialog.title = "新增部门";
    formData.parentId = parentId;
  }
}

function handleSubmit() {
  formLoading.value = true;
  deptFormRef.value.validate((valid: any) => {
    if (valid) {
      const deptId = formData.id;
      if (deptId) {
        DeptAPI.update(deptId, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            tableRef.value?.reload(true);
          })
          .finally(() => (formLoading.value = false));
      } else {
        DeptAPI.create(formData)
          .then(() => {
            ElMessage.success("新增成功");
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

function handleDelete(deptId?: number) {
  const deptIds = deptId !== undefined ? [deptId] : selectIds.value;
  if (!deptIds || (Array.isArray(deptIds) && deptIds.length === 0)) {
    ElMessage.warning("请勾选删除项");
    return;
  }

  ElMessageBox.confirm("确认删除已选中的数据项?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(
    () => {
      DeptAPI.deleteByIds(deptIds as any)
        .then(() => {
          ElMessage.success("删除成功");
          tableRef.value?.reload(true);
        })
        .finally(() => undefined);
    },
    () => {
      ElMessage.info("已取消删除");
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
