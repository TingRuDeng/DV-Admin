<template>
  <ProFormDrawer
    ref="dictFormRef"
    v-model="dialogState.visible"
    :title="t(dialogState.titleKey)"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    size="500px"
    label-width="80px"
    @submit="handleSubmitWrapper"
    @close="handleClose"
  >
    <el-form-item :label="t('system.dictName')" prop="name">
      <el-input v-model="formData.name" :placeholder="t('system.dictNameInput')" />
    </el-form-item>

    <el-form-item :label="t('system.dictCode')" prop="dictCode">
      <el-input v-model="formData.dictCode" :placeholder="t('system.dictCodeInput')" />
    </el-form-item>

    <el-form-item :label="t('common.status')">
      <el-radio-group v-model="formData.status">
        <el-radio :value="1">{{ t("common.enabled") }}</el-radio>
        <el-radio :value="0">{{ t("common.disabled") }}</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item :label="t('system.roleRemark')">
      <el-input v-model="formData.remark" type="textarea" :placeholder="t('system.remarkInput')" />
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import type { FormRules } from "element-plus";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import DictAPI from "@/api/system/dict-api";

interface DictFormData {
  id?: string;
  name: string;
  dictCode: string;
  status: number;
  remark: string;
}

const emit = defineEmits<{
  success: [];
}>();

const dictFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const formLoading = ref(false);

const dialogState = reactive({
  titleKey: "system.addDict",
  visible: false,
});

const formData = reactive<DictFormData>(createDefaultFormData());

const rules: FormRules<DictFormData> = {
  name: [{ required: true, message: () => t("system.dictNameInput"), trigger: "blur" }],
  dictCode: [{ required: true, message: () => t("system.dictCodeInput"), trigger: "blur" }],
};

function createDefaultFormData(): DictFormData {
  return {
    id: undefined,
    name: "",
    dictCode: "",
    status: 1,
    remark: "",
  };
}

function resetFormData() {
  Object.assign(formData, createDefaultFormData());
}

async function openCreate() {
  resetFormData();
  dialogState.titleKey = "system.addDict";
  dialogState.visible = true;
}

async function openEdit(id: string) {
  resetFormData();
  dialogState.titleKey = "system.editDict";
  dialogState.visible = true;
  const data = await DictAPI.getFormData(id);
  Object.assign(formData, data);
}

const handleSubmit = useDebounceFn(() => {
  dictFormRef.value?.validate((isValid: boolean) => {
    if (!isValid) {
      formLoading.value = false;
      return;
    }

    const id = formData.id;
    const request = id ? DictAPI.update(id, formData) : DictAPI.create(formData);
    request
      .then(() => {
        ElMessage.success(id ? t("system.updateSuccess") : t("system.createSuccess"));
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

function handleClose() {
  dialogState.visible = false;
  dictFormRef.value?.resetFields();
  dictFormRef.value?.clearValidate();
  resetFormData();
}

defineExpose({
  openCreate,
  openEdit,
});
</script>
