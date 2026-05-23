<template>
  <ProDialog
    v-model="dialogVisible"
    :title="dialog.title"
    :width="500"
    @submit="emit('submit')"
    @cancel="emit('cancel')"
    @close="emit('cancel')"
  >
    <el-form
      v-if="dialog.type === ProfileDialogType.ACCOUNT"
      ref="userProfileFormRef"
      :model="profileForm"
      :label-width="100"
      class="ff-form"
    >
      <el-form-item label="昵称">
        <el-input v-model="profileForm.name" />
      </el-form-item>
    </el-form>

    <el-form
      v-if="dialog.type === ProfileDialogType.PASSWORD"
      ref="passwordChangeFormRef"
      :model="passwordForm"
      :rules="passwordRules"
      :label-width="100"
      class="ff-form"
    >
      <el-form-item label="原密码" prop="currentPassword">
        <el-input v-model="passwordForm.currentPassword" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="passwordForm.newPassword" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
      </el-form-item>
    </el-form>
  </ProDialog>
</template>

<script setup lang="ts">
import ProDialog from "@/components/ProDialog/index.vue";
import type { PasswordForm, ProfileForm } from "@/api/information-api";
import type { FormInstance } from "element-plus";
import { ProfileDialogType, type ProfileDialogState } from "../types";

const props = defineProps<{
  dialog: ProfileDialogState;
  passwordForm: PasswordForm;
  profileForm: ProfileForm;
}>();

const emit = defineEmits<{
  cancel: [];
  "update:visible": [visible: boolean];
  submit: [];
}>();

const dialogVisible = computed({
  get: () => props.dialog.visible,
  set: (visible) => emit("update:visible", visible),
});

const userProfileFormRef = ref<FormInstance>();
const passwordChangeFormRef = ref<FormInstance>();

const passwordRules = {
  currentPassword: [{ required: true, message: "请输入原密码", trigger: "blur" }],
  newPassword: [{ required: true, message: "请输入新密码", trigger: "blur" }],
  confirmPassword: [{ required: true, message: "请再次输入新密码", trigger: "blur" }],
};

function resetProfileForm() {
  userProfileFormRef.value?.resetFields();
}

function resetPasswordForm() {
  passwordChangeFormRef.value?.resetFields();
}

function validatePasswordForm() {
  return passwordChangeFormRef.value?.validate().catch(() => false);
}

defineExpose({
  resetPasswordForm,
  resetProfileForm,
  validatePasswordForm,
});
</script>
