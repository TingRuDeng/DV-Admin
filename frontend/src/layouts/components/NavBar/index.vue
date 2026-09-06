<template>
  <div class="navbar">
    <div class="navbar__primary">
      <!-- 菜单折叠按钮 -->
      <Hamburger
        :is-active="isSidebarOpened"
        controls="layout-sidebar"
        @toggle-click="toggleSideBar"
      />
      <!-- 面包屑导航 -->
      <Breadcrumb />
    </div>
    <!-- 导航栏操作区域 -->
    <div class="navbar__actions">
      <NavbarActions />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from "@/store";
import Hamburger from "@/components/Hamburger/index.vue";
import Breadcrumb from "@/components/Breadcrumb/index.vue";
import NavbarActions from "./components/NavbarActions.vue";

const appStore = useAppStore();

// 侧边栏展开状态
const isSidebarOpened = computed(() => appStore.sidebar.opened);

// 切换侧边栏展开/折叠状态
function toggleSideBar() {
  appStore.toggleSidebar();
}
</script>

<style lang="scss" scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: $navbar-height;
  padding: 0 12px;

  &__primary {
    display: flex;
    flex: 1;
    align-items: center;
    min-width: 0;
  }

  &__actions {
    display: flex;
    align-items: center;
    height: 100%;
  }
}

@media (max-width: 767px) {
  .navbar {
    padding: 0 6px;

    :deep(.el-breadcrumb) {
      display: none;
    }
  }
}
</style>
