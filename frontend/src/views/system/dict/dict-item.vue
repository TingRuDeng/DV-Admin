<!-- 字典项 -->
<template>
  <div class="app-container p-6 bg-[#f8fafc] min-h-screen flex flex-col gap-4">
    <div
      class="bg-white p-5 rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.02)] border border-slate-100 transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]"
    >
      <el-form ref="queryFormRef" :model="queryParams" :inline="true" class="minimal-form">
        <el-form-item label="关键字" prop="search">
          <el-input
            v-model="queryParams.search"
            placeholder="字典项标签/字典项值"
            clearable
            class="minimal-input"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="归属字典" prop="dictSelect">
          <el-select
            v-model="queryParams.dict"
            placeholder="请选择归属字典"
            clearable
            filterable
            class="minimal-input"
          >
            <el-option
              v-for="item in dictList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item class="ml-auto mb-0">
          <el-button type="primary" icon="search" class="minimal-btn" @click="handleQuery">
            搜索
          </el-button>
          <el-button icon="refresh" class="minimal-btn-plain" @click="handleResetQuery">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div
      class="bg-white p-6 flex-1 rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.02)] border border-slate-100 flex flex-col transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]"
    >
      <div class="flex justify-between items-center mb-5">
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-4 bg-primary rounded-full"></div>
          <span class="text-base font-semibold text-slate-700 tracking-wide">字典项数据</span>
        </div>
        <div class="flex gap-2">
          <el-button
            v-hasPerm="['system:dictitems:add']"
            type="primary"
            icon="plus"
            class="minimal-btn"
            @click="handleOpenDialog()"
          >
            新增字典项
          </el-button>
          <el-button
            v-hasPerm="['system:dictitems:delete']"
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
          <el-table-column label="归属字典" prop="dictName" min-width="120" />
          <el-table-column label="字典项标签" prop="label" min-width="120" />
          <el-table-column label="字典项值" prop="value" min-width="100" />
          <el-table-column label="标签类型" width="100" align="center">
            <template #default="scope">
              <el-tag
                v-if="scope.row.tagType"
                :type="scope.row.tagType"
                effect="light"
                class="minimal-tag"
              >
                {{ scope.row.tagType }}
              </el-tag>
              <span v-else class="text-slate-400">无</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="scope">
              <el-tag
                v-if="scope.row.status === 1"
                type="success"
                effect="light"
                class="minimal-tag success"
              >
                启用
              </el-tag>
              <el-tag v-else type="info" effect="light" class="minimal-tag info">禁用</el-tag>
            </template>
          </el-table-column>

          <el-table-column fixed="right" label="操作" width="200">
            <template #default="scope">
              <el-button
                v-hasPerm="['system:dictitems:edit']"
                type="primary"
                link
                icon="edit"
                @click.stop="handleOpenDialog(scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-hasPerm="['system:dictitems:delete']"
                type="danger"
                link
                icon="delete"
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

    <!--字典项弹窗-->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.title"
      width="600px"
      class="minimal-dialog"
      @close="handleCloseDialog"
    >
      <el-form
        ref="dataFormRef"
        :model="formData"
        :rules="computedRules"
        label-width="100px"
        class="minimal-form pt-4"
      >
        <el-form-item label="归属字典" prop="dict">
          <el-select
            v-model="formData.dict"
            placeholder="请选择归属字典"
            filterable
            class="minimal-input w-full"
          >
            <el-option
              v-for="item in dictList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="字典项标签" prop="label">
          <el-input v-model="formData.label" placeholder="请输入字典标签" class="minimal-input" />
        </el-form-item>
        <el-form-item label="字典项值" prop="value">
          <el-input v-model="formData.value" placeholder="请输入字典值" class="minimal-input" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标签类型">
          <el-tag v-if="formData.tagType" :type="formData.tagType" class="mr-2">
            {{ formData.label }}
          </el-tag>
          <el-radio-group v-model="formData.tagType">
            <el-radio value="success" border size="small">success</el-radio>
            <el-radio value="warning" border size="small">warning</el-radio>
            <el-radio value="info" border size="small">info</el-radio>
            <el-radio value="primary" border size="small">primary</el-radio>
            <el-radio value="danger" border size="small">danger</el-radio>
            <el-radio value="" border size="small">清空</el-radio>
          </el-radio-group>
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
import DictAPI, { DictPageVO } from "@/api/system/dict-api";
import DictItemAPI, {
  DictItemForm,
  DictItemPageVO,
  DictItemPageQuery,
} from "@/api/system/dict-items-api";

const route = useRoute();

const dict = route.query.dict as string;
const dataFormRef = ref();
const queryFormRef = ref();
const dictList = ref<DictPageVO[]>([]);
const formData = reactive<DictItemForm>({});

const loading = ref(false);
const ids = ref<number[]>([]);
const total = ref(0);

const queryParams = reactive<DictItemPageQuery>({
  pageNum: 1,
  pageSize: 10,
});

const tableData = ref<DictItemPageVO[]>();

const dialog = reactive({
  title: "",
  visible: false,
});

const computedRules = computed(() => {
  const rules: Partial<Record<string, any>> = {
    dict: [{ required: true, message: "请选择归属字典", trigger: "change" }],
    value: [{ required: true, message: "请输入字典值", trigger: "blur" }],
    label: [{ required: true, message: "请输入字典标签", trigger: "blur" }],
  };

  return rules;
});

// 获取数据
function fetchData() {
  loading.value = true;
  DictItemAPI.getDictItemPage(queryParams)
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

// 打开弹窗
function handleOpenDialog(id?: number) {
  dialog.visible = true;
  dialog.title = id ? "编辑字典项" : "新增字典项";

  if (id) {
    DictItemAPI.getDictItemFormData(id).then((data) => {
      Object.assign(formData, data);
    });
  }
}

// 提交表单
function handleSubmitClick() {
  dataFormRef.value.validate((isValid: boolean) => {
    if (isValid) {
      loading.value = true;
      const id = formData.id;
      if (id) {
        DictItemAPI.updateDictItem(id, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            handleQuery();
          })
          .finally(() => (loading.value = false));
      } else {
        DictItemAPI.createDictItem(formData)
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

// 关闭弹窗
function handleCloseDialog() {
  dataFormRef.value.resetFields();
  dataFormRef.value.clearValidate();

  formData.id = undefined;
  formData.status = 1;
  formData.tagType = "";

  dialog.visible = false;
}
/**
 * 删除字典
 *
 * @param id 字典ID
 */
function handleDelete(id?: number) {
  const itemIds = id !== undefined ? [id] : ids.value;
  if (!itemIds) {
    ElMessage.warning("请勾选删除项");
    return;
  }
  ElMessageBox.confirm("确认删除已选中的数据项?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(
    () => {
      DictItemAPI.deleteDictItems(itemIds).then(() => {
        ElMessage.success("删除成功");
        handleResetQuery();
      });
    },
    () => {
      ElMessage.info("已取消删除");
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
