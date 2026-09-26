<template>
  <el-tag
    class="tags-view-item"
    :class="{ 'is-affix': tag.affix }"
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
    <AppIcon v-if="iconName" :name="iconName" :size="12" class="tags-view-item__icon" />
    {{ translateRouteTitle(tag.title) }}
  </el-tag>
</template>

<script setup lang="ts">
import { translateRouteTitle } from "@/utils/i18n";
import AppIcon from "@/components/AppIcon/index.vue";
import { hasAppIcon, normalizeMenuIconName } from "@/components/AppIcon/icon-map";

const props = defineProps<{
  tag: TagView;
  isActive: boolean;
}>();

// 只显示有专属映射的图标，没有映射时不显示问号
const iconName = computed(() => {
  if (!props.tag.icon) return "";
  const name = normalizeMenuIconName(props.tag.icon);
  return hasAppIcon(name) ? name : "";
});

const emit = defineEmits<{
  close: [tag: TagView];
  "middle-click": [tag: TagView];
  navigate: [tag: TagView];
  "open-menu": [tag: TagView, event: MouseEvent];
}>();
</script>

<style lang="scss" scoped>
.tags-view-item {
  height: 30px;
  padding: 0 12px;
  margin: 0 2px;
  font-size: 12px;
  font-weight: 500;
  // 页签可拖动排序，拖动时不应选中文字
  user-select: none;
  border: 1px solid var(--ff-shell-border);
  border-radius: var(--ff-radius-chip);
  transition:
    color var(--ff-duration-fast) ease,
    background-color var(--ff-duration-fast) ease,
    border-color var(--ff-duration-fast) ease,
    box-shadow var(--ff-duration-fast) ease;

  &.el-tag--info {
    color: var(--ff-shell-text-muted);
    background: var(--ff-shell-surface-muted);

    &:hover {
      color: var(--ff-shell-text);
      background: var(--ff-shell-hover);
      border-color: var(--ff-line-strong);
    }
  }

  // 当前页：面板底色 + 虹彩描边（padding-box / border-box 双层背景），边框保持 solid 以便键盘与测试识别
  &.el-tag--primary {
    font-weight: 600;
    color: var(--ff-shell-text);
    background:
      linear-gradient(var(--ff-color-bg-panel-strong), var(--ff-color-bg-panel-strong)) padding-box,
      var(--ff-iri) border-box;
    border-color: transparent;
    box-shadow: 0 6px 16px -10px color-mix(in srgb, var(--ff-iri-b) 70%, transparent);
  }

  &:focus-visible {
    outline: 2px solid var(--el-color-primary-light-5);
    outline-offset: 1px;
  }

  &.is-drag-ghost {
    opacity: 0.4;
  }

  :deep(.el-tag__content) {
    display: inline-flex;
    gap: 6px;
    align-items: center;
  }

  .tags-view-item__icon {
    flex: none;
    opacity: 0.8;
  }

  :deep(.el-tag__close) {
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
