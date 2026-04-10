<template>
  <div class="tags-container">
    <!-- 水平滚动容器 -->
    <el-scrollbar
      ref="scrollbarRef"
      class="scroll-container"
      :view-style="{ height: '100%' }"
      @wheel="handleScroll"
    >
      <div h-full flex-y-center gap-8px>
        <el-tag
          v-for="tag in visitedViews"
          :key="tag.fullPath"
          h-26px
          cursor-pointer
          :closable="!tag.affix"
          :effect="tagsViewStore.isActive(tag) ? 'dark' : 'light'"
          :type="tagsViewStore.isActive(tag) ? 'primary' : 'info'"
          @click.middle="handleMiddleClick(tag)"
          @contextmenu.prevent="(event: MouseEvent) => openContextMenu(tag, event)"
          @close="closeSelectedTag(tag)"
          @click="
            router.push({
              path: tag.fullPath,
              query: tag.query,
            })
          "
        >
          {{ translateRouteTitle(tag.title) }}
        </el-tag>
      </div>
    </el-scrollbar>

    <!-- 标签右键菜单 -->
    <Teleport to="body">
      <ul
        v-show="contextMenu.visible"
        class="contextmenu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <li @click="refreshSelectedTag(selectedTag)">
          <div class="i-svg:refresh" />
          刷新
        </li>
        <li v-if="!selectedTag?.affix" @click="closeSelectedTag(selectedTag)">
          <div class="i-svg:close" />
          关闭
        </li>
        <li @click="closeOtherTags">
          <div class="i-svg:close_other" />
          关闭其它
        </li>
        <li v-if="!isFirstView" @click="closeLeftTags">
          <div class="i-svg:close_left" />
          关闭左侧
        </li>
        <li v-if="!isLastView" @click="closeRightTags">
          <div class="i-svg:close_right" />
          关闭右侧
        </li>
        <li @click="closeAllTags(selectedTag)">
          <div class="i-svg:close_all" />
          关闭所有
        </li>
      </ul>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter, type RouteRecordRaw } from "vue-router";
import { resolve } from "path-browserify";
import { translateRouteTitle } from "@/utils/i18n";
import { usePermissionStore, useTagsViewStore } from "@/store";

interface ContextMenu {
  visible: boolean;
  x: number;
  y: number;
}

const router = useRouter();
const route = useRoute();

// 状态管理
const permissionStore = usePermissionStore();
const tagsViewStore = useTagsViewStore();

const { visitedViews } = storeToRefs(tagsViewStore);

// 当前选中的标签
const selectedTag = ref<TagView | null>(null);

// 右键菜单状态
const contextMenu = reactive<ContextMenu>({
  visible: false,
  x: 0,
  y: 0,
});

// 滚动条引用
const scrollbarRef = ref();

// 路由映射缓存，提升查找性能
const routePathMap = computed(() => {
  const map = new Map<string, TagView>();
  visitedViews.value.forEach((tag) => {
    map.set(tag.path, tag);
  });
  return map;
});

// 判断是否为第一个标签
const isFirstView = computed(() => {
  if (!selectedTag.value) return false;
  return (
    selectedTag.value.path === "/dashboard" ||
    selectedTag.value.fullPath === visitedViews.value[1]?.fullPath
  );
});

// 判断是否为最后一个标签
const isLastView = computed(() => {
  if (!selectedTag.value) return false;
  return selectedTag.value.fullPath === visitedViews.value[visitedViews.value.length - 1]?.fullPath;
});

/**
 * 递归提取固定标签
 */
const extractAffixTags = (routes: RouteRecordRaw[], basePath = "/"): TagView[] => {
  const affixTags: TagView[] = [];

  const traverse = (routeList: RouteRecordRaw[], currentBasePath: string) => {
    routeList.forEach((route) => {
      const fullPath = resolve(currentBasePath, route.path);

      // 如果是固定标签，添加到列表
      if (route.meta?.affix) {
        affixTags.push({
          path: fullPath,
          fullPath,
          name: String(route.name || ""),
          title: route.meta.title || "no-name",
          affix: true,
          keepAlive: route.meta.keepAlive || false,
        });
      }

      // 递归处理子路由
      if (route.children?.length) {
        traverse(route.children, fullPath);
      }
    });
  };

  traverse(routes, basePath);
  return affixTags;
};

