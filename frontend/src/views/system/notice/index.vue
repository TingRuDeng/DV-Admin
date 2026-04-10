<template>
  <div class="app-container p-6 bg-[#f8fafc] min-h-screen flex flex-col gap-4">
    <!-- 搜索区域 -->
    <div
      class="bg-white p-5 rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.02)] border border-slate-100 transition-all hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]"
    >
      <el-form
        ref="queryFormRef"
        :model="queryParams"
        :inline="true"
        label-suffix=":"
        class="minimal-form"
      >
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="queryParams.title"
            placeholder="标题"
            clearable
            class="minimal-input"
            @keyup.enter="handleQuery()"
          />
        </el-form-item>

        <el-form-item label="发布状态" prop="publishStatus">
          <el-select
            v-model="queryParams.publishStatus"
            clearable
            placeholder="全部"
            class="minimal-input"
            style="width: 100px"
          >
            <el-option :value="0" label="未发布" />
            <el-option :value="1" label="已发布" />
            <el-option :value="-1" label="已撤回" />
          </el-select>
        </el-form-item>

        <el-form-item class="ml-auto mb-0">
          <el-button type="primary" icon="search" class="minimal-btn" @click="handleQuery()">
            搜索
          </el-button>
          <el-button icon="refresh" class="minimal-btn-plain" @click="handleResetQuery()">
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
          <span class="text-base font-semibold text-slate-700 tracking-wide">通知公告</span>
        </div>
        <div class="flex gap-2">
          <el-button
            v-hasPerm="['sys:notice:add']"
            type="primary"
            icon="plus"
            class="minimal-btn"
            @click="handleOpenDialog()"
          >
            新增通知
          </el-button>
          <el-button
            v-hasPerm="['sys:notice:delete']"
            type="danger"
            plain
            :disabled="selectIds.length === 0"
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
          ref="dataTableRef"
          v-loading="loading"
          :data="pageData"
          highlight-current-row
          class="minimal-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column label="通知标题" prop="title" min-width="200" />
          <el-table-column align="center" label="通知类型" width="150">
            <template #default="scope">
              <DictLabel v-model="scope.row.type" :code="'notice_type'" />
            </template>
          </el-table-column>
          <el-table-column align="center" label="发布人" prop="publisherName" width="150" />
          <el-table-column align="center" label="通知等级" width="100">
            <template #default="scope">
              <DictLabel v-model="scope.row.level" code="notice_level" />
            </template>
          </el-table-column>
          <el-table-column align="center" label="通告目标类型" prop="targetType" width="120">
            <template #default="scope">
              <el-tag
                v-if="scope.row.targetType == 1"
                type="warning"
                effect="light"
                class="minimal-tag warning"
              >
                全体
              </el-tag>
              <el-tag
                v-if="scope.row.targetType == 2"
                type="success"
                effect="light"
                class="minimal-tag success"
              >
                指定
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column align="center" label="发布状态" width="100">
            <template #default="scope">
              <el-tag
                v-if="scope.row.publishStatus == 0"
                type="info"
                effect="light"
                class="minimal-tag info"
              >
                未发布
              </el-tag>
              <el-tag
                v-if="scope.row.publishStatus == 1"
                type="success"
                effect="light"
                class="minimal-tag success"
              >
                已发布
              </el-tag>
              <el-tag
                v-if="scope.row.publishStatus == -1"
                type="warning"
                effect="light"
                class="minimal-tag warning"
              >
                已撤回
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作时间" width="250">
            <template #default="scope">
              <div class="flex items-center gap-1 text-sm">
                <span class="text-slate-400">创建：</span>
                <span>{{ scope.row.createTime || "-" }}</span>
              </div>

              <div v-if="scope.row.publishStatus === 1" class="flex items-center gap-1 text-sm">
                <span class="text-slate-400">发布：</span>
                <span>{{ scope.row.publishTime || "-" }}</span>
              </div>
              <div
                v-else-if="scope.row.publishStatus === -1"
                class="flex items-center gap-1 text-sm"
              >
                <span class="text-slate-400">撤回：</span>
                <span>{{ scope.row.revokeTime || "-" }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column align="center" fixed="right" label="操作" width="200">
            <template #default="scope">
              <el-button type="primary" link @click="openDetailDialog(scope.row.id)">
                查看
              </el-button>
              <el-button
                v-if="scope.row.publishStatus != 1"
                v-hasPerm="['sys:notice:publish']"
                type="primary"
                link
                @click="handlePublish(scope.row.id)"
              >
                发布
              </el-button>
              <el-button
                v-if="scope.row.publishStatus == 1"
                v-hasPerm="['sys:notice:revoke']"
                type="primary"
                link
                @click="handleRevoke(scope.row.id)"
              >
                撤回
              </el-button>
              <el-button
                v-if="scope.row.publishStatus != 1"
                v-hasPerm="['sys:notice:edit']"
                type="primary"
                link
                icon="edit"
                @click="handleOpenDialog(scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-if="scope.row.publishStatus != 1"
                v-hasPerm="['sys:notice:delete']"
                type="danger"
                link
                icon="delete"
                @click="handleDelete(scope.row.id)"
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
        @pagination="fetchData()"
      />
    </div>

    <!-- 通知公告表单弹窗 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.title"
      top="3vh"
      width="80%"
      class="minimal-dialog"
      @close="handleCloseDialog"
    >
      <el-form
        ref="dataFormRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        class="minimal-form pt-4"
      >
        <el-form-item label="通知标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="通知标题"
            clearable
            class="minimal-input"
          />
        </el-form-item>

        <el-form-item label="通知类型" prop="type">
          <Dict v-model="formData.type" code="notice_type" />
        </el-form-item>
        <el-form-item label="通知等级" prop="level">
          <Dict v-model="formData.level" code="notice_level" />
        </el-form-item>
        <el-form-item label="目标类型" prop="targetType">
          <el-radio-group v-model="formData.targetType">
            <el-radio :value="1">全体</el-radio>
            <el-radio :value="2">指定</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="formData.targetType == 2" label="指定用户" prop="targetUserIds">
          <el-select
            v-model="formData.targetUserIds"
            multiple
            search
            placeholder="请选择指定用户"
            class="minimal-input w-full"
          >
            <el-option
              v-for="item in userOptions"
              :key="item.id"
              :label="item.label"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="通知内容" prop="content">
          <WangEditor v-model="formData.content" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer flex justify-end gap-2">
          <el-button class="minimal-btn-plain" @click="handleCloseDialog()">取消</el-button>
          <el-button type="primary" class="minimal-btn" @click="handleSubmit()">确定</el-button>
        </div>
      </template>
    </el-dialog>
    <!-- 通知公告详情 -->
    <el-dialog
      v-model="detailDialog.visible"
      :show-close="false"
      width="50%"
      append-to-body
      class="minimal-dialog"
      @close="closeDetailDialog"
    >
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-semibold text-slate-700">通知公告详情</span>
          <div class="dialog-toolbar">
            <el-button circle @click="closeDetailDialog">
              <template #icon>
                <Close />
              </template>
            </el-button>
          </div>
        </div>
      </template>
      <el-descriptions :column="1">
        <el-descriptions-item label="标题：">
          {{ currentNotice.title }}
        </el-descriptions-item>
        <el-descriptions-item label="发布状态：">
          <el-tag
            v-if="currentNotice.publishStatus == 0"
            type="info"
            effect="light"
            class="minimal-tag info"
          >
            未发布
          </el-tag>
          <el-tag
            v-else-if="currentNotice.publishStatus == 1"
            type="success"
            effect="light"
            class="minimal-tag success"
          >
            已发布
          </el-tag>
          <el-tag
            v-else-if="currentNotice.publishStatus == -1"
            type="warning"
            effect="light"
            class="minimal-tag warning"
          >
            已撤回
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布人：">
          {{ currentNotice.publisherName }}
        </el-descriptions-item>
        <el-descriptions-item label="发布时间：">
          {{ currentNotice.publishTime }}
        </el-descriptions-item>
        <el-descriptions-item label="公告内容：">
          <div class="notice-content" v-html="currentNotice.content" />
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Notice",
  inheritAttrs: false,
});

