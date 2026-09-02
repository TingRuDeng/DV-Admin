<template>
  <BaseLayout>
    <!-- 左侧菜单栏 -->
    <div
      class="layout__sidebar"
      :class="{ 'layout__sidebar--collapsed': !isSidebarOpen }"
      :aria-hidden="isMobile && !isSidebarOpen ? 'true' : undefined"
      :inert="isMobile && !isSidebarOpen"
    >
      <div :class="{ 'has-logo': isShowLogo }" class="layout-sidebar">
        <!-- Logo -->
        <AppLogo v-if="isShowLogo" :collapse="!isSidebarOpen" />
        <!-- 主菜单内容 -->
        <el-scrollbar>
          <BasicMenu :data="routes" base-path="" />
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

// 布局相关参数
const { isShowTagsView, isShowLogo, isSidebarOpen, isMobile } = useLayout();

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
    background: var(--ff-shell-surface);
    border-right: 1px solid var(--ff-shell-border);
    box-shadow: var(--ff-shadow-shell);
    transition: width var(--ff-duration-base) var(--ff-ease-standard);

    &--collapsed {
      width: $sidebar-width-collapsed;
    }

    .layout-sidebar {
      position: relative;
      height: 100%;
      background: transparent;
      transition: width var(--ff-duration-base) var(--ff-ease-standard);

      &.has-logo {
        .el-scrollbar {
          height: calc(100vh - $navbar-height);
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
    background: var(--ff-shell-bg);
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
    box-shadow: var(--ff-shadow-shell-raised);
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
