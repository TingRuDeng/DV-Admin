<template>
  <DataPanel title="账号信息">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="用户名">
        {{ profile.username }}
        <AppIcon
          :name="profile.gender === 1 ? 'mars' : 'venus'"
          :size="16"
          class="ff-profile-gender"
          :class="profile.gender === 1 ? 'male' : 'female'"
        />
      </el-descriptions-item>
      <el-descriptions-item label="手机号码">
        {{ profile.mobile || "未绑定" }}
      </el-descriptions-item>
      <el-descriptions-item label="邮箱">
        {{ profile.email || "未绑定" }}
      </el-descriptions-item>
      <el-descriptions-item label="部门">
        {{ profile.deptName }}
      </el-descriptions-item>
    </el-descriptions>
  </DataPanel>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import type { UserProfile } from "@/api/information-api";

defineProps<{
  profile: UserProfile;
}>();
</script>
