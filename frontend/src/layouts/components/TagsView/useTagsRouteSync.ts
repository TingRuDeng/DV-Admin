import { getRouteCacheKey } from "@/utils/view-cache";
import { usePermissionStore, useTagsViewStore } from "@/store";
import { extractAffixTags } from "./useAffixTags";

// 将当前路由转换为标签对象，确保新增和更新标签使用同一份字段规则。
function createRouteTag(route: ReturnType<typeof useRoute>): TagView | null {
  if (!route.meta?.title) {
    return null;
  }

  return {
    name: route.name as string,
    title: route.meta.title,
    path: route.path,
    fullPath: route.fullPath,
    cacheKey: getRouteCacheKey(route),
    affix: route.meta.affix || false,
    keepAlive: route.meta.keepAlive || false,
    query: route.query,
  };
}

// 管理 TagsView 与当前路由之间的同步，保持视图组件只负责交互编排。
export function useTagsRouteSync(visitedViews: Ref<TagView[]>) {
  const route = useRoute();
  const permissionStore = usePermissionStore();
  const tagsViewStore = useTagsViewStore();

  const routePathMap = computed(() => {
    const map = new Map<string, TagView>();
    visitedViews.value.forEach((tag) => {
      map.set(tag.path, tag);
    });
    return map;
  });

  // 初始化固定标签，固定标签来源于权限路由表。
  function initAffixTags() {
    const affixTags = extractAffixTags(permissionStore.routes);

    affixTags.forEach((tag) => {
      if (tag.name) {
        tagsViewStore.addVisitedView(tag);
      }
    });
  }

  // 当前路由具备标题时才加入标签栏。
  function addCurrentTag() {
    const currentTag = createRouteTag(route);
    if (currentTag) {
      tagsViewStore.addView(currentTag);
    }
  }

  // query/fullPath 变化时更新已有标签，避免同一路由不同参数展示陈旧。
  function updateCurrentTag() {
    nextTick(() => {
      const currentTag = routePathMap.value.get(route.path);
      const nextTag = createRouteTag(route);

      if (currentTag && nextTag && currentTag.fullPath !== route.fullPath) {
        tagsViewStore.updateVisitedView(nextTag);
      }
    });
  }

  // 注册路由监听和固定标签初始化副作用。
  function useRouteTagSync() {
    watch(
      route,
      () => {
        addCurrentTag();
        updateCurrentTag();
      },
      { immediate: true }
    );

    onMounted(() => {
      initAffixTags();
    });
  }

  return {
    updateCurrentTag,
    useRouteTagSync,
  };
}
