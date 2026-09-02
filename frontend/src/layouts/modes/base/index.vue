<template>
  <div class="layout" :class="layoutClass">
    <!-- 移动端遮罩层 - 当侧边栏打开时显示 -->
    <button
      v-if="isMobile && isSidebarOpen"
      type="button"
      class="layout__overlay"
      aria-label="关闭导航"
      @click="closeSidebar"
    />

    <!-- 布局内容插槽 - 各种布局模式的具体内容 -->
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useLayout, useDeviceDetection } from "@/composables";

/// Layout-related functionality and state management
const { layoutClass, isSidebarOpen, closeSidebar } = useLayout();

/// Device detection for responsive layout
const { isMobile } = useDeviceDetection();
const route = useRoute();

watch(
  () => route.fullPath,
  () => {
    if (isMobile.value && isSidebarOpen.value) {
      closeSidebar();
    }
  }
);
</script>

<style lang="scss" scoped>
.layout {
  width: 100%;
  min-height: 100%;
  background: var(--ff-shell-bg);

  &__overlay {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 999;
    width: 100%;
    height: 100%;
    padding: 0;
    cursor: pointer;
    background: var(--ff-shell-overlay);
    border: 0;
    -webkit-backdrop-filter: blur(2px);
    backdrop-filter: blur(2px);
  }
}
</style>
