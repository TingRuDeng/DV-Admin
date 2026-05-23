<template>
  <ProFormDrawer
    ref="noticeFormRef"
    v-model="dialogState.visible"
    :title="dialogState.title"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    size="80%"
    label-width="100px"
    @close="handleClose"
    @submit="handleSubmitWrapper"
  >
    <el-form-item label="通知标题" prop="title">
      <el-input v-model="formData.title" placeholder="通知标题" clearable />
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
        class="w-full"
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
  </ProFormDrawer>
</template>

<script setup lang="ts">
import type { FormRules } from "element-plus";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import NoticeAPI, { type NoticeForm } from "@/api/system/notice-api";
import UserAPI from "@/api/system/user-api";

const emit = defineEmits<{
  success: [];
}>();

const noticeFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const formLoading = ref(false);
const userOptions = ref<OptionType[]>([]);

const dialogState = reactive({
  title: "新增公告",
  visible: false,
});

const formData = reactive<NoticeForm>({
  level: "L",
  targetType: 1,
});

const rules: FormRules = {
  title: [{ required: true, message: "请输入通知标题", trigger: "blur" }],
  content: [
    {
      required: true,
      message: "请输入通知内容",
      trigger: "blur",
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (!value.replace(/<[^>]+>/g, "").trim()) {
          callback(new Error("请输入通知内容"));
          return;
        }
        callback();
      },
    },
  ],
  type: [{ required: true, message: "请选择通知类型", trigger: "change" }],
};

function resetFormData() {
  Object.assign(formData, {
    id: undefined,
    title: undefined,
    content: undefined,
    type: undefined,
    level: "L",
    targetType: 1,
    targetUserIds: undefined,
  });
}

async function loadUserOptions() {
  userOptions.value = await UserAPI.getOptions();
}

async function openCreate() {
  resetFormData();
  dialogState.title = "新增公告";
  dialogState.visible = true;
  await loadUserOptions();
}

async function openEdit(id: string) {
  resetFormData();
  dialogState.title = "修改公告";
  dialogState.visible = true;
  await loadUserOptions();
  const data = await NoticeAPI.getFormData(id);
  Object.assign(formData, data);
}

function handleClose() {
  dialogState.visible = false;
  noticeFormRef.value?.resetFields();
  noticeFormRef.value?.clearValidate();
  resetFormData();
}

const handleSubmit = useDebounceFn(() => {
  noticeFormRef.value?.validate((valid: boolean) => {
    if (!valid) {
      formLoading.value = false;
      return;
    }

    const noticeId = formData.id;
    const request = noticeId ? NoticeAPI.update(noticeId, formData) : NoticeAPI.create(formData);
    request
      .then(() => {
        ElMessage.success(noticeId ? "修改成功" : "新增成功");
        handleClose();
        emit("success");
      })
      .finally(() => {
        formLoading.value = false;
      });
  });
}, 300);

function handleSubmitWrapper() {
  formLoading.value = true;
  handleSubmit();
}

defineExpose({
  openCreate,
  openEdit,
});
</script>
