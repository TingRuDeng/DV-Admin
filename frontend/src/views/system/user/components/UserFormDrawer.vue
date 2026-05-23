<template>
  <ProFormDrawer
    ref="userFormRef"
    v-model="dialogState.visible"
    :title="dialogState.title"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    :size="drawerSize"
    @submit="handleSubmitWrapper"
    @close="handleClose"
  >
    <el-form-item label="用户名" prop="username">
      <el-input v-model="formData.username" :readonly="!!formData.id" placeholder="请输入用户名" />
    </el-form-item>
    <el-form-item label="用户昵称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入用户昵称" />
    </el-form-item>
    <el-form-item label="所属部门" prop="deptId">
      <el-tree-select
        v-model="formData.deptId"
        placeholder="请选择所属部门"
        :data="deptOptions"
        node-key="id"
        filterable
        check-strictly
        :render-after-expand="false"
        class="w-full"
      />
    </el-form-item>
    <el-form-item label="角色" prop="roles">
      <el-select v-model="formData.roles" multiple placeholder="请选择" class="w-full">
        <el-option
          v-for="item in roleOptions"
          :key="item.id"
          :label="item.label"
          :value="item.id"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="手机号码" prop="mobile">
      <el-input v-model="formData.mobile" placeholder="请输入手机号码" maxlength="11" />
    </el-form-item>
    <el-form-item label="邮箱" prop="email">
      <el-input v-model="formData.email" placeholder="请输入邮箱" maxlength="50" />
    </el-form-item>
    <el-form-item label="状态" prop="isActive">
      <el-switch
        v-model="formData.isActive"
        inline-prompt
        active-text="正常"
        inactive-text="禁用"
        :active-value="1"
        :inactive-value="0"
      />
    </el-form-item>
  </ProFormDrawer>
</template>

<script setup lang="ts">
import type { FormRules } from "element-plus";
import ProFormDrawer from "@/components/ProFormDrawer/index.vue";
import { useAppStore } from "@/store/modules/app-store";
import { DeviceEnum } from "@/enums/settings/device-enum";
import UserAPI, { type UserForm } from "@/api/system/user-api";
import DeptAPI from "@/api/system/dept-api";
import RoleAPI from "@/api/system/role-api";

const emit = defineEmits<{
  success: [];
}>();

const appStore = useAppStore();
const userFormRef = ref<InstanceType<typeof ProFormDrawer> | null>(null);
const formLoading = ref(false);
const deptOptions = ref<OptionType[]>();
const roleOptions = ref<OptionType[]>();

const dialogState = reactive({
  visible: false,
  title: "新增用户",
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const formData = reactive<UserForm>({
  isActive: 1,
});

const rules: FormRules = {
  username: [{ required: true, message: "用户名不能为空", trigger: "blur" }],
  name: [{ required: true, message: "用户昵称不能为空", trigger: "blur" }],
  deptId: [{ required: true, message: "所属部门不能为空", trigger: "blur" }],
  roles: [{ required: true, message: "用户角色不能为空", trigger: "blur" }],
  email: [
    {
      pattern: /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/,
      message: "请输入正确的邮箱地址",
      trigger: "blur",
    },
  ],
  mobile: [
    {
      pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/,
      message: "请输入正确的手机号码",
      trigger: "blur",
    },
  ],
};

function resetFormData() {
  Object.assign(formData, {
    id: undefined,
    username: undefined,
    name: undefined,
    deptId: undefined,
    roles: undefined,
    mobile: undefined,
    email: undefined,
    isActive: 1,
  });
}

async function loadOptions() {
  const [roles, depts] = await Promise.all([RoleAPI.getOptions(), DeptAPI.getOptions()]);
  roleOptions.value = roles;
  deptOptions.value = depts;
}

async function openCreate() {
  resetFormData();
  dialogState.title = "新增用户";
  dialogState.visible = true;
  await loadOptions();
}

async function openEdit(id: string) {
  resetFormData();
  dialogState.title = "修改用户";
  dialogState.visible = true;
  await loadOptions();
  const data = await UserAPI.getFormData(id);
  Object.assign(formData, data);
}

function handleClose() {
  dialogState.visible = false;
  userFormRef.value?.resetFields();
  userFormRef.value?.clearValidate();
  resetFormData();
}

const handleSubmit = useDebounceFn(() => {
  userFormRef.value?.validate((valid: boolean) => {
    if (!valid) {
      formLoading.value = false;
      return;
    }

    const userId = formData.id;
    const request = userId ? UserAPI.update(userId, formData) : UserAPI.create(formData);
    request
      .then(() => {
        ElMessage.success(userId ? "修改用户成功" : "新增用户成功");
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
