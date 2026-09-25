<template>
  <BaseLayout>
    <!-- 顶部菜单栏 -->
    <div class="layout__header">
      <div class="layout__header-content">
        <!-- Logo区域 -->
        <div v-if="isShowLogo" class="layout__header-logo">
          <AppLogo :collapse="isLogoCollapsed" />
        </div>

        <Hamburger
          v-if="isMobile"
          :is-active="isSidebarOpen"
          controls="layout-sidebar"
          @toggle-click="toggleSidebar"
        />

        <!-- 顶部菜单区域 -->
        <div v-if="!isMobile" class="layout__header-menu">
          <MixTopMenu />
        </div>

        <!-- 右侧操作区域 -->
        <div class="layout__header-actions">
          <NavbarActions />
        </div>
      </div>
    </div>

    <!-- 主内容区容器 -->
    <div class="layout__container">
      <!-- 左侧菜单栏 -->
      <div
        id="layout-sidebar"
        class="layout__sidebar--left"
        role="navigation"
        aria-label="主导航"
        tabindex="-1"
        :class="{ 'layout__sidebar--collapsed': !isSidebarOpen }"
        :aria-hidden="isMobile && !isSidebarOpen ? 'true' : undefined"
        :inert="isMobile && !isSidebarOpen"
      >
        <el-scrollbar>
          <el-menu
            :default-active="activeLeftMenuPath"
            :collapse="!isSidebarOpen"
            :collapse-transition="false"
            :unique-opened="false"
            :background-color="variables['menu-background']"
            :text-color="variables['menu-text']"
            :active-text-color="variables['menu-active-text']"
          >
            <MenuItem
              v-for="item in sidebarMenuRoutes"
              :key="item.path"
              :item="item"
              :base-path="resolvePath(item.path)"
            />
          </el-menu>
        </el-scrollbar>
        <!-- 侧边栏切换按钮 -->
        <div class="layout__sidebar-toggle">
          <Hamburger
            :is-active="isSidebarOpen"
            controls="layout-sidebar"
            :label="isSidebarOpen ? '收起侧边导航' : '展开侧边导航'"
            @toggle-click="toggleSidebar"
          />
        </div>
      </div>

      <!-- 主内容区 -->
      <div :class="{ hasTagsView: isShowTagsView }" class="layout__main">
        <TagsView v-if="isShowTagsView" />
        <AppMain />
      </div>
    </div>
  </BaseLayout>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useWindowSize } from "@vueuse/core";
import { useLayout, useLayoutMenu } from "@/composables";
import { useMixLayoutState } from "./useMixLayoutState";
import BaseLayout from "../base/index.vue";
import AppLogo from "../../components/AppLogo/index.vue";
import MixTopMenu from "../../components/Menu/MixTopMenu.vue";
import NavbarActions from "../../components/NavBar/components/NavbarActions.vue";
import TagsView from "../../components/TagsView/index.vue";
import AppMain from "../../components/AppMain/index.vue";
import MenuItem from "../../components/Menu/components/MenuItem.vue";
import Hamburger from "@/components/Hamburger/index.vue";
import variables from "@/styles/variables.module.scss";

const route = useRoute();

// 布局相关参数
const { isShowTagsView, isShowLogo, isSidebarOpen, isMobile, toggleSidebar } = useLayout();

// 菜单相关
const { routes, sideMenuRoutes, activeTopMenuPath } = useLayoutMenu();

// 响应式窗口尺寸
const { width } = useWindowSize();

const { activeLeftMenuPath, isLogoCollapsed, sidebarMenuRoutes, resolvePath } = useMixLayoutState({
  route,
  activeTopMenuPath,
  viewportWidth: width,
  isMobile,
  routes,
  sideMenuRoutes,
});
</script>

<style lang="scss" scoped>
.layout {
  &__header {
    position: sticky;
    top: 0;
    z-index: 999;
    width: 100%;
    height: $navbar-height;

    &-content {
      display: flex;
      align-items: center;
      height: 100%;
      padding: 0;
    }

    &-logo {
      display: flex;
      flex-shrink: 0;
      align-items: center;
      justify-content: center;
      height: 100%;
    }

    &-menu {
      display: flex;
      flex: 1;
      align-items: center;
      min-width: 0;
      height: 100%;
      overflow: hidden;

      :deep(.el-menu) {
        height: 100%;
        background-color: transparent;
        border: none;
      }

      // 水平菜单项的胶囊形状和激活态由 skins/_menu.scss 统一提供
      :deep(.el-menu--horizontal) {
        display: flex;
        align-items: center;
        height: 100%;
      }
    }

    &-actions {
      display: flex;
      flex-shrink: 0;
      align-items: center;
      height: 100%;
      padding: 0 8px;
    }
  }

  &__container {
    display: flex;
    height: calc(100vh - $navbar-height);
    padding-top: 0;

    .layout__sidebar--left {
      position: relative;
      width: $sidebar-width;
      height: 100%;
      transition: width 0.28s;

      &.layout__sidebar--collapsed {
        width: $sidebar-width-collapsed !important;
      }

      // 宿主上下各有 --ff-shell-gap 内边距，把玻璃面板让出来
      :deep(.el-scrollbar) {
        height: calc(100vh - $navbar-height - 50px - 2 * var(--ff-shell-gap));
      }

      :deep(.el-menu) {
        height: 100%;
        border: none;
      }

      .layout__sidebar-toggle {
        position: absolute;
        bottom: var(--ff-shell-gap);
        left: var(--ff-shell-gap);
        display: flex;
        align-items: center;
        justify-content: center;
        width: calc(100% - var(--ff-shell-gap));
        height: 50px;
        line-height: 50px;
        border-top: 1px solid var(--ff-shell-border);
        border-radius: 0 0 var(--ff-radius-panel) var(--ff-radius-panel);
      }
    }

    .layout__main {
      flex: 1;
      min-width: 0;
      height: 100%;
      margin-left: 0;
      overflow-y: auto;
      background: transparent;
    }
  }
}

/* 移动端样式 */
.mobile {
  .layout__container {
    .layout__sidebar--left {
      position: fixed;
      top: $navbar-height;
      bottom: 0;
      left: 0;
      z-index: 1000;
      width: $sidebar-width !important;
      height: auto;
      transition: transform 0.28s;
    }
  }

  &.hideSidebar {
    .layout__sidebar--left {
      transform: translateX(-$sidebar-width);
    }
  }

  &.openSidebar {
    .layout__sidebar--left {
      transform: translateX(0);
    }
  }
}
:deep(.hasTagsView) {
  .app-main {
    height: calc(100vh - $navbar-height - $tags-view-height) !important;
  }
}
</style>
