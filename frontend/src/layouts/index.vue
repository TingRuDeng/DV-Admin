<template>
  <div class="layout-wrapper">
    <component :is="currentLayoutComponent" />

    <!-- 设置面板 - 独立于布局组件 -->
    <Settings v-if="isShowSettings" />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useLayout } from "@/composables/layout/useLayout";
import LeftLayout from "@/layouts/modes/left/index.vue";
import TopLayout from "@/layouts/modes/top/index.vue";
import MixLayout from "@/layouts/modes/mix/index.vue";
import DoubleLayout from "@/layouts/modes/double/index.vue";
import Settings from "./components/Settings/index.vue";
import { LayoutMode } from "@/enums/settings/layout-enum";
import { defaultSettings } from "@/settings";

const { currentLayout, isMobile } = useLayout();
const route = useRoute();

/// Select the corresponding component based on the current layout mode
const currentLayoutComponent = computed(() => {
  const override = route.meta?.layout as LayoutMode | undefined;
  // 路由级覆盖同样遵守“双列布局在移动端退化为左侧布局”
  const layoutToUse =
    isMobile.value && override === LayoutMode.DOUBLE
      ? LayoutMode.LEFT
      : (override ?? currentLayout.value);
  switch (layoutToUse) {
    case LayoutMode.TOP:
      return TopLayout;
    case LayoutMode.MIX:
      return MixLayout;
    case LayoutMode.DOUBLE:
      return DoubleLayout;
    case LayoutMode.LEFT:
    default:
      return LeftLayout;
  }
});

/// Whether to show the settings panel
const isShowSettings = computed(() => defaultSettings.showSettings);
</script>

<style lang="scss" scoped>
.layout-wrapper {
  width: 100%;
  height: 100%;
}
</style>
