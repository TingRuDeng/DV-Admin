<!-- 字典项 -->
<template>
  <div class="app-container p-4 md:p-6 flex flex-col gap-4">
    <div class="glass-panel p-5">
      <el-form ref="queryFormRef" :model="queryParams" :inline="true" class="minimal-form mb-0">
        <el-form-item label="关键字" prop="search" class="mb-0">
          <el-input
            v-model="queryParams.search"
            placeholder="字典项标签/字典项值"
            clearable
            class="minimal-input"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="归属字典" prop="dictSelect" class="mb-0">
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

<!-- 全局穿透样式已统一至 @/styles/_minimal-saas.scss，此处不再重复定义 -->
