<template>
  <div class="app-container p-4 md:p-6 flex flex-col gap-4">
    <div class="glass-panel p-5">
      <el-form ref="queryFormRef" :model="queryParams" :inline="true" class="minimal-form mb-0">
        <el-form-item label="关键字" prop="search" class="mb-0">
          <el-input
            v-model="queryParams.search"
            placeholder="输入部门名称"
            @keyup.enter="handleQuery"
            class="minimal-input"
          />
        </el-form-item>

        <el-form-item label="部门状态" prop="status" class="mb-0">
          <el-select v-model="queryParams.status" placeholder="全部" clearable class="minimal-input" style="width: 120px">
            <el-option :value="1" label="正常" />
            <el-option :value="0" label="禁用" />
          </el-select>
        </el-form-item>

        <el-form-item class="search-buttons mb-0 ml-auto">
          <el-button type="primary" icon="search" class="minimal-btn" @click="handleQuery">搜索</el-button>
          <el-button icon="refresh" class="minimal-btn-plain" @click="handleResetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="glass-panel p-5 flex-1 flex flex-col overflow-hidden">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-4 bg-primary rounded-full"></div>
          <span class="text-base font-semibold text-slate-700 tracking-wide">部门数据</span>
        </div>
        <div class="flex gap-2">
          <el-button v-hasPerm="['system:departments:add']" type="primary" icon="plus" class="minimal-btn" @click="handleOpenDialog()">新增部门</el-button>
          <el-button v-hasPerm="['system:departments:delete']" type="danger" plain :disabled="selectIds.length === 0" icon="delete" class="minimal-btn-danger" @click="handleDelete()">批量删除</el-button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden border border-slate-100/50 rounded-xl bg-white/20">
        <el-table
          v-loading="loading"
          :data="deptList"
          row-key="id"
          highlight-current-row
          default-expand-all
          :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
          class="minimal-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column prop="sort" label="排序" width="100" align="center">
            <template #default="{ row }">
              <span class="text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded-md">{{ row.sort }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="部门名称" min-width="200" />
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.status == 1 ? 'success' : 'info'" class="minimal-tag" :class="scope.row.status == 1 ? 'success' : 'info'">
                {{ scope.row.status == 1 ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="280">
            <template #default="scope">
              <el-button v-hasPerm="['system:departments:add']" type="primary" link icon="plus" size="small" @click.stop="handleOpenDialog(scope.row.id, undefined)">新增</el-button>
              <el-button v-hasPerm="['system:departments:edit']" type="primary" link icon="edit" size="small" @click.stop="handleOpenDialog(scope.row.parentId, scope.row.id)">编辑</el-button>
              <el-button v-hasPerm="['system:departments:delete']" type="danger" link icon="delete" size="small" @click.stop="handleDelete(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <el-dialog
      v-model="dialog.visible"
      :title="dialog.title"
      width="600px"
      class="minimal-dialog"
      @closed="handleCloseDialog"
    >
      <el-form ref="deptFormRef" :model="formData" :rules="rules" label-width="80px" class="minimal-form pt-4">
        <el-form-item label="上级部门" prop="parentId">
          <el-tree-select
            v-model="formData.parentId"
            placeholder="选择上级部门"
            :data="deptOptions"
            filterable
            node-key="id"
            check-strictly
            :render-after-expand="false"
            class="minimal-input w-full"
          />
        </el-form-item>
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入部门名称" class="minimal-input" />
        </el-form-item>
        <el-form-item label="显示排序" prop="sort">
          <el-input-number v-model="formData.sort" controls-position="right" style="width: 120px" :min="0" class="minimal-input" />
        </el-form-item>
        <el-form-item label="部门状态">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="handleCloseDialog">取 消</el-button>
          <el-button type="primary" class="minimal-btn" @click="handleSubmit">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Dept",
  inheritAttrs: false,
});

import DeptAPI, { DeptForm, DeptQuery, DeptVO } from "@/api/system/dept-api";

const queryFormRef = ref();
const deptFormRef = ref();

const loading = ref(false);
const selectIds = ref<string[]>([]);
const queryParams = reactive<DeptQuery>({});

const dialog = reactive({
  title: "",
  visible: false,
});

const deptList = ref<DeptVO[]>();
const deptOptions = ref<OptionType[]>();
const formData = reactive<DeptForm>({
  status: 1,
  parentId: undefined,
  sort: 1,
});

const rules = reactive({
  name: [{ required: true, message: "部门名称不能为空", trigger: "blur" }],
  sort: [{ required: true, message: "显示排序不能为空", trigger: "blur" }],
});

function handleQuery() {
  loading.value = true;
  DeptAPI.getList(queryParams).then((data) => {
    deptList.value = data;
    loading.value = false;
  });
}

function handleResetQuery() {
  queryFormRef.value.resetFields();
  handleQuery();
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
  deptFormRef.value.validate((valid: any) => {
    if (valid) {
      loading.value = true;
      const deptId = formData.id;
      if (deptId) {
        DeptAPI.update(deptId, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            handleQuery();
          })
          .finally(() => (loading.value = false));
      } else {
        DeptAPI.create(formData)
          .then(() => {
            ElMessage.success("新增成功");
            handleCloseDialog();
            handleQuery();
          })
          .finally(() => (loading.value = false));
      }
    }
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
      loading.value = true;
      DeptAPI.deleteByIds(deptIds as any)
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

onMounted(() => {
  handleQuery();
});
</script>

<style scoped lang="scss">
/* 玻璃面板样式 */
.glass-panel {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px) saturate(110%);
  -webkit-backdrop-filter: blur(12px) saturate(110%);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.glass-panel:hover {
  box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.08);
}

/* 深色模式 */
html.dark {
  .glass-panel {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.3);
  }
}
</style>
