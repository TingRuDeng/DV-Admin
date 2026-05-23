<template>
  <DataPanel title="账号信息">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="用户名">
        {{ profile.username }}
        <el-icon v-if="profile.gender === 1" class="ff-profile-gender male">
          <Male />
        </el-icon>
        <el-icon v-else class="ff-profile-gender female">
          <Female />
        </el-icon>
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
import type { UserProfile } from "@/api/information-api";

defineProps<{
  profile: UserProfile;
}>();
</script>
