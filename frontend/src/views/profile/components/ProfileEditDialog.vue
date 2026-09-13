<template>
  <ProDialog
    v-model="dialogVisible"
    :title="dialog.titleKey ? t(dialog.titleKey) : ''"
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
      <el-form-item :label="t('profile.nickname')">
        <el-input v-model="profileForm.name" />
      </el-form-item>
    </el-form>

    <el-form
      v-if="dialog.type === ProfileDialogType.PASSWORD"
      ref="passwordChangeFormRef"
      :model="passwordForm"
      :rules="passwordRules"
      :validate-on-rule-change="false"
      :label-width="100"
      class="ff-form"
    >
      <el-form-item :label="t('profile.oldPassword')" prop="oldPassword">
        <el-input v-model="passwordForm.oldPassword" type="password" show-password />
      </el-form-item>
      <el-form-item :label="t('profile.newPassword')" prop="newPassword">
        <el-input v-model="passwordForm.newPassword" type="password" show-password />
      </el-form-item>
      <el-form-item :label="t('profile.confirmPassword')" prop="confirmPassword">
        <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
      </el-form-item>
    </el-form>
  </ProDialog>
</template>

<script setup lang="ts">
import ProDialog from "@/components/ProDialog/index.vue";
import type { PasswordForm, PasswordPolicy, ProfileForm } from "@/api/information-api";
import { passwordLengthError } from "@/utils/password-policy";
import type { FormInstance } from "element-plus";
import { ProfileDialogType, type ProfileDialogState } from "../types";

const { t } = useI18n();

const props = defineProps<{
  dialog: ProfileDialogState;
  passwordForm: PasswordForm;
  passwordPolicy: PasswordPolicy | null;
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

const passwordRules = computed(() => ({
  oldPassword: [{ required: true, message: t("profile.oldPasswordRequired"), trigger: "blur" }],
  newPassword: [
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        const error = passwordLengthError(value ?? "", props.passwordPolicy, {
          policyUnavailable: t("profile.passwordPolicyUnavailable"),
          invalidLength: (min, max) => t("profile.passwordLength", { min, max }),
        });
        callback(error ? new Error(error) : undefined);
      },
      trigger: "blur",
    },
  ],
  confirmPassword: [
    { required: true, message: t("profile.confirmPasswordRequired"), trigger: "blur" },
  ],
}));

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
