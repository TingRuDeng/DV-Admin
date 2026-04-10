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
          <el-button type="primary" icon="search" class="minimal-btn" @click="handleQuery">
            搜索
          </el-button>
          <el-button icon="refresh" class="minimal-btn-plain" @click="handleResetQuery">
            重置
          </el-button>
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
          <el-button
            v-hasPerm="['system:dicts:add']"
            type="primary"
            icon="plus"
            class="minimal-btn"
            @click="handleAddClick()"
          >
            新增字典
          </el-button>
          <el-button
            v-hasPerm="['system:dicts:delete']"
            type="danger"
            plain
            :disabled="ids.length === 0"
            icon="delete"
            class="minimal-btn-danger"
            @click="handleDelete()"
          >
            批量删除
          </el-button>
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
              <el-tag
                :type="scope.row.status === 1 ? 'success' : 'info'"
                class="minimal-tag"
                :class="scope.row.status === 1 ? 'success' : 'info'"
              >
                {{ scope.row.status === 1 ? "启用" : "禁用" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" width="280">
            <template #default="scope">
              <el-button
                v-hasPerm="['system:dictitems:query']"
                type="primary"
                link
                size="small"
                @click.stop="handleOpenDictData(scope.row)"
              >
                <template #icon><Collection /></template>
                字典数据
              </el-button>
              <el-button
                v-hasPerm="['system:dicts:edit']"
                type="primary"
                link
                icon="edit"
                size="small"
                @click.stop="handleEditClick(scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['system:dicts:delete']"
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
      <el-form
        ref="dataFormRef"
        :model="formData"
        :rules="computedRules"
        label-width="80px"
        class="minimal-form pt-4"
      >
        <el-form-item label="字典名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入字典名称" class="minimal-input" />
        </el-form-item>

        <el-form-item label="字典编码" prop="dictCode">
          <el-input
            v-model="formData.dictCode"
            placeholder="请输入字典编码"
            class="minimal-input"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="formData.remark"
            type="textarea"
            placeholder="请输入备注"
            class="minimal-input"
          />
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

<!-- 页面特定样式 (scoped) -->
<style scoped lang="scss">
/* 页面特定样式 - 无 */
</style>

<!-- 全局穿透样式 (非 scoped，用于覆盖 Element Plus) -->
<style lang="scss">
/* stylelint-disable no-descending-specificity */
/* 玻璃面板样式 */
.glass-panel {
  background: rgba(255, 255, 255, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.8) !important;
  border-radius: 16px;
  box-shadow: 0 8px 32px -8px rgba(0, 0, 0, 0.05) !important;
  -webkit-backdrop-filter: blur(16px) saturate(120%);
  backdrop-filter: blur(16px) saturate(120%);
  transition: all 0.3s ease;
}

.glass-panel:hover {
  box-shadow: 0 12px 48px -12px rgba(0, 0, 0, 0.08) !important;
}

/* 表格净化 */
.minimal-table {
  background: transparent !important;
  --el-table-border-color: rgba(0, 0, 0, 0.04);
  --el-table-header-bg-color: rgba(0, 0, 0, 0.02);
  --el-table-header-text-color: #475569;
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.6);
  --el-table-tr-bg-color: transparent;
}

.minimal-table th.el-table__cell {
  font-weight: 600;
  border-bottom: 2px solid rgba(0, 0, 0, 0.06) !important;
}

.minimal-table td.el-table__cell {
  border-bottom: 1px dashed rgba(0, 0, 0, 0.04) !important;
}

.minimal-table .el-table__inner-wrapper::before {
  display: none;
}

/* 表单输入框圆润化 */
.minimal-input .el-input__wrapper,
.minimal-input.el-select .el-select__wrapper {
  background-color: rgba(255, 255, 255, 0.6) !important;
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #cbd5e1 inset !important;
  transition: all 0.2s ease;
}

.minimal-input .el-input__wrapper.is-focus,
.minimal-input.el-select .el-select__wrapper.is-focus {
  background-color: #ffffff !important;
  box-shadow:
    0 0 0 1px var(--el-color-primary) inset,
    0 0 0 3px rgba(64, 128, 255, 0.1) !important;
}

/* 按钮与标签高级感 */
.minimal-btn {
  font-weight: 500;
  border: none;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(64, 128, 255, 0.2);
  transition: all 0.2s ease;
}

.minimal-btn:hover {
  box-shadow: 0 4px 8px rgba(64, 128, 255, 0.3);
  transform: translateY(-1px);
}

.minimal-btn-plain {
  color: #64748b;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}

.minimal-btn-plain:hover {
  color: var(--el-color-primary);
  background: #ffffff;
  border-color: var(--el-color-primary);
}

.minimal-tag {
  padding: 0 12px !important;
  font-weight: 500 !important;
  border: none !important;
  border-radius: 6px !important;
}

.minimal-tag.success {
  color: #16a34a !important;
  background-color: #dcfce7 !important;
}

.minimal-tag.info {
  color: #64748b !important;
  background-color: #f1f5f9 !important;
}

/* 分页组件融化 */
.minimal-pagination {
  justify-content: flex-end;
}

.minimal-pagination button,
.minimal-pagination li {
  background: transparent !important;
}

.minimal-pagination li.is-active {
  color: white !important;
  background: var(--el-color-primary) !important;
  border-radius: 6px;
}

/* 表格内操作按钮"软徽章化" */
.minimal-table .el-button.is-link {
  height: auto !important;
  padding: 6px 10px !important;
  font-weight: 500 !important;
  border-radius: 8px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.minimal-table .el-button--primary.is-link {
  color: #64748b !important;
}

.minimal-table .el-button--primary.is-link:hover {
  color: var(--el-color-primary) !important;
  background-color: rgba(64, 128, 255, 0.1) !important;
}

.minimal-table .el-button--danger.is-link {
  color: #94a3b8 !important;
}

.minimal-table .el-button--danger.is-link:hover {
  color: #ef4444 !important;
  background-color: rgba(239, 68, 68, 0.1) !important;
}

.minimal-table .el-table__cell .cell {
  display: flex;
  gap: 4px;
  align-items: center;
}

/* 深色模式 */
html.dark .glass-panel {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.3);
}
</style>
