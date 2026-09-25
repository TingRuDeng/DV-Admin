<template>
  <div class="sidebar-logo-container" :class="{ collapse }">
    <router-link class="sidebar-logo-link" to="/" :aria-label="platformName">
      <span class="sidebar-logo-mark" aria-hidden="true">
        <AppIcon name="command" :size="19" :stroke-width="2.2" />
      </span>
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

import AppIcon from "@/components/AppIcon/index.vue";

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
  font-weight: 700;
  color: var(--ff-on-iri);
  letter-spacing: -0.02em;
  background: var(--ff-iri);
  border-radius: 10px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.35),
    0 6px 16px -8px color-mix(in srgb, var(--ff-iri-b) 80%, transparent);
}

.sidebar-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 17px;
  font-weight: 600;
  color: var(--ff-shell-text);
  letter-spacing: -0.02em;
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
    height: 100%;
    background: transparent;
    border-bottom: 0;
  }
}

// left 布局的 Logo 行与顶栏玻璃面板等高，分隔线和顶栏面板底边对齐
.layout-left .layout__sidebar .sidebar-logo-container {
  height: var(--ff-shell-bar-height);
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
