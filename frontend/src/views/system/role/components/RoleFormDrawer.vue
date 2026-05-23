<template>
  <ProFormDrawer
    ref="roleFormRef"
    v-model="dialogState.visible"
    :title="dialogState.title"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    :size="drawerSize"
    label-width="100px"
    @submit="handleSubmitWrapper"
    @close="handleClose"
  >
    <el-form-item label="角色名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入角色名称" />
    </el-form-item>
    <el-form-item label="状态" prop="status">
      <el-radio-group v-model="formData.status">
        <el-radio :value="1">正常</el-radio>
        <el-radio :value="0">停用</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="是否默认" prop="isDefault">
      <el-radio-group v-model="formData.isDefault">
        <el-radio :value="1">是</el-radio>
        <el-radio :value="0">否</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="排序" prop="sort">
      <el-input-number
        v-model="formData.sort"
        controls-position="right"
        :min="0"
        style="width: 100px"
      />
    </el-form-item>
    <el-form-item label="备注" prop="desc">
      <el-input v-model="formData.desc" placeholder="请输入角色备注" type="textarea" :rows="2" />
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import type { FormRules } from "element-plus";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import { DeviceEnum } from "@/enums/settings/device-enum";
import RoleAPI, { type RoleForm } from "@/api/system/role-api";
import { useAppStore } from "@/store/modules/app-store";

const emit = defineEmits<{
  success: [];
}>();

const appStore = useAppStore();
const roleFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const formLoading = ref(false);

const dialogState = reactive({
  title: "新增角色",
  visible: false,
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const formData = reactive<RoleForm>({
  sort: 1,
  status: 1,
  isDefault: 1,
});

const rules: FormRules = {
  name: [{ required: true, message: "请输入角色名称", trigger: "blur" }],
  status: [{ required: true, message: "请选择状态", trigger: "blur" }],
};

function resetFormData() {
  Object.assign(formData, {
    id: undefined,
    name: undefined,
    sort: 1,
    status: 1,
    isDefault: 1,
    desc: undefined,
  });
}

async function openCreate() {
  resetFormData();
  dialogState.title = "新增角色";
  dialogState.visible = true;
}

async function openEdit(roleId: string) {
  resetFormData();
  dialogState.title = "修改角色";
  dialogState.visible = true;
  const data = await RoleAPI.getFormData(roleId);
  Object.assign(formData, data);
}

function handleClose() {
  dialogState.visible = false;
  roleFormRef.value?.resetFields();
  roleFormRef.value?.clearValidate();
  resetFormData();
}

const handleSubmit = useDebounceFn(() => {
  roleFormRef.value?.validate((valid: boolean) => {
    if (!valid) {
      formLoading.value = false;
      return;
    }

    const roleId = formData.id;
    const request = roleId ? RoleAPI.update(roleId, formData) : RoleAPI.create(formData);
    request
      .then(() => {
        ElMessage.success(roleId ? "修改成功" : "新增成功");
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
