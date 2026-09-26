<template>
  <BaseLayout>
    <!-- 第一列：一级菜单图标栏 -->
    <aside class="layout-double__rail" aria-label="一级导航">
      <div class="layout-double__rail-inner">
        <AppLogo v-if="isShowLogo" :collapse="true" />
        <el-scrollbar>
          <DoubleRailMenu />
        </el-scrollbar>
      </div>
    </aside>

    <!-- 第二列：当前一级菜单的子菜单；一级菜单没有子菜单或被收起时隐藏 -->
    <div
      id="layout-sidebar"
      class="layout-double__panel"
      :class="{ 'is-collapsed': !isPanelVisible }"
      role="navigation"
      aria-label="主导航"
      :aria-hidden="isPanelVisible ? undefined : 'true'"
      :inert="!isPanelVisible"
    >
      <div class="layout-double__panel-inner">
        <div class="layout-double__panel-title">{{ panelTitle }}</div>
        <el-scrollbar>
          <el-menu
            :default-active="activeLeftMenuPath"
            :collapse="false"
            :collapse-transition="false"
            :unique-opened="false"
          >
            <MenuItem
              v-for="item in sidebarMenuRoutes"
              :key="item.path"
              :item="item"
              :base-path="resolvePath(item.path)"
            />
          </el-menu>
        </el-scrollbar>
      </div>
    </div>

    <!-- 主内容区 -->
    <div
      :class="{ hasTagsView: isShowTagsView, 'layout__main--with-panel': isPanelVisible }"
      class="layout__main"
    >
      <NavBar />
      <TagsView v-if="isShowTagsView" />
      <AppMain />
    </div>
  </BaseLayout>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useWindowSize } from "@vueuse/core";
import { useLayout, useLayoutMenu } from "@/composables";
import { translateRouteTitle } from "@/utils/i18n";
import { useMixLayoutState } from "../mix/useMixLayoutState";
import BaseLayout from "../base/index.vue";
import AppLogo from "../../components/AppLogo/index.vue";
import NavBar from "../../components/NavBar/index.vue";
import TagsView from "../../components/TagsView/index.vue";
import AppMain from "../../components/AppMain/index.vue";
import MenuItem from "../../components/Menu/components/MenuItem.vue";
import DoubleRailMenu from "../../components/Menu/DoubleRailMenu.vue";
import { hasSubMenus } from "../../components/Menu/useTopMenuNavigation";

const route = useRoute();
const { isShowTagsView, isShowLogo, isSidebarOpen, isMobile } = useLayout();
const { routes, sideMenuRoutes, activeTopMenuPath } = useLayoutMenu();
const { width } = useWindowSize();

// 第二列复用 mix 布局左栏的状态：激活项、子菜单路径拼接与路由同步
const { activeLeftMenuPath, sidebarMenuRoutes, resolvePath } = useMixLayoutState({
  route,
  activeTopMenuPath,
  viewportWidth: width,
  isMobile,
  routes,
  sideMenuRoutes,
});

const activeTopMenu = computed(() =>
  routes.value.find((item) => item.path === activeTopMenuPath.value)
);
// 顶栏的折叠按钮收起第二列；只有一个可见子菜单的一级菜单直接当叶子，不显示第二列
const isPanelVisible = computed(
  () => isSidebarOpen.value && !!activeTopMenu.value && hasSubMenus(activeTopMenu.value)
);
const panelTitle = computed(() => translateRouteTitle(activeTopMenu.value?.meta?.title));
</script>

<style lang="scss" scoped>
$double-rail-width: 80px;
$double-panel-width: 200px;

.layout-double__rail,
.layout-double__panel {
  position: fixed;
  top: 0;
  bottom: 0;
  z-index: 999;
}

.layout-double__rail {
  left: 0;
  width: $double-rail-width;
}

.layout-double__panel {
  left: $double-rail-width;
  width: $double-panel-width;
  overflow: hidden;
  transition:
    width var(--ff-duration-base) var(--ff-ease-standard),
    opacity var(--ff-duration-base) var(--ff-ease-standard);

  &.is-collapsed {
    width: 0;
    opacity: 0;
  }
}

// 两列都是悬浮玻璃面板：上下和左侧留 --ff-shell-gap，玻璃材质由 skins/_chrome.scss 提供
.layout-double__rail-inner,
.layout-double__panel-inner {
  position: relative;
  display: flex;
  flex-direction: column;
  height: calc(100% - 2 * var(--ff-shell-gap));
  margin: var(--ff-shell-gap) 0 var(--ff-shell-gap) var(--ff-shell-gap);

  :deep(.el-scrollbar) {
    flex: 1;
    min-height: 0;
  }

  :deep(.el-menu) {
    border: none;
  }
}

.layout-double__rail-inner {
  width: calc(100% - var(--ff-shell-gap));
}

.layout-double__panel-inner {
  width: calc($double-panel-width - var(--ff-shell-gap));
}

.layout-double__panel-title {
  display: flex;
  flex: none;
  align-items: center;
  height: var(--ff-shell-bar-height);
  padding: 0 18px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 15px;
  font-weight: 600;
  color: var(--ff-shell-text);
  white-space: nowrap;
  border-bottom: 1px solid var(--ff-shell-border);
}

.layout__main {
  position: relative;
  height: 100%;
  margin-left: $double-rail-width;
  overflow-y: auto;
  background: transparent;
  transition: margin-left var(--ff-duration-base) var(--ff-ease-standard);

  &--with-panel {
    margin-left: $double-rail-width + $double-panel-width;
  }
}

.hasTagsView {
  :deep(.app-main) {
    height: calc(100vh - $navbar-height - $tags-view-height) !important;
  }
}
</style>
