<template>
  <DataPanel :title="t('profile.securitySettings')">
    <div class="ff-profile-security-item">
      <div class="ff-profile-security-item__copy">
        <div class="ff-profile-security-item__title">{{ t("profile.password") }}</div>
      </div>
      <el-button type="primary" link @click="emit('change-password')">
        {{ t("profile.edit") }}
      </el-button>
    </div>
  </DataPanel>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  "change-password": [];
}>();

const { t } = useI18n();
</script>