import NoticeAPI, {
  NoticePageVO,
  NoticeForm,
  NoticePageQuery,
  NoticeDetailVO,
} from "@/api/system/notice-api";
import UserAPI from "@/api/system/user-api";

const queryFormRef = ref();
const dataFormRef = ref();

const loading = ref(false);
const selectIds = ref<number[]>([]);
const total = ref(0);

const queryParams = reactive<NoticePageQuery>({
  pageNum: 1,
  pageSize: 10,
});

const userOptions = ref<OptionType[]>([]);
// 通知公告表格数据
const pageData = ref<NoticePageVO[]>([]);

// 弹窗
const dialog = reactive({
  title: "",
  visible: false,
});

// 通知公告表单数据
const formData = reactive<NoticeForm>({
  level: "L", // 默认优先级为低
  targetType: 1, // 默认目标类型为全体
});

// 通知公告表单校验规则
const rules = reactive({
  title: [{ required: true, message: "请输入通知标题", trigger: "blur" }],
  content: [
    {
      required: true,
      message: "请输入通知内容",
      trigger: "blur",
      validator: (rule: any, value: string, callback: any) => {
        if (!value.replace(/<[^>]+>/g, "").trim()) {
          callback(new Error("请输入通知内容"));
        } else {
          callback();
        }
      },
    },
  ],
  type: [{ required: true, message: "请选择通知类型", trigger: "change" }],
});

