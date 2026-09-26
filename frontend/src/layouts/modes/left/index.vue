<template>
  <BaseLayout>
    <!-- 左侧菜单栏 -->
    <div
      id="layout-sidebar"
      class="layout__sidebar"
      role="navigation"
      aria-label="主导航"
      tabindex="-1"
      :class="{
        'layout__sidebar--collapsed': isCollapsedView,
        'layout__sidebar--peeking': isPeeking,
      }"
      :aria-hidden="isMobile && !isSidebarOpen ? 'true' : undefined"
      :inert="isMobile && !isSidebarOpen"
      @mouseenter="startPeek"
      @mouseleave="endPeek"
    >
      <div :class="{ 'has-logo': isShowLogo }" class="layout-sidebar">
        <!-- Logo -->
        <AppLogo v-if="isShowLogo" :collapse="isCollapsedView" />
        <!-- 主菜单内容 -->
        <el-scrollbar>
          <BasicMenu :data="routes" base-path="" :collapsed="isCollapsedView" />
        </el-scrollbar>
      </div>
    </div>

    <!-- 主内容区 -->
    <div
      :class="{
        hasTagsView: isShowTagsView,
        'layout__main--collapsed': !isSidebarOpen,
      }"
      class="layout__main"
    >
      <NavBar />
      <TagsView v-if="isShowTagsView" />
      <AppMain />
    </div>
  </BaseLayout>
</template>

<script setup lang="ts">
import { useLayout } from "@/composables/layout/useLayout";
import { useLayoutMenu } from "@/composables/layout/useLayoutMenu";
import BaseLayout from "../base/index.vue";
import AppLogo from "../../components/AppLogo/index.vue";
import NavBar from "../../components/NavBar/index.vue";
import TagsView from "../../components/TagsView/index.vue";
import AppMain from "../../components/AppMain/index.vue";
import BasicMenu from "../../components/Menu/BasicMenu.vue";
import { useSettingsStore } from "@/store";

// 布局相关参数
const { isShowTagsView, isShowLogo, isSidebarOpen, isMobile } = useLayout();
const settingsStore = useSettingsStore();

// 收起时悬停预览：只是组件内的临时状态，不改写持久化的侧栏展开状态；
// 预览时侧栏浮在内容上方，主内容仍按收起宽度留边，页面不重排
const PEEK_DELAY = 150;
const isPeeking = ref(false);
let peekTimer: ReturnType<typeof setTimeout> | undefined;
const canPeek = computed(
  () => !isSidebarOpen.value && !isMobile.value && settingsStore.sidebarPeek
);
const isCollapsedView = computed(() => !isSidebarOpen.value && !isPeeking.value);

function startPeek() {
  if (!canPeek.value) return;
  clearTimeout(peekTimer);
  peekTimer = setTimeout(() => {
    isPeeking.value = true;
  }, PEEK_DELAY);
}

function endPeek() {
  clearTimeout(peekTimer);
  isPeeking.value = false;
}

watch(canPeek, (enabled) => {
  if (!enabled) endPeek();
});
onBeforeUnmount(endPeek);

// 菜单相关
const { routes } = useLayoutMenu();
</script>

<style lang="scss" scoped>
.layout {
  &__sidebar {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 999;
    width: $sidebar-width;
    transition: width var(--ff-duration-base) var(--ff-ease-standard);

    &--collapsed {
      width: $sidebar-width-collapsed;
    }

    // 悬浮面板：左、上、下各留 --ff-shell-gap，玻璃材质由 skins/_chrome.scss 提供
    .layout-sidebar {
      position: relative;
      width: calc(100% - var(--ff-shell-gap));
      height: calc(100% - 2 * var(--ff-shell-gap));
      margin: var(--ff-shell-gap) 0 var(--ff-shell-gap) var(--ff-shell-gap);
      background: transparent;
      transition: width var(--ff-duration-base) var(--ff-ease-standard);

      &.has-logo {
        .el-scrollbar {
          height: calc(100% - var(--ff-shell-bar-height));
        }
      }

      :deep(.el-menu) {
        border: none;
      }
    }
  }

  &__main {
    position: relative;
    height: 100%;
    margin-left: $sidebar-width;
    overflow-y: auto;
    background: transparent;
    transition: margin-left var(--ff-duration-base) var(--ff-ease-standard);

    &--collapsed {
      margin-left: $sidebar-width-collapsed;
    }

    .fixed-header {
      position: sticky;
      top: 0;
      z-index: 9;
      transition: width 0.28s;
    }
  }
}

/* 移动端样式 */
.mobile {
  .layout__sidebar {
    width: $sidebar-width !important;
    transition:
      transform var(--ff-duration-base) var(--ff-ease-standard),
      width 0s;
  }

  &.hideSidebar {
    .layout__sidebar {
      transform: translateX(-$sidebar-width);
    }
  }

  &.openSidebar {
    .layout__sidebar {
      transform: translateX(0);
    }
  }

  .layout__main {
    margin-left: 0 !important;
  }
}

.hasTagsView {
  :deep(.app-main) {
    height: calc(100vh - $navbar-height - $tags-view-height) !important;
  }
}
</style>
