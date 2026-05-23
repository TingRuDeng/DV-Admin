<template>
  <section class="ff-side-panel ff-profile-page__sidebar">
    <div class="ff-profile-user">
      <div class="ff-profile-user__avatar">
        <el-avatar :src="avatar" :size="100" />
        <el-button
          type="info"
          class="ff-profile-user__avatar-button"
          circle
          :icon="Camera"
          size="small"
          @click="emit('upload-avatar')"
        />
        <input
          ref="fileInput"
          type="file"
          style="display: none"
          accept="image/*"
          @change="emit('file-change', $event)"
        />
      </div>
      <div class="ff-profile-user__name">
        <span class="ff-profile-user__display-name">{{ profile.name }}</span>
        <el-icon class="ff-profile-user__edit" @click="emit('edit-account')">
          <Edit />
        </el-icon>
      </div>
      <div class="ff-profile-user__role">{{ profile.roleNames }}</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Camera } from "@element-plus/icons-vue";
import type { UserProfile } from "@/api/information-api";

defineProps<{
  avatar?: string;
  profile: UserProfile;
}>();

const emit = defineEmits<{
  "edit-account": [];
  "file-change": [event: Event];
  "upload-avatar": [];
}>();

const fileInput = ref<HTMLInputElement | null>(null);

function triggerFileUpload() {
  fileInput.value?.click();
}

defineExpose({
  triggerFileUpload,
});
</script>
