<!-- 字典 -->
<template>
  <div class="app-container p-4 md:p-6 flex flex-col gap-4">
    <!-- 搜索区域 -->
    <div class="glass-panel p-5">
      <el-form ref="queryFormRef" :model="queryParams" :inline="true" class="minimal-form mb-0">
        <el-form-item label="关键字" prop="search" class="mb-0">
          <el-input
            v-model="queryParams.search"
            placeholder="字典名称/编码"
            clearable
            class="minimal-input"
            @keyup.enter="handleQuery"
          />
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
          <span class="text-base font-semibold text-slate-700 tracking-wide">字典数据</span>
        </div>
        <div class="flex gap-2">
          <el-button v-hasPerm="['system:dicts:add']" type="primary" icon="plus" class="minimal-btn" @click="handleAddClick()">新增字典</el-button>
          <el-button v-hasPerm="['system:dicts:delete']" type="danger" plain :disabled="ids.length === 0" icon="delete" class="minimal-btn-danger" @click="handleDelete()">批量删除</el-button>
        </div>
      </div>

      <div class="flex-1 overflow-hidden border border-slate-100/50 rounded-xl bg-white/20">
        <el-table
          v-loading="loading"
          highlight-current-row
          :data="tableData"
          class="minimal-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="字典名称" prop="name" min-width="150" />
          <el-table-column label="字典编码" prop="dictCode" min-width="150" />
          <el-table-column label="状态" prop="status" width="100" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.status === 1 ? 'success' : 'info'" class="minimal-tag" :class="scope.row.status === 1 ? 'success' : 'info'">
                {{ scope.row.status === 1 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" width="280">
            <template #default="scope">
              <el-button v-hasPerm="['system:dictitems:query']" type="primary" link size="small" @click.stop="handleOpenDictData(scope.row)">
                <template #icon><Collection /></template>
                字典数据
              </el-button>
              <el-button v-hasPerm="['system:dicts:edit']" type="primary" link icon="edit" size="small" @click.stop="handleEditClick(scope.row.id)">编辑</el-button>
              <el-button v-hasPerm="['system:dicts:delete']" type="danger" link icon="delete" size="small" @click.stop="handleDelete(scope.row.id)">删除</el-button>
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

    <!--字典弹窗-->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.title"
      width="500px"
      class="minimal-dialog"
      @close="handleCloseDialog"
    >
      <el-form ref="dataFormRef" :model="formData" :rules="computedRules" label-width="80px" class="minimal-form pt-4">
        <el-form-item label="字典名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入字典名称" class="minimal-input" />
        </el-form-item>

        <el-form-item label="字典编码" prop="dictCode">
          <el-input v-model="formData.dictCode" placeholder="请输入字典编码" class="minimal-input" />
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" placeholder="请输入备注" class="minimal-input" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="handleCloseDialog">取 消</el-button>
          <el-button type="primary" class="minimal-btn" @click="handleSubmitClick">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Dict",
  inherititems: false,
});

import DictAPI, { DictPageQuery, DictPageVO } from "@/api/system/dict-api";

import router from "@/router";

const queryFormRef = ref();
const dataFormRef = ref();

const loading = ref(false);
const ids = ref<number[]>([]);
const total = ref(0);

const queryParams = reactive<DictPageQuery>({
  pageNum: 1,
  pageSize: 10,
});

const tableData = ref<DictPageVO[]>();

const dialog = reactive({
  title: "",
  visible: false,
});

const formData = reactive({
  id: undefined,
  name: "",
  dictCode: "",
  status: 1,
  remark: "",
});

const computedRules = computed(() => {
  const rules: Partial<Record<string, any>> = {
    name: [{ required: true, message: "请输入字典名称", trigger: "blur" }],
    dictCode: [{ required: true, message: "请输入字典编码", trigger: "blur" }],
  };
  return rules;
});

// 获取数据
function fetchData() {
  loading.value = true;
  DictAPI.getPage(queryParams)
    .then((data) => {
      tableData.value = data.list;
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

// 行选择
function handleSelectionChange(selection: any) {
  ids.value = selection.map((item: any) => item.id);
}

// 新增字典
function handleAddClick() {
  dialog.visible = true;
  dialog.title = "新增字典";
}

/**
 * 编辑字典
 *
 * @param id 字典ID
 */
function handleEditClick(id: string) {
  dialog.visible = true;
  dialog.title = "修改字典";
  DictAPI.getFormData(id).then((data) => {
    Object.assign(formData, data);
  });
}

// 提交字典表单
function handleSubmitClick() {
  dataFormRef.value.validate((isValid: boolean) => {
    if (isValid) {
      loading.value = true;
      const id = formData.id;
      if (id) {
        DictAPI.update(id, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            handleQuery();
          })
          .finally(() => (loading.value = false));
      } else {
        DictAPI.create(formData)
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

// 关闭字典弹窗
function handleCloseDialog() {
  dialog.visible = false;

  dataFormRef.value.resetFields();
  dataFormRef.value.clearValidate();

  formData.id = undefined;
  formData.status = 1;
  formData.name = "";
  formData.remark = "";
  formData.dictCode = "";
}
/**
 * 删除字典
 *
 * @param id 字典ID
 */
function handleDelete(id?: number) {
  const attrGroupIds = id !== undefined ? [id] : ids.value;
  if (!attrGroupIds) {
    ElMessage.warning("请勾选删除项");
    return;
  }
  ElMessageBox.confirm("确认删除已选中的数据项?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(
    () => {
      DictAPI.deleteByIds(attrGroupIds).then(() => {
        ElMessage.success("删除成功");
        handleResetQuery();
      });
    },
    () => {
      ElMessage.info("已取消删除");
    }
  );
}

// 打开字典项
function handleOpenDictData(row: DictPageVO) {
  if (!row || !row.id || !row.name) {
    ElMessage.warning("字典数据无效");
    return;
  }

  router.push({
    path: "dict-item",
    query: {
      dict: row.id,
    },
  });
}

onMounted(() => {
  handleQuery();
});
</script>
