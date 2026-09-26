<!-- 混合布局顶部菜单 -->
<template>
  <el-menu
    mode="horizontal"
    :default-active="activeTopMenuPath"
    :background-color="
      theme === 'dark' || sidebarColorScheme === SidebarColor.CLASSIC_BLUE
        ? variables['menu-background']
        : undefined
    "
    :text-color="
      theme === 'dark' || sidebarColorScheme === SidebarColor.CLASSIC_BLUE
        ? variables['menu-text']
        : undefined
    "
    :active-text-color="
      theme === 'dark' || sidebarColorScheme === SidebarColor.CLASSIC_BLUE
        ? variables['menu-active-text']
        : undefined
    "
    @select="handleMenuSelect"
  >
    <el-menu-item v-for="menuItem in topMenus" :key="menuItem.path" :index="menuItem.path">
      <MenuItemContent
        v-if="menuItem.meta"
        :icon="menuItem.meta.icon"
        :title="menuItem.meta.title"
      />
    </el-menu-item>
  </el-menu>
</template>

<script lang="ts" setup>
import MenuItemContent from "./components/MenuItemContent.vue";
import { useSettingsStore } from "@/store";
import variables from "@/styles/variables.module.scss";
import { SidebarColor } from "@/enums/settings/theme-enum";
import { useTopMenuNavigation } from "./useTopMenuNavigation";

defineOptions({
  name: "MixTopMenu",
});

const settingsStore = useSettingsStore();

// 获取主题
const theme = computed(() => settingsStore.theme);

// 获取浅色主题下的侧边栏配色方案
const sidebarColorScheme = computed(() => settingsStore.sidebarColorScheme);

// 一级菜单列表、激活状态和点击跳转与双列布局共用
const { activeTopMenuPath, selectTopMenu, topMenus } = useTopMenuNavigation();

function handleMenuSelect(routePath: string) {
  selectTopMenu(routePath);
}
</script>

<style lang="scss" scoped>
.el-menu {
  width: 100%;
  height: 100%;

  &--horizontal {
    height: $navbar-height !important;

    // 确保菜单项垂直居中
    :deep(.el-menu-item) {
      height: 100%;
      line-height: $navbar-height;
    }

    // 移除默认的底部边框
    &:after {
      display: none;
    }
  }
}
</style>
