<!-- 字典 -->
<template>
  <PageShell class="ff-dict-page">
    <ProSearch
      ref="queryFormRef"
      :model="queryParams"
      @submit="handleQuery"
      @reset="handleResetQuery"
    >
      <el-form-item label="关键字" prop="search" class="mb-0">
        <el-input
          v-model="queryParams.search"
          placeholder="字典名称/编码"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
    </ProSearch>

    <ProTable
      ref="tableRef"
      title="字典数据"
      :request="requestTableData"
      :params="queryParams"
      @selection-change="handleSelectionChange"
    >
      <template #actions>
        <div class="ff-button-group">
          <el-button
            v-hasPerm="['system:dicts:add']"
            type="primary"
            icon="plus"
            class="ff-button-primary"
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
            class="ff-button-danger"
            @click="handleDelete()"
          >
            批量删除
          </el-button>
        </div>
      </template>

      <template #default>
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="字典名称" prop="name" min-width="150" />
        <el-table-column label="字典编码" prop="dictCode" min-width="150" />
        <el-table-column label="状态" prop="status" width="100" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === 1 ? 'success' : 'info'"
              class="ff-status-tag"
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
      </template>
    </ProTable>

    <!--字典弹窗-->
    <ProFormDrawer
      ref="dataFormRef"
      v-model="dialog.visible"
      :title="dialog.title"
      :model="formData"
      :rules="computedRules"
      :loading="loading"
      size="500px"
      label-width="80px"
      @submit="handleSubmitClick"
      @close="handleCloseDialog"
    >
      <el-form-item label="字典名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入字典名称" />
      </el-form-item>

      <el-form-item label="字典编码" prop="dictCode">
        <el-input v-model="formData.dictCode" placeholder="请输入字典编码" />
      </el-form-item>

      <el-form-item label="状态">
        <el-radio-group v-model="formData.status">
          <el-radio :value="1">启用</el-radio>
          <el-radio :value="0">禁用</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="备注">
        <el-input v-model="formData.remark" type="textarea" placeholder="请输入备注" />
      </el-form-item>
    </ProFormDrawer>
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "Dict",
  inheritAttrs: false,
});

import DictAPI, { DictPageQuery, DictPageVO } from "@/api/system/dict-api";
import PageShell from "@/components/PageShell/index.vue";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import ProSearch from "@/components/ProSearch/index.vue";
import ProTable from "@/components/ProTable/index.vue";

import router from "@/router";

const queryFormRef = ref();
const dataFormRef = ref();
const tableRef = ref<{ reload: (resetPage?: boolean) => Promise<void> } | null>(null);

const loading = ref(false);
const ids = ref<number[]>([]);

const queryParams = reactive<Omit<DictPageQuery, "pageNum" | "pageSize">>({});

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

function requestTableData(params: Record<string, unknown>) {
  return DictAPI.getPage(params as unknown as DictPageQuery);
}

// 查询（重置页码后获取数据）
function handleQuery() {
  tableRef.value?.reload(true);
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value.resetFields();
  tableRef.value?.reload(true);
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
            tableRef.value?.reload(true);
          })
          .finally(() => (loading.value = false));
      } else {
        DictAPI.create(formData)
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
        tableRef.value?.reload(true);
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
</script>
