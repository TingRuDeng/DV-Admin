<template>
  <ProFormDrawer
    ref="noticeFormRef"
    v-model="dialogState.visible"
    :title="t(dialogState.titleKey)"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    size="80%"
    label-width="100px"
    @close="handleClose"
    @submit="handleSubmitWrapper"
  >
    <el-form-item :label="t('system.noticeTitle')" prop="title">
      <el-input v-model="formData.title" :placeholder="t('system.noticeTitle')" clearable />
    </el-form-item>

    <el-form-item :label="t('system.noticeType')" prop="type">
      <Dict v-model="formData.type" code="notice_type" />
    </el-form-item>
    <el-form-item :label="t('system.noticeLevel')" prop="level">
      <Dict v-model="formData.level" code="notice_level" />
    </el-form-item>
    <el-form-item :label="t('system.target')" prop="targetType">
      <el-radio-group v-model="formData.targetType">
        <el-radio :value="1">{{ t("system.allUsers") }}</el-radio>
        <el-radio :value="2">{{ t("system.specifiedUsers") }}</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item
      v-if="formData.targetType == 2"
      :label="t('system.specifiedUser')"
      prop="targetUserIds"
    >
      <el-select
        v-model="formData.targetUserIds"
        multiple
        search
        :placeholder="t('system.specifiedUserPlaceholder')"
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
    <el-form-item :label="t('system.noticeContent')" prop="content">
      <WangEditor v-model="formData.content" />
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
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
  titleKey: "system.addNoticeTitle",
  visible: false,
});

const formData = reactive<NoticeForm>({
  level: "L",
  targetType: 1,
});

const rules: FormRules = {
  title: [{ required: true, message: () => t("system.noticeTitleRequired"), trigger: "blur" }],
  content: [
    {
      required: true,
      message: () => t("system.noticeContentRequired"),
      trigger: "blur",
      validator: (_rule: unknown, value: string | undefined, callback: (error?: Error) => void) => {
        if (!(value ?? "").replace(/<[^>]+>/g, "").trim()) {
          callback(new Error(t("system.noticeContentRequired")));
          return;
        }
        callback();
      },
    },
  ],
  type: [{ required: true, message: () => t("system.noticeTypeRequired"), trigger: "change" }],
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
  dialogState.titleKey = "system.addNoticeTitle";
  dialogState.visible = true;
  await loadUserOptions();
}

async function openEdit(id: string) {
  resetFormData();
  dialogState.titleKey = "system.editNotice";
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
        ElMessage.success(noticeId ? t("system.updateSuccess") : t("system.createSuccess"));
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