/**
 * 初始化固定标签
 */
const initAffixTags = () => {
  const affixTags = extractAffixTags(permissionStore.routes);

  affixTags.forEach((tag) => {
    if (tag.name) {
      tagsViewStore.addVisitedView(tag);
    }
  });
};

/**
 * 添加当前路由标签
 */
const addCurrentTag = () => {
  if (!route.meta?.title) return;

  tagsViewStore.addView({
    name: route.name as string,
    title: route.meta.title,
    path: route.path,
    fullPath: route.fullPath,
    affix: route.meta.affix || false,
    keepAlive: route.meta.keepAlive || false,
    query: route.query,
  });
};

/**
 * 更新当前标签
 */
const updateCurrentTag = () => {
  nextTick(() => {
    const currentTag = routePathMap.value.get(route.path);

    if (currentTag && currentTag.fullPath !== route.fullPath) {
      tagsViewStore.updateVisitedView({
        name: route.name as string,
        title: route.meta?.title || "",
        path: route.path,
        fullPath: route.fullPath,
        affix: route.meta?.affix || false,
        keepAlive: route.meta?.keepAlive || false,
        query: route.query,
      });
    }
  });
};

/**
 * 处理中键点击
 */
const handleMiddleClick = (tag: TagView) => {
  if (!tag.affix) {
    closeSelectedTag(tag);
  }
};

/**
 * 打开右键菜单
 */
const openContextMenu = (tag: TagView, event: MouseEvent) => {
  contextMenu.x = event.clientX;
  contextMenu.y = event.clientY;
  contextMenu.visible = true;

  selectedTag.value = tag;
};

/**
 * 关闭右键菜单
 */
const closeContextMenu = () => {
  contextMenu.visible = false;
};

/**
 * 处理滚轮事件
 */
const handleScroll = (event: WheelEvent) => {
  closeContextMenu();

  const scrollWrapper = scrollbarRef.value?.wrapRef;
  if (!scrollWrapper) return;

  const hasHorizontalScroll = scrollWrapper.scrollWidth > scrollWrapper.clientWidth;
  if (!hasHorizontalScroll) return;

  const deltaY = event.deltaY || -(event as any).wheelDelta || 0;
  const newScrollLeft = scrollWrapper.scrollLeft + deltaY;

  scrollbarRef.value.setScrollLeft(newScrollLeft);
};

/**
 * 刷新标签
 */
const refreshSelectedTag = (tag: TagView | null) => {
  if (!tag) return;

  tagsViewStore.delCachedView(tag);
  nextTick(() => {
    router.replace("/redirect" + tag.fullPath);
  });
};

/**
 * 关闭标签
 */
const closeSelectedTag = (tag: TagView | null) => {
  if (!tag) return;

  tagsViewStore.delView(tag).then((result: any) => {
    if (tagsViewStore.isActive(tag)) {
      tagsViewStore.toLastView(result.visitedViews, tag);
    }
  });
};

/**
 * 关闭左侧标签
 */
const closeLeftTags = () => {
  if (!selectedTag.value) return;

  tagsViewStore.delLeftViews(selectedTag.value).then((result: any) => {
    const hasCurrentRoute = result.visitedViews.some((item: TagView) => item.path === route.path);

    if (!hasCurrentRoute) {
      tagsViewStore.toLastView(result.visitedViews);
    }
  });
};

/**
 * 关闭右侧标签
 */
const closeRightTags = () => {
  if (!selectedTag.value) return;

  tagsViewStore.delRightViews(selectedTag.value).then((result: any) => {
    const hasCurrentRoute = result.visitedViews.some((item: TagView) => item.path === route.path);

    if (!hasCurrentRoute) {
      tagsViewStore.toLastView(result.visitedViews);
    }
  });
};

