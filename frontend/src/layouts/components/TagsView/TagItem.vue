<template>
  <el-tag
    h-26px
    cursor-pointer
    :closable="!tag.affix"
    :effect="isActive ? 'dark' : 'light'"
    :type="isActive ? 'primary' : 'info'"
    @click.middle="emit('middle-click', tag)"
    @contextmenu.prevent="(event: MouseEvent) => emit('open-menu', tag, event)"
    @close="emit('close', tag)"
    @click="emit('navigate', tag)"
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
  height: 28px;
  padding: 0 12px;
  margin: 0 4px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid transparent;
  border-radius: 8px;
  transition: all 0.2s ease;

  &.el-tag--info {
    color: #64748b;
    background: rgba(255, 255, 255, 0.8);
    border-color: rgba(0, 0, 0, 0.06);

    &:hover {
      color: #3b82f6;
      background: rgba(255, 255, 255, 1);
      border-color: rgba(59, 130, 246, 0.3);
    }
  }

  &.el-tag--primary {
    color: #3b82f6;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
    border-color: rgba(59, 130, 246, 0.3);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);

    &:hover {
      background: linear-gradient(
        135deg,
        rgba(59, 130, 246, 0.15) 0%,
        rgba(99, 102, 241, 0.15) 100%
      );
      border-color: rgba(59, 130, 246, 0.5);
    }
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

:global(html.dark) {
  :deep(.el-tag) {
    &.el-tag--info {
      color: #cbd5e1;
      background: rgba(30, 41, 59, 0.8);
      border-color: rgba(255, 255, 255, 0.08);

      &:hover {
        color: #60a5fa;
        background: rgba(30, 41, 59, 1);
        border-color: rgba(96, 165, 250, 0.3);
      }
    }

    &.el-tag--primary {
      color: #60a5fa;
      background: linear-gradient(
        135deg,
        rgba(96, 165, 250, 0.15) 0%,
        rgba(139, 92, 246, 0.15) 100%
      );
      border-color: rgba(96, 165, 250, 0.3);
      box-shadow: 0 2px 8px rgba(96, 165, 250, 0.2);

      &:hover {
        background: linear-gradient(
          135deg,
          rgba(96, 165, 250, 0.2) 0%,
          rgba(139, 92, 246, 0.2) 100%
        );
        border-color: rgba(96, 165, 250, 0.5);
      }
    }
  }
}
</style>
