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
        <TagItem
          v-for="tag in visitedViews"
          :key="tag.fullPath"
          :tag="tag"
          :is-active="tagsViewStore.isActive(tag)"
          @close="closeSelectedTag(tag)"
          @middle-click="handleMiddleClick(tag)"
          @navigate="navigateToTag(tag)"
          @open-menu="openContextMenu"
        />
      </div>
    </el-scrollbar>

    <TagsContextMenu
      :is-first-view="isFirstView"
      :is-last-view="isLastView"
      :selected-tag="selectedTag"
      :visible="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
      @refresh="refreshSelectedTag(selectedTag)"
      @close="closeSelectedTag(selectedTag)"
      @close-other="closeOtherTags"
      @close-left="closeLeftTags"
      @close-right="closeRightTags"
      @close-all="closeAllTags(selectedTag)"
    />
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { useTagsViewStore } from "@/store";
import TagItem from "./TagItem.vue";
import TagsContextMenu from "./TagsContextMenu.vue";
import { useTagsContextMenu } from "./useTagsContextMenu";
import { useTagsRouteSync } from "./useTagsRouteSync";

interface LegacyWheelEvent extends WheelEvent {
  wheelDelta?: number;
}

const router = useRouter();
const route = useRoute();

const tagsViewStore = useTagsViewStore();

const { visitedViews } = storeToRefs(tagsViewStore);

// 滚动条引用
const scrollbarRef = ref();

const {
  closeContextMenu,
  contextMenu,
  isFirstView,
  isLastView,
  openContextMenu,
  selectedTag,
  useContextMenuManager,
} = useTagsContextMenu(visitedViews);

const { updateCurrentTag, useRouteTagSync } = useTagsRouteSync(visitedViews);

/**
 * 处理中键点击
 */
const handleMiddleClick = (tag: TagView) => {
  if (!tag.affix) {
    closeSelectedTag(tag);
  }
};

/**
 * 跳转到标签对应路由
 */
const navigateToTag = (tag: TagView) => {
  router.push({
    path: tag.fullPath,
    query: tag.query,
  });
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

  const legacyWheelDelta = (event as LegacyWheelEvent).wheelDelta ?? 0;
  const deltaY = event.deltaY || -legacyWheelDelta;
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

  tagsViewStore.delView(tag).then((result) => {
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

  tagsViewStore.delLeftViews(selectedTag.value).then((result) => {
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

  tagsViewStore.delRightViews(selectedTag.value).then((result) => {
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
  tagsViewStore.delAllViews().then((result) => {
    tagsViewStore.toLastView(result.visitedViews, tag || undefined);
  });
};

// 启用右键菜单管理
useContextMenuManager();
useRouteTagSync();
</script>

<style lang="scss" scoped>
.tags-container {
  width: 100%;
  height: $tags-view-height;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.6);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);

  .scroll-container {
    white-space: nowrap;
  }
}

/* 深色模式适配 */
html.dark {
  .tags-container {
    background: rgba(30, 41, 59, 0.6);
    border-bottom-color: rgba(255, 255, 255, 0.05);
  }
}
</style>
