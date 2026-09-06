<template>
  <button
    type="button"
    class="hamburger-wrapper"
    :aria-label="label || (isActive ? '收起导航' : '展开导航')"
    :aria-expanded="isActive"
    :aria-controls="controls"
    @click="toggleClick"
  >
    <div :class="['i-svg:collapse', { hamburger: true, 'is-active': isActive }, hamburgerClass]" />
  </button>
</template>

<script setup lang="ts">
import { useSettingsStore } from "@/store";
import { ThemeMode, SidebarColor } from "@/enums/settings/theme-enum";
import { LayoutMode } from "@/enums/settings/layout-enum";

defineProps({
  isActive: { type: Boolean, required: true },
  controls: { type: String, default: undefined },
  label: { type: String, default: undefined },
});

const emit = defineEmits<{
  toggleClick: [];
}>();

const settingsStore = useSettingsStore();
const layout = computed(() => settingsStore.layout);

const hamburgerClass = computed(() => {
  // 如果暗黑主题
  if (settingsStore.theme === ThemeMode.DARK) {
    return "hamburger--white";
  }

  // 如果是混合布局 && 侧边栏配色方案是经典蓝
  if (
    layout.value === LayoutMode.MIX &&
    settingsStore.sidebarColorScheme === SidebarColor.CLASSIC_BLUE
  ) {
    return "hamburger--white";
  }

  // 默认返回空字符串
  return "";
});

function toggleClick() {
  emit("toggleClick");
}
</script>

<style scoped lang="scss">
.hamburger-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  color: var(--ff-shell-text-muted);
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: var(--ff-radius-nav);
  transition:
    color var(--ff-duration-fast) ease,
    background-color var(--ff-duration-fast) ease;

  &:hover,
  &:focus-visible {
    color: var(--el-color-primary);
    background: var(--ff-shell-hover);
  }

  &:focus-visible {
    outline: 2px solid var(--el-color-primary-light-5);
    outline-offset: -2px;
  }

  .hamburger {
    font-size: 18px;
    vertical-align: middle;
    transform: scaleX(-1);
    transition: transform var(--ff-duration-base) var(--ff-ease-standard);

    &--white {
      color: #fff;
    }

    &.is-active {
      transform: scaleX(1);
    }
  }
}
</style>
