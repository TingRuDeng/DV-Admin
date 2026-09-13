<template>
  <ProFormDrawer
    ref="userFormRef"
    v-model="dialogState.visible"
    :title="t(dialogState.titleKey)"
    :model="formData"
    :rules="rules"
    :loading="formLoading"
    :size="drawerSize"
    @submit="handleSubmitWrapper"
    @close="handleClose"
  >
    <el-form-item :label="t('userForm.username')" prop="username">
      <el-input
        v-model="formData.username"
        :readonly="!!formData.id"
        :placeholder="t('userForm.usernamePlaceholder')"
      />
    </el-form-item>
    <el-form-item :label="t('userForm.name')" prop="name">
      <el-input v-model="formData.name" :placeholder="t('userForm.namePlaceholder')" />
    </el-form-item>
    <el-form-item :label="t('userForm.department')" prop="deptId">
      <el-tree-select
        v-model="formData.deptId"
        :placeholder="t('userForm.departmentPlaceholder')"
        :data="deptOptions"
        node-key="id"
        filterable
        check-strictly
        :render-after-expand="false"
        class="w-full"
      />
    </el-form-item>
    <el-form-item :label="t('userForm.roles')" prop="roles">
      <el-select
        v-model="formData.roles"
        multiple
        :placeholder="t('userForm.selectPlaceholder')"
        class="w-full"
      >
        <el-option
          v-for="item in roleOptions"
          :key="item.id"
          :label="item.label"
          :value="item.id"
        />
      </el-select>
    </el-form-item>
    <el-form-item :label="t('userForm.mobile')" prop="mobile">
      <el-input
        v-model="formData.mobile"
        :placeholder="t('userForm.mobilePlaceholder')"
        maxlength="11"
      />
    </el-form-item>
    <el-form-item :label="t('userForm.email')" prop="email">
      <el-input
        v-model="formData.email"
        :placeholder="t('userForm.emailPlaceholder')"
        maxlength="50"
      />
    </el-form-item>
    <el-form-item :label="t('userForm.status')" prop="isActive">
      <el-switch
        v-model="formData.isActive"
        inline-prompt
        :active-text="t('user.active')"
        :inactive-text="t('user.inactive')"
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
import { useI18n } from "vue-i18n";

const { t } = useI18n();

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
  titleKey: "user.create",
});

const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const formData = reactive<UserForm>({
  isActive: 1,
});

const rules = computed<FormRules>(() => ({
  username: [{ required: true, message: t("userForm.usernameRequired"), trigger: "blur" }],
  name: [{ required: true, message: t("userForm.nameRequired"), trigger: "blur" }],
  deptId: [{ required: true, message: t("userForm.departmentRequired"), trigger: "blur" }],
  roles: [{ required: true, message: t("userForm.rolesRequired"), trigger: "blur" }],
  email: [
    {
      pattern: /\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}/,
      message: t("userForm.emailInvalid"),
      trigger: "blur",
    },
  ],
  mobile: [
    {
      pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/,
      message: t("userForm.mobileInvalid"),
      trigger: "blur",
    },
  ],
}));

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
  dialogState.titleKey = "user.create";
  dialogState.visible = true;
  await loadOptions();
}

async function openEdit(id: string) {
  resetFormData();
  dialogState.titleKey = "userForm.editTitle";
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
        ElMessage.success(userId ? t("userForm.editSuccess") : t("userForm.createSuccess"));
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
