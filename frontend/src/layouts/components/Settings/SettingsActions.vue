<template>
  <div class="action-buttons">
    <el-button class="action-buttons__button" :loading="copyLoading" @click="emit('copy')">
      <AppIcon name="copy" :size="16" />
      {{ t("settings.copyConfig") }}
    </el-button>
    <el-button class="action-buttons__button" :loading="resetLoading" @click="emit('reset')">
      <AppIcon name="refresh" :size="16" />
      {{ t("settings.resetConfig") }}
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
// 两个操作同级，用同一种次级样式，只靠图标区分；悬停只变底色，不做位移
.action-buttons {
  display: flex;
  gap: 10px;
}

.action-buttons__button.el-button {
  flex: 1;
  height: 40px;
  margin: 0;
  font-size: 14px;
  color: var(--ff-color-text-primary);
  background: var(--ff-field-bg);
  border: 0;
  border-radius: var(--ff-radius-control);
  box-shadow: inset 0 0 0 1px var(--ff-line-strong);
  transition:
    background-color var(--ff-duration-fast) ease,
    box-shadow var(--ff-duration-fast) ease;

  :deep(.app-icon) {
    margin-right: 6px;
  }

  &:hover,
  &:focus-visible {
    color: var(--ff-color-text-primary);
    background: var(--ff-hover);
    box-shadow: inset 0 0 0 1px var(--ff-iri-b);
  }
}
</style>
