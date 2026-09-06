<template>
  <div ref="layoutRef" class="layout" :class="layoutClass">
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
import { nextTick, ref, watch } from "vue";
import { useEventListener, useScrollLock } from "@vueuse/core";
import { useRoute } from "vue-router";
import { useLayout, useDeviceDetection } from "@/composables";

/// Layout-related functionality and state management
const { layoutClass, isSidebarOpen, closeSidebar } = useLayout();

/// Device detection for responsive layout
const { isMobile } = useDeviceDetection();
const route = useRoute();
const layoutRef = ref<HTMLElement | null>(null);
const bodyScrollLock = useScrollLock(typeof document === "undefined" ? null : document.body);
const restoreFocusTarget = ref<HTMLElement | null>(null);
const mobileSidebarWasOpen = ref(false);

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled]):not([type='hidden'])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[contenteditable='true']",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

function getMobileSidebar() {
  return layoutRef.value?.querySelector<HTMLElement>("#layout-sidebar") ?? null;
}

function getFocusableElements(sidebar: HTMLElement) {
  return Array.from(sidebar.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
    (element) => element.getAttribute("aria-hidden") !== "true" && !element.hasAttribute("inert")
  );
}

function focusMobileSidebar() {
  nextTick(() => {
    if (!isMobile.value || !isSidebarOpen.value) return;

    const sidebar = getMobileSidebar();
    if (!sidebar) return;

    const firstFocusable = getFocusableElements(sidebar)[0];
    (firstFocusable ?? sidebar).focus({ preventScroll: true });
  });
}

function restoreFocus() {
  const target = restoreFocusTarget.value;
  restoreFocusTarget.value = null;
  if (target?.isConnected) {
    target.focus({ preventScroll: true });
  }
}

watch(
  [isMobile, isSidebarOpen],
  ([mobile, open]) => {
    const shouldManageMobileSidebar = mobile && open;
    bodyScrollLock.value = shouldManageMobileSidebar;

    if (shouldManageMobileSidebar && !mobileSidebarWasOpen.value) {
      restoreFocusTarget.value =
        document.activeElement instanceof HTMLElement ? document.activeElement : null;
      focusMobileSidebar();
    } else if (!shouldManageMobileSidebar && mobileSidebarWasOpen.value) {
      restoreFocus();
    }

    mobileSidebarWasOpen.value = shouldManageMobileSidebar;
  },
  { immediate: true }
);

useEventListener("keydown", (event) => {
  if (event.key !== "Escape" || event.defaultPrevented) return;
  if (!isMobile.value || !isSidebarOpen.value) return;

  event.preventDefault();
  closeSidebar();
});

useEventListener("keydown", (event) => {
  if (event.key !== "Tab" || !isMobile.value || !isSidebarOpen.value) return;

  const sidebar = getMobileSidebar();
  if (!sidebar) return;

  const focusableElements = getFocusableElements(sidebar);
  if (focusableElements.length === 0) {
    event.preventDefault();
    sidebar.focus({ preventScroll: true });
    return;
  }

  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];
  const activeElement = document.activeElement;

  if (event.shiftKey && (activeElement === firstFocusable || !sidebar.contains(activeElement))) {
    event.preventDefault();
    lastFocusable.focus({ preventScroll: true });
  } else if (
    !event.shiftKey &&
    (activeElement === lastFocusable || !sidebar.contains(activeElement))
  ) {
    event.preventDefault();
    firstFocusable.focus({ preventScroll: true });
  }
});

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
