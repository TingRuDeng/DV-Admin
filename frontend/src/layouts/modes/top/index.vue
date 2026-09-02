<template>
  <BaseLayout>
    <!-- 顶部菜单栏 -->
    <div class="layout__header">
      <div class="layout__header-left">
        <!-- Logo -->
        <AppLogo v-if="isShowLogo" :collapse="isLogoCollapsed" />
        <Hamburger v-if="isMobile" :is-active="isSidebarOpen" @toggle-click="toggleSidebar" />
        <!-- 菜单 -->
        <BasicMenu v-if="!isMobile" :data="routes" menu-mode="horizontal" base-path="" />
      </div>
      <!-- 操作按钮 -->
      <div class="layout__header-right">
        <NavbarActions />
      </div>
    </div>

    <aside
      v-if="isMobile"
      class="layout__mobile-menu"
      :class="{ 'layout__mobile-menu--collapsed': !isSidebarOpen }"
      aria-label="主导航"
      :aria-hidden="!isSidebarOpen ? 'true' : undefined"
      :inert="!isSidebarOpen"
    >
      <el-scrollbar>
        <BasicMenu :data="routes" base-path="" />
      </el-scrollbar>
    </aside>

    <!-- 主内容区 -->
    <div :class="{ hasTagsView: isShowTagsView }" class="layout__main">
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
import BasicMenu from "../../components/Menu/BasicMenu.vue";
import NavbarActions from "../../components/NavBar/components/NavbarActions.vue";
import TagsView from "../../components/TagsView/index.vue";
import AppMain from "../../components/AppMain/index.vue";
import Hamburger from "@/components/Hamburger/index.vue";

// 布局相关参数
const { isShowTagsView, isShowLogo, isMobile, isSidebarOpen, toggleSidebar } = useLayout();

// 菜单相关
const { routes } = useLayoutMenu();

// 响应式窗口尺寸
const { width } = useWindowSize();

// 只有在小屏设备（移动设备）时才折叠Logo（只显示图标，隐藏文字）
const isLogoCollapsed = computed(() => isMobile.value || width.value < 768);
</script>

<style lang="scss" scoped>
.layout {
  &__header {
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: $navbar-height;
    background: var(--ff-shell-surface);
    border-bottom: 1px solid var(--ff-shell-border);
    box-shadow: var(--ff-shadow-shell);

    &-left {
      display: flex;
      flex: 1;
      align-items: center;
      min-width: 0; // 允许flex收缩
      height: 100%;

      // Logo样式由AppLogo组件的全局样式控制
      :deep(.logo) {
        flex-shrink: 0; // 防止Logo被压缩
        height: $navbar-height;
      }
    }

    &-right {
      display: flex;
      flex-shrink: 0; // 防止操作按钮被压缩
      align-items: center;
      height: 100%;
      padding: 0 8px;
    }

    // 菜单样式
    :deep(.el-menu--horizontal) {
      flex: 1;
      min-width: 0; // 允许菜单收缩
      height: $navbar-height;
      overflow: hidden; // 防止菜单溢出
      line-height: $navbar-height;
      background-color: transparent;
      border: none;

      .el-menu-item {
        height: $navbar-height;
        line-height: $navbar-height;
      }

      .el-sub-menu {
        .el-sub-menu__title {
          height: $navbar-height;
          line-height: $navbar-height;
        }

        // 父菜单激活状态 - 水平布局专用
        &.has-active-child {
          .el-sub-menu__title {
            color: var(--el-color-primary) !important;
            border-bottom: 2px solid var(--el-color-primary) !important;

            .menu-icon {
              color: var(--el-color-primary) !important;
            }
          }
        }
      }

      // 修复子菜单弹出位置
      .el-menu--popup {
        min-width: 160px;
      }
    }
  }

  &__main {
    height: calc(100vh - $navbar-height);
    overflow-y: auto;
    background: var(--ff-shell-bg);
  }

  &__mobile-menu {
    position: fixed;
    top: $navbar-height;
    bottom: 0;
    left: 0;
    z-index: 1001;
    width: $sidebar-width;
    overflow: hidden;
    background: var(--ff-shell-surface);
    border-right: 1px solid var(--ff-shell-border);
    box-shadow: var(--ff-shadow-shell-raised);
    transition: transform var(--ff-duration-base) var(--ff-ease-standard);

    &--collapsed {
      transform: translateX(-$sidebar-width);
    }

    :deep(.el-scrollbar) {
      height: 100%;
    }
  }
}

@media (max-width: 991px) {
  .layout__header-left {
    flex: 0 1 auto;
  }
}

// 当存在TagsView时的样式调整
.hasTagsView {
  :deep(.app-main) {
    height: calc(100vh - $navbar-height - $tags-view-height) !important;
  }
}
</style>
