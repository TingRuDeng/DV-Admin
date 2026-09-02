<template>
  <div class="sidebar-logo-container" :class="{ collapse }">
    <router-link class="sidebar-logo-link" to="/" :aria-label="platformName">
      <span class="sidebar-logo-mark" aria-hidden="true">{{ logoMark }}</span>
      <transition name="sidebar-logo-fade">
        <span v-if="!collapse" class="sidebar-title">{{ platformName }}</span>
      </transition>
    </router-link>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  collapse: boolean;
}>();

const logoText = import.meta.env.VITE_APP_LOGO_TEXT || "DV";
const logoMark = logoText.slice(0, 2).toUpperCase();
const platformName = import.meta.env.VITE_APP_TITLE || "DV-Admin";
</script>

<style lang="scss" scoped>
.sidebar-logo-link {
  display: flex;
  gap: 10px;
  align-items: center;
  width: 100%;
  min-width: 0;
  height: 100%;
  color: var(--sidebar-logo-text-color);
  text-decoration: none;
}

.sidebar-logo-container {
  display: flex;
  align-items: center;
  width: 100%;
  height: $navbar-height;
  padding: 0 14px;
  background: var(--sidebar-logo-background);
  border-bottom: 1px solid var(--ff-shell-border);
  transition:
    width var(--ff-duration-base) var(--ff-ease-standard),
    padding var(--ff-duration-base) var(--ff-ease-standard);

  &.collapse {
    justify-content: center;
    padding: 0;

    .sidebar-logo-link {
      justify-content: center;
    }
  }
}

.sidebar-logo-mark {
  display: inline-flex;
  flex: 0 0 32px;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  font-size: 12px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 9px;
  box-shadow: 0 6px 14px -8px var(--el-color-primary);
}

.sidebar-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 17px;
  font-weight: 700;
  color: var(--ff-shell-text);
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.sidebar-logo-fade-enter-active,
.sidebar-logo-fade-leave-active {
  transition: opacity var(--ff-duration-fast) ease;
}

.sidebar-logo-fade-enter-from,
.sidebar-logo-fade-leave-to {
  opacity: 0;
}
</style>

<style lang="scss">
.layout-top,
.layout-mix {
  .sidebar-logo-container {
    background: transparent;
    border-bottom: 0;
  }
}

.openSidebar {
  &.layout-top .layout__header-left .sidebar-logo-container,
  &.layout-mix .layout__header-logo .sidebar-logo-container {
    width: $sidebar-width;
  }
}

.hideSidebar {
  &.layout-top .layout__header-left .sidebar-logo-container,
  &.layout-mix .layout__header-logo .sidebar-logo-container {
    width: $sidebar-width-collapsed;
  }
}
</style>
