<template>
  <div class="action-buttons">
    <el-button type="primary" size="default" :loading="copyLoading" @click="emit('copy')">
      <AppIcon name="document" :size="16" />
      {{ copyLoading ? t("settings.copyLoading") : t("settings.copyConfig") }}
    </el-button>
    <el-button type="warning" size="default" :loading="resetLoading" @click="emit('reset')">
      <AppIcon name="refresh" :size="16" />
      {{ resetLoading ? t("settings.resetLoading") : t("settings.resetConfig") }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";

defineProps<{
  copyLoading: boolean;
  resetLoading: boolean;
}>();

const emit = defineEmits<{
  copy: [];
  reset: [];
}>();

const { t } = useI18n();
</script>

<style lang="scss" scoped>
.action-buttons {
  display: flex;

  & > .el-button {
    flex: 1;
    font-size: 14px;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      transform: translateY(-2px);
    }
  }
}
</style>