const detailDialog = reactive({
  visible: false,
});
const currentNotice = ref<NoticeDetailVO>({});

// 查询通知公告
function handleQuery() {
  queryParams.pageNum = 1;
  fetchData();
}

//发送请求接口
function fetchData() {
  loading.value = true;
  NoticeAPI.getPage(queryParams)
    .then((data) => {
      pageData.value = data.list;
      total.value = data.total;
    })
    .finally(() => {
      loading.value = false;
    });
}

// 重置查询
function handleResetQuery() {
  queryFormRef.value!.resetFields();
  queryParams.pageNum = 1;
  handleQuery();
}

// 行复选框选中项变化
function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
}

// 打开通知公告弹窗
function handleOpenDialog(id?: string) {
  UserAPI.getOptions().then((data) => {
    userOptions.value = data;
  });

  dialog.visible = true;
  if (id) {
    dialog.title = "修改公告";
    NoticeAPI.getFormData(id).then((data) => {
      Object.assign(formData, data);
    });
  } else {
    Object.assign(formData, { level: 0, targetType: 0 });
    dialog.title = "新增公告";
  }
}

// 发布通知公告
function handlePublish(id: string) {
  NoticeAPI.publish(id).then(() => {
    ElMessage.success("发布成功");
    handleQuery();
  });
}

// 撤回通知公告
function handleRevoke(id: string) {
  NoticeAPI.revoke(id).then(() => {
    ElMessage.success("撤回成功");
    handleQuery();
  });
}

// 通知公告表单提交
function handleSubmit() {
  dataFormRef.value.validate((valid: any) => {
    if (valid) {
      loading.value = true;
      const id = formData.id;
      if (id) {
        NoticeAPI.update(id, formData)
          .then(() => {
            ElMessage.success("修改成功");
            handleCloseDialog();
            handleResetQuery();
          })
          .finally(() => (loading.value = false));
      } else {
        NoticeAPI.create(formData)
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
  formData.targetType = 1;
}

// 关闭通知公告弹窗
function handleCloseDialog() {
  dialog.visible = false;
  resetForm();
}

// 删除通知公告
function handleDelete(id?: number) {
  const deleteIds = [id || selectIds.value].join(",");
  if (!deleteIds) {
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
      NoticeAPI.deleteByIds(deleteIds)
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

const closeDetailDialog = () => {
  detailDialog.visible = false;
};

const openDetailDialog = async (id: string) => {
  const noticeDetail = await NoticeAPI.getDetail(id);
  currentNotice.value = noticeDetail;
  detailDialog.visible = true;
};

onMounted(() => {
  handleQuery();
});
</script>
