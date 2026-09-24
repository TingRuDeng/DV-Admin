<template>
  <main class="app-main" :style="{ height: appMainHeight }">
    <router-view>
      <template #default="{ Component, route }">
        <transition name="ff-route" mode="out-in">
          <keep-alive :include="cachedViews">
            <component :is="currentComponent(Component, route)" :key="getComponentKey(route)" />
          </keep-alive>
        </transition>
      </template>
    </router-view>

    <!-- 返回顶部按钮 -->
    <el-backtop target=".app-main">
      <AppIcon name="arrow-up" :size="18" />
    </el-backtop>
  </main>
</template>

<script setup lang="ts">
import { type RouteLocationNormalized } from "vue-router";
import { useSettingsStore, useTagsViewStore } from "@/store";
import variables from "@/styles/variables.module.scss";
import { getRouteRenderKey } from "@/utils/view-cache";
import { createLogger } from "@/utils/logger";
import Error404 from "@/views/error/404.vue";
import AppIcon from "@/components/AppIcon/index.vue";

const appMainLogger = createLogger("AppMain");
const { cachedViews } = toRefs(useTagsViewStore());

// 当前组件
const wrapperMap = new Map<string, Component>();
const currentComponent = (component: Component, route: RouteLocationNormalized) => {
  if (!component) return;

  const componentName = getRouteRenderKey(route);
  let wrapper = wrapperMap.get(componentName);

  if (!wrapper) {
    wrapper = {
      name: componentName,
      render: () => {
        try {
          return h(component);
        } catch (error) {
          appMainLogger.error(`渲染路由组件失败: ${componentName}`, error);
          return h(Error404);
        }
      },
    };
    wrapperMap.set(componentName, wrapper);
  }

  // 添加组件数量限制
  if (wrapperMap.size > 100) {
    const firstKey = wrapperMap.keys().next().value;
    if (firstKey) {
      wrapperMap.delete(firstKey);
    }
  }

  return h(wrapper);
};

const getComponentKey = (route: RouteLocationNormalized) => {
  return getRouteRenderKey(route);
};

const appMainHeight = computed(() => {
  if (useSettingsStore().showTagsView) {
    return `calc(100vh - ${variables["navbar-height"]} - ${variables["tags-view-height"]})`;
  } else {
    return `calc(100vh - ${variables["navbar-height"]})`;
  }
});
</script>

<style lang="scss" scoped>
.app-main {
  position: relative;
  overflow-y: auto;
  scrollbar-gutter: stable;
  background: transparent;
}
</style>

<style lang="scss">
// 路由过渡类加在页面组件根节点上，不走 scoped；进场淡入并上移 8px，离场只淡出。
// 过渡结束后类名移除、不残留 transform，页面内 fixed 元素不会被带偏。
.ff-route-enter-active {
  transition:
    opacity 0.32s var(--ff-ease-out),
    transform 0.32s var(--ff-ease-out);
}

.ff-route-leave-active {
  transition: opacity 0.16s ease;
}

.ff-route-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.ff-route-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .ff-route-enter-active,
  .ff-route-leave-active {
    transition: none;
  }

  .ff-route-enter-from {
    transform: none;
  }
}
</style>
