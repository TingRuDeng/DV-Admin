<template>
  <DataPanel :title="t('profile.accountInfo')">
    <el-descriptions :column="1" border>
      <el-descriptions-item :label="t('profile.username')">
        {{ profile.username }}
        <AppIcon
          v-if="profile.gender === 1 || profile.gender === 2"
          :name="profile.gender === 1 ? 'mars' : 'venus'"
          :size="16"
          class="ff-profile-gender"
          :class="profile.gender === 1 ? 'male' : 'female'"
        />
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.mobile')">
        {{ profile.mobile || t("profile.unbound") }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.email')">
        {{ profile.email || t("profile.unbound") }}
      </el-descriptions-item>
      <el-descriptions-item :label="t('profile.department')">
        {{ profile.deptName }}
      </el-descriptions-item>
    </el-descriptions>
  </DataPanel>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import type { UserProfile } from "@/api/information-api";

const { t } = useI18n();

defineProps<{
  profile: UserProfile;
}>();
</script>