/**
 * 关闭其他标签
 */
const closeOtherTags = () => {
  if (!selectedTag.value) return;

  router.push(selectedTag.value);
  tagsViewStore.delOtherViews(selectedTag.value).then(() => {
    updateCurrentTag();
  });
};

/**
 * 关闭所有标签
 */
const closeAllTags = (tag: TagView | null) => {
  tagsViewStore.delAllViews().then((result: any) => {
    tagsViewStore.toLastView(result.visitedViews, tag || undefined);
  });
};

// 右键菜单管理
const useContextMenuManager = () => {
  const handleOutsideClick = () => {
    closeContextMenu();
  };

  watchEffect(() => {
    if (contextMenu.visible) {
      document.addEventListener("click", handleOutsideClick);
    } else {
      document.removeEventListener("click", handleOutsideClick);
    }
  });

  // 组件卸载时清理
  onBeforeUnmount(() => {
    document.removeEventListener("click", handleOutsideClick);
  });
};

// 监听路由变化
watch(
  route,
  () => {
    addCurrentTag();
    updateCurrentTag();
  },
  { immediate: true }
);

// 初始化
onMounted(() => {
  initAffixTags();
});

// 启用右键菜单管理
useContextMenuManager();
</script>

<style lang="scss" scoped>
.tags-container {
  width: 100%;
  height: $tags-view-height;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);

  .scroll-container {
    white-space: nowrap;
  }

  /* 标签样式优化 */
  :deep(.el-tag) {
    height: 28px;
    padding: 0 12px;
    margin: 0 4px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
    border: 1px solid transparent;
    transition: all 0.2s ease;

    /* 默认状态 */
    &.el-tag--info {
      background: rgba(255, 255, 255, 0.8);
      border-color: rgba(0, 0, 0, 0.06);
      color: #64748b;

      &:hover {
        background: rgba(255, 255, 255, 1);
        border-color: rgba(59, 130, 246, 0.3);
        color: #3b82f6;
      }
    }

    /* 激活状态 */
    &.el-tag--primary {
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
      border-color: rgba(59, 130, 246, 0.3);
      color: #3b82f6;
      box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);

      &:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%);
        border-color: rgba(59, 130, 246, 0.5);
      }
    }

    /* 关闭按钮 */
    .el-tag__close {
      margin-left: 6px;
      font-size: 12px;
      color: inherit;
      opacity: 0.6;

      &:hover {
        opacity: 1;
        background: transparent;
      }
    }
  }
}

/* 右键菜单优化 */
.contextmenu {
  position: absolute;
  z-index: 3000;
  padding: 8px 0;
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  list-style-type: none;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

  li {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 10px 16px;
    margin: 0;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: rgba(59, 130, 246, 0.08);
      color: #3b82f6;
    }

    &:first-child {
      border-radius: 12px 12px 0 0;
    }

    &:last-child {
      border-radius: 0 0 12px 12px;
    }
  }
}

/* 深色模式适配 */
html.dark {
  .tags-container {
    background: rgba(30, 41, 59, 0.6);
    border-bottom-color: rgba(255, 255, 255, 0.05);

    :deep(.el-tag) {
      &.el-tag--info {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(255, 255, 255, 0.08);
        color: #cbd5e1;

        &:hover {
          background: rgba(30, 41, 59, 1);
          border-color: rgba(96, 165, 250, 0.3);
          color: #60a5fa;
        }
      }

      &.el-tag--primary {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        border-color: rgba(96, 165, 250, 0.3);
        color: #60a5fa;
        box-shadow: 0 2px 8px rgba(96, 165, 250, 0.2);

        &:hover {
          background: linear-gradient(135deg, rgba(96, 165, 250, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
          border-color: rgba(96, 165, 250, 0.5);
        }
      }
    }
  }

  .contextmenu {
    background: rgba(30, 41, 59, 0.95);
    border-color: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;

    li:hover {
      background: rgba(96, 165, 250, 0.15);
      color: #60a5fa;
    }
  }
}
</style>
