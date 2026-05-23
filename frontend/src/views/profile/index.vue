<template>
  <PageShell class="ff-profile-page">
    <div class="ff-profile-page__grid">
      <ProfileSidebar
        ref="profileSidebarRef"
        :avatar="userStore.userInfo.avatar"
        :profile="userProfile"
        @edit-account="handleOpenDialog(ProfileDialogType.ACCOUNT)"
        @file-change="handleFileChange"
        @upload-avatar="triggerFileUpload"
      />

      <div class="ff-profile-page__main">
        <ProfileInfoPanel :profile="userProfile" />
        <ProfileSecurityPanel @change-password="handleOpenDialog(ProfileDialogType.PASSWORD)" />
      </div>
    </div>

    <ProfileEditDialog
      ref="profileEditDialogRef"
      :dialog="dialog"
      :password-form="passwordChangeForm"
      :profile-form="userProfileForm"
      @update:visible="dialog.visible = $event"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </PageShell>
</template>

<script lang="ts" setup>
import FileAPI from "@/api/file-api";
import InformationAPI, { UserProfile, ProfileForm, PasswordForm } from "@/api/information-api";
import { useUserStoreHook } from "@/store";
import { createLogger } from "@/utils/logger";
import ProfileEditDialog from "./components/ProfileEditDialog.vue";
import ProfileInfoPanel from "./components/ProfileInfoPanel.vue";
import ProfileSecurityPanel from "./components/ProfileSecurityPanel.vue";
import ProfileSidebar from "./components/ProfileSidebar.vue";
import { ProfileDialogType, type ProfileDialogState } from "./types";

const profileLogger = createLogger("Profile");
const userStore = useUserStoreHook();

const userProfile = ref<UserProfile>({});

const dialog = reactive<ProfileDialogState>({
  visible: false,
  title: "",
  type: "",
});

const userProfileForm = reactive<ProfileForm>({});
const passwordChangeForm = reactive<PasswordForm>({});

const profileSidebarRef = ref<InstanceType<typeof ProfileSidebar> | null>(null);
const profileEditDialogRef = ref<InstanceType<typeof ProfileEditDialog> | null>(null);

/**
 * 打开弹窗
 * @param type 弹窗类型 ACCOUNT: 账号资料 PASSWORD: 修改密码
 */
const handleOpenDialog = (type: ProfileDialogType) => {
  dialog.type = type;
  dialog.visible = true;
  switch (type) {
    case ProfileDialogType.ACCOUNT:
      dialog.title = "账号资料";
      userProfileForm.id = userProfile.value.id;
      userProfileForm.name = userProfile.value.name;
      userProfileForm.gender = userProfile.value.gender;
      break;
    case ProfileDialogType.PASSWORD:
      dialog.title = "修改密码";
      break;
  }
};

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (dialog.type === ProfileDialogType.ACCOUNT) {
    await InformationAPI.updateProfile(userProfileForm);
    ElMessage.success("账号资料修改成功");
    handleCancel();
    await loadUserProfile();
  } else if (dialog.type === ProfileDialogType.PASSWORD) {
    const isValid = await profileEditDialogRef.value?.validatePasswordForm();
    if (!isValid) {
      return;
    }
    if (passwordChangeForm.newPassword !== passwordChangeForm.confirmPassword) {
      ElMessage.error("两次输入的密码不一致");
      return;
    }
    await InformationAPI.changePassword(passwordChangeForm);
    ElMessage.success("密码修改成功");
    handleCancel();
  }
};

/**
 * 取消
 */
const handleCancel = () => {
  dialog.visible = false;
  if (dialog.type === ProfileDialogType.ACCOUNT) {
    profileEditDialogRef.value?.resetProfileForm();
  } else if (dialog.type === ProfileDialogType.PASSWORD) {
    profileEditDialogRef.value?.resetPasswordForm();
  }
};

const triggerFileUpload = () => {
  profileSidebarRef.value?.triggerFileUpload();
};

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files ? target.files[0] : null;
  if (file) {
    // 调用文件上传API
    try {
      const data = await FileAPI.uploadFile(file);
      // 更新用户信息
      await InformationAPI.updateProfile({
        avatar: data.url,
      });
      // 更新用户头像
      userStore.userInfo.avatar = data.url;
    } catch (error) {
      profileLogger.error("头像上传失败:", error);
      ElMessage.error("头像上传失败");
    }
  }
};

/** 加载用户信息 */
const loadUserProfile = async () => {
  userProfile.value = await InformationAPI.getProfile();
};

onMounted(async () => {
  await loadUserProfile();
});
</script>
