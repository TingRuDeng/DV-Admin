<template>
  <ProFormDrawer
    ref="dictFormRef"
    v-model="dialogState.visible"
    :title="dialogState.title"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    size="500px"
    label-width="80px"
    @submit="handleSubmitWrapper"
    @close="handleClose"
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
</template>

<script setup lang="ts">
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
  title: "新增字典",
  visible: false,
});

const formData = reactive<DictFormData>(createDefaultFormData());

const rules: FormRules<DictFormData> = {
  name: [{ required: true, message: "请输入字典名称", trigger: "blur" }],
  dictCode: [{ required: true, message: "请输入字典编码", trigger: "blur" }],
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
  dialogState.title = "新增字典";
  dialogState.visible = true;
}

async function openEdit(id: string) {
  resetFormData();
  dialogState.title = "修改字典";
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
        ElMessage.success(id ? "修改成功" : "新增成功");
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
