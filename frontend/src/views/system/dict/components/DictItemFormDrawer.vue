<template>
  <ProFormDrawer
    ref="dictItemFormRef"
    v-model="dialogState.visible"
    :title="dialogState.title"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    size="600px"
    label-width="100px"
    @close="handleClose"
    @submit="handleSubmitWrapper"
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
</template>

<script setup lang="ts">
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
  title: "新增字典项",
  visible: false,
});

const rules: FormRules<DictItemForm> = {
  dict: [{ required: true, message: "请选择归属字典", trigger: "change" }],
  value: [{ required: true, message: "请输入字典值", trigger: "blur" }],
  label: [{ required: true, message: "请输入字典标签", trigger: "blur" }],
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
  dialogState.title = "新增字典项";
  dialogState.visible = true;
}

async function openEdit(id: number) {
  resetFormData();
  dialogState.title = "编辑字典项";
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
      ElMessage.success(id ? "修改成功" : "新增成功");
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
