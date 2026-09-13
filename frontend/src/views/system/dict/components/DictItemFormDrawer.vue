<template>
  <ProFormDrawer
    ref="dictItemFormRef"
    v-model="dialogState.visible"
    :title="t(dialogState.titleKey)"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    size="600px"
    label-width="100px"
    @close="handleClose"
    @submit="handleSubmitWrapper"
  >
    <el-form-item :label="t('system.dictOwner')" prop="dict">
      <el-select
        v-model="formData.dict"
        :placeholder="t('system.dictRequired')"
        filterable
        class="w-full"
      >
        <el-option v-for="item in dictList" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
    </el-form-item>
    <el-form-item :label="t('system.dictItemLabel')" prop="label">
      <el-input v-model="formData.label" :placeholder="t('system.dictLabelInput')" />
    </el-form-item>
    <el-form-item :label="t('system.dictItemValue')" prop="value">
      <el-input v-model="formData.value" :placeholder="t('system.dictValueInput')" />
    </el-form-item>
    <el-form-item :label="t('common.status')">
      <el-radio-group v-model="formData.status">
        <el-radio :value="1">{{ t("common.enabled") }}</el-radio>
        <el-radio :value="0">{{ t("common.disabled") }}</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item :label="t('system.labelType')">
      <el-tag v-if="formData.tagType" :type="formData.tagType" class="mr-2">
        {{ formData.label }}
      </el-tag>
      <el-radio-group v-model="formData.tagType">
        <el-radio value="success" border size="small">success</el-radio>
        <el-radio value="warning" border size="small">warning</el-radio>
        <el-radio value="info" border size="small">info</el-radio>
        <el-radio value="primary" border size="small">primary</el-radio>
        <el-radio value="danger" border size="small">danger</el-radio>
        <el-radio value="" border size="small">{{ t("system.clearForm") }}</el-radio>
      </el-radio-group>
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
import type { FormRules } from "element-plus";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import type { DictPageVO } from "@/api/system/dict-api";
import DictItemAPI, { type DictItemForm } from "@/api/system/dict-items-api";

defineProps<{
  dictList: DictPageVO[];
}>();

const emit = defineEmits<{
  success: [];
}>();

const dictItemFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const formLoading = ref(false);
const formData = reactive<DictItemForm>(createDefaultFormData());

const dialogState = reactive({
  titleKey: "system.addDictItem",
  visible: false,
});

const rules: FormRules<DictItemForm> = {
  dict: [{ required: true, message: () => t("system.dictRequired"), trigger: "change" }],
  value: [{ required: true, message: () => t("system.dictValueInput"), trigger: "blur" }],
  label: [{ required: true, message: () => t("system.dictLabelInput"), trigger: "blur" }],
};

function createDefaultFormData(): DictItemForm {
  return {
    id: undefined,
    status: 1,
    tagType: "",
  };
}

function resetFormData() {
  Object.assign(formData, createDefaultFormData());
}

async function openCreate(dict?: number | string) {
  resetFormData();
  formData.dict = dict === undefined ? undefined : String(dict);
  dialogState.titleKey = "system.addDictItem";
  dialogState.visible = true;
}

async function openEdit(id: number) {
  resetFormData();
  dialogState.titleKey = "system.editDictItem";
  dialogState.visible = true;
  const data = await DictItemAPI.getDictItemFormData(id);
  Object.assign(formData, data);
}

const handleSubmit = useDebounceFn(() => {
  dictItemFormRef.value?.validate((isValid: boolean) => {
    if (!isValid) {
      formLoading.value = false;
      return;
    }

    submitDictItem();
  });
}, 300);

function submitDictItem() {
  const id = formData.id;
  const request = id
    ? DictItemAPI.updateDictItem(id, formData)
    : DictItemAPI.createDictItem(formData);
  request
    .then(() => {
      ElMessage.success(id ? t("system.updateSuccess") : t("system.createSuccess"));
      handleClose();
      emit("success");
    })
    .finally(() => {
      formLoading.value = false;
    });
}

function handleSubmitWrapper() {
  formLoading.value = true;
  handleSubmit();
}

function handleClose() {
  dictItemFormRef.value?.resetFields();
  dictItemFormRef.value?.clearValidate();
  resetFormData();
  dialogState.visible = false;
}

defineExpose({
  openCreate,
  openEdit,
});
</script>
