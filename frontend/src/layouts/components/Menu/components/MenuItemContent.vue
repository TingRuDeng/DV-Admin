<template>
  <!-- 菜单图标 -->
  <AppIcon v-if="icon" :name="iconName" class="menu-icon" :size="18" />
  <template v-else>
    <AppIcon name="menu" class="menu-icon" :size="18" />
  </template>
  <!-- 菜单标题 -->
  <span v-if="title" class="menu-title ml-1">{{ translateRouteTitle(title) }}</span>
</template>

<script setup lang="ts">
import { translateRouteTitle } from "@/utils/i18n";
import AppIcon from "@/components/AppIcon/index.vue";

const props = defineProps<{
  icon?: string;
  title?: string;
}>();

const iconName = computed(() => {
  const value = props.icon ?? "menu";
  return value.replace(/^el-icon-/, "").replace(/^i-svg:/, "");
});
</script>

<style lang="scss" scoped>
.menu-icon {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: var(--el-menu-icon-width);
  height: var(--el-menu-icon-width);
  margin-right: 5px;
  font-size: 18px;
  color: currentcolor;
}

:global(.el-menu--collapse) .menu-icon {
  margin-right: 0;
}
</style>
