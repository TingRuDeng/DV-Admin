<template>
  <DataPanel title="安全设置">
    <div class="ff-profile-security-item">
      <div class="ff-profile-security-item__copy">
        <div class="ff-profile-security-item__title">账户密码</div>
        <div class="ff-profile-security-item__desc">定期修改密码有助于保护账户安全</div>
      </div>
      <el-button type="primary" link @click="emit('change-password')">修改</el-button>
    </div>
  </DataPanel>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  "change-password": [];
}>();
</script>
