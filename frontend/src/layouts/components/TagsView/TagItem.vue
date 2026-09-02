<template>
  <el-tag
    cursor-pointer
    :closable="!tag.affix"
    :effect="isActive ? 'dark' : 'light'"
    :type="isActive ? 'primary' : 'info'"
    role="link"
    tabindex="0"
    :aria-current="isActive ? 'page' : undefined"
    @click.middle="emit('middle-click', tag)"
    @contextmenu.prevent="(event: MouseEvent) => emit('open-menu', tag, event)"
    @close="emit('close', tag)"
    @click="emit('navigate', tag)"
    @keydown.enter.space.prevent="emit('navigate', tag)"
  >
    {{ translateRouteTitle(tag.title) }}
  </el-tag>
</template>

<script setup lang="ts">
import { translateRouteTitle } from "@/utils/i18n";

defineProps<{
  tag: TagView;
  isActive: boolean;
}>();

const emit = defineEmits<{
  close: [tag: TagView];
  "middle-click": [tag: TagView];
  navigate: [tag: TagView];
  "open-menu": [tag: TagView, event: MouseEvent];
}>();
</script>

<style lang="scss" scoped>
:deep(.el-tag) {
  height: 30px;
  padding: 0 11px;
  margin: 0 3px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid var(--ff-shell-border);
  border-radius: 6px;
  transition:
    color var(--ff-duration-fast) ease,
    background-color var(--ff-duration-fast) ease,
    border-color var(--ff-duration-fast) ease,
    box-shadow var(--ff-duration-fast) ease;

  &.el-tag--info {
    color: var(--ff-shell-text-muted);
    background: var(--ff-shell-surface);

    &:hover {
      color: var(--el-color-primary);
      background: var(--ff-shell-hover);
      border-color: var(--el-color-primary-light-5);
    }
  }

  &.el-tag--primary {
    color: #ffffff;
    background: var(--el-color-primary);
    border-color: var(--el-color-primary);
    box-shadow: 0 6px 14px -9px var(--el-color-primary);

    &:hover {
      background: var(--el-color-primary-light-3);
      border-color: var(--el-color-primary-light-3);
    }
  }

  &:focus-visible {
    outline: 2px solid var(--el-color-primary-light-5);
    outline-offset: 1px;
  }

  .el-tag__close {
    margin-left: 6px;
    font-size: 12px;
    color: inherit;
    opacity: 0.6;

    &:hover {
      background: transparent;
      opacity: 1;
    }
  }
}
</style>
