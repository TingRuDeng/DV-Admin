<template>
  <div class="tags-toolbar">
    <button
      type="button"
      class="tags-toolbar__button"
      :aria-label="t('tagsView.refreshCurrent')"
      @click="emit('refresh')"
    >
      <AppIcon name="refresh" :size="15" />
    </button>
    <button
      type="button"
      class="tags-toolbar__button"
      :aria-label="t(appStore.contentMaximized ? 'tagsView.restore' : 'tagsView.maximize')"
      :aria-pressed="appStore.contentMaximized"
      @click="appStore.toggleContentMaximized()"
    >
      <AppIcon :name="appStore.contentMaximized ? 'minimize' : 'maximize'" :size="15" />
    </button>
  </div>
</template>

<script setup lang="ts">
import AppIcon from "@/components/AppIcon/index.vue";
import { useAppStore } from "@/store";

const emit = defineEmits<{ refresh: [] }>();
const { t } = useI18n();
const appStore = useAppStore();
</script>

<style lang="scss" scoped>
.tags-toolbar {
  display: flex;
  flex: none;
  gap: 2px;
  align-items: center;
  padding-left: 10px;
  margin-left: 6px;
  border-left: 1px solid var(--ff-shell-border);
}

.tags-toolbar__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  color: var(--ff-shell-text-muted);
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: var(--ff-radius-chip);
  transition:
    color var(--ff-duration-fast) ease,
    background-color var(--ff-duration-fast) ease;

  &:hover {
    color: var(--ff-shell-text);
    background: var(--ff-shell-hover);
  }

  &:focus-visible {
    outline: 2px solid var(--el-color-primary-light-5);
    outline-offset: 1px;
  }
}
</style>
