<!-- 字典项 -->
<template>
  <PageShell class="ff-dict-item-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item label="关键字" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          placeholder="字典项标签/字典项值"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="归属字典" prop="dictSelect" class="mb-0">
        <el-select v-model="queryParams.dict" placeholder="请选择归属字典" clearable filterable>
          <el-option v-for="item in dictList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      title="字典项数据"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:dictitems:add']"
            type="primary"
            icon="plus"
            class="ff-button-primary"
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
            class="ff-button-danger"
            @click="handleDelete()"
          >
            批量删除
          </el-button>
        </div>
      </template>

      <template #default>
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="归属字典" prop="dictName" min-width="120" />
        <el-table-column label="字典项标签" prop="label" min-width="120" />
        <el-table-column label="字典项值" prop="value" min-width="100" />
        <el-table-column label="标签类型" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.tagType" :type="scope.row.tagType" effect="light">
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
              class="ff-status-tag success"
            >
              启用
            </el-tag>
            <el-tag v-else type="info" effect="light" class="ff-status-tag info">禁用</el-tag>
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
      </template>
    </ProTable>

    <!--字典项弹窗-->
    <ProFormDrawer
      ref="dataFormRef"
      v-model="dialog.visible"
      :title="dialog.title"
      :model="formData"
      :rules="computedRules"
      :loading="loading"
      size="600px"
      label-width="100px"
      @close="handleCloseDialog"
      @submit="handleSubmitClick"
    >
      <el-form-item label="归属字典" prop="dict">
        <el-select v-model="formData.dict" placeholder="请选择归属字典" filterable class="w-full">
          <el-option v-for="item in dictList" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="字典项标签" prop="label">
        <el-input v-model="formData.label" placeholder="请输入字典标签" />
      </el-form-item>
      <el-form-item label="字典项值" prop="value">
        <el-input v-model="formData.value" placeholder="请输入字典值" />
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
    </ProFormDrawer>
  </PageShell>
</template>

<script setup lang="ts">
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import DictAPI, { DictPageVO } from "@/api/system/dict-api";
import DictItemAPI, {
  DictItemForm,
  DictItemPageQuery,
  DictItemPageVO,
} from "@/api/system/dict-items-api";
import type { FormRules } from "element-plus";

const route = useRoute();

const dict = route.query.dict as string;
const dataFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const tableRef = ref<ProTableExpose | null>(null);
const dictList = ref<DictPageVO[]>([]);
const formData = reactive<DictItemForm>({});

const loading = ref(false);
const ids = ref<number[]>([]);
const queryParams = reactive<Omit<DictItemPageQuery, "pageNum" | "pageSize">>({});

const dialog = reactive({
  title: "",
  visible: false,
});

const computedRules = computed(() => {
  const rules: FormRules<DictItemForm> = {
    dict: [{ required: true, message: "请选择归属字典", trigger: "change" }],
    value: [{ required: true, message: "请输入字典值", trigger: "blur" }],
    label: [{ required: true, message: "请输入字典标签", trigger: "blur" }],
  };

  return rules;
});

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
  dataFormRef.value?.validate((isValid: boolean) => {
    if (isValid) {
      loading.value = true;
      const id = formData.id;
      if (id) {
        DictItemAPI.updateDictItem(id, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            tableRef.value?.reload(true);
          })
          .finally(() => (loading.value = false));
      } else {
        DictItemAPI.createDictItem(formData)
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

// 关闭弹窗
function handleCloseDialog() {
  dataFormRef.value?.resetFields();
  dataFormRef.value?.clearValidate();

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
        tableRef.value?.reload(true);
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
});
</script>
