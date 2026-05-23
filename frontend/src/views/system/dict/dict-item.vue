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

    <DictItemFormDrawer ref="dictItemFormDrawerRef" :dict-list="dictList" @success="handleQuery" />
  </PageShell>
</template>

<script setup lang="ts">
import type { ProTableExpose } from "@/components/ProTable/types";
import { createPageRequest } from "@/utils/pro-table-request";
import DictAPI, { DictPageVO } from "@/api/system/dict-api";
import DictItemAPI, { DictItemPageQuery, DictItemPageVO } from "@/api/system/dict-items-api";
import DictItemFormDrawer from "./components/DictItemFormDrawer.vue";

const route = useRoute();

const dict = route.query.dict as string;
const dictItemFormDrawerRef = ref<InstanceType<typeof DictItemFormDrawer> | null>(null);
const queryFormRef = ref<{ resetFields: () => void } | null>(null);
const tableRef = ref<ProTableExpose | null>(null);
const dictList = ref<DictPageVO[]>([]);

const ids = ref<number[]>([]);
const queryParams = reactive<Omit<DictItemPageQuery, "pageNum" | "pageSize">>({});

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
async function handleOpenDialog(id?: number) {
  if (id) {
    await dictItemFormDrawerRef.value?.openEdit(id);
    return;
  }
  await dictItemFormDrawerRef.value?.openCreate(queryParams.dict);
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
