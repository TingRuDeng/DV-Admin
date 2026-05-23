import { appendCacheKeyWithLimit, getRouteCacheKey, getTagCacheKey } from "@/utils/view-cache";

export interface TagsViewChangeResult {
  visitedViews: TagView[];
  cachedViews?: string[];
}

function createChangeResult(visitedViews: TagView[], cachedViews: string[]): TagsViewChangeResult {
  return {
    visitedViews: [...visitedViews],
    cachedViews: [...cachedViews],
  };
}

export const useTagsViewStore = defineStore("tagsView", () => {
  const visitedViews = ref<TagView[]>([]);
  const cachedViews = ref<string[]>([]);
  const router = useRouter();
  const route = useRoute();

  function addVisitedView(view: TagView) {
    if (view.path.startsWith("/redirect")) {
      return;
    }
    if (visitedViews.value.some((v) => v.path === view.path)) {
      return;
    }
    if (view.affix) {
      visitedViews.value.unshift(view);
    } else {
      visitedViews.value.push(view);
    }
  }

  function addCachedView(view: TagView) {
    const cacheKey = getTagCacheKey(view);

    if (cachedViews.value.includes(cacheKey)) {
      return;
    }

    if (view.keepAlive && cacheKey) {
      cachedViews.value = appendCacheKeyWithLimit(cachedViews.value, cacheKey);
    }
  }

  function delVisitedView(view: TagView) {
    return new Promise<TagView[]>((resolve) => {
      for (const [i, v] of visitedViews.value.entries()) {
        if (v.path === view.path) {
          visitedViews.value.splice(i, 1);
          break;
        }
      }
      resolve([...visitedViews.value]);
    });
  }

  function delCachedView(view: TagView) {
    const cacheKey = getTagCacheKey(view);
    return new Promise<string[]>((resolve) => {
      const index = cachedViews.value.indexOf(cacheKey);
      if (index > -1) {
        cachedViews.value.splice(index, 1);
      }
      resolve([...cachedViews.value]);
    });
  }
  function delOtherVisitedViews(view: TagView) {
    return new Promise<TagView[]>((resolve) => {
      visitedViews.value = visitedViews.value.filter((v) => {
        return v?.affix || v.path === view.path;
      });
      resolve([...visitedViews.value]);
    });
  }

  function delOtherCachedViews(view: TagView) {
    const cacheKey = getTagCacheKey(view);
    return new Promise<string[]>((resolve) => {
      const index = cachedViews.value.indexOf(cacheKey);
      if (index > -1) {
        cachedViews.value = cachedViews.value.slice(index, index + 1);
      } else {
        // if index = -1, there is no cached tags
        cachedViews.value = [];
      }
      resolve([...cachedViews.value]);
    });
  }

  function removeCachedView(view: TagView) {
    const cacheIndex = cachedViews.value.indexOf(getTagCacheKey(view));
    if (cacheIndex > -1) {
      cachedViews.value.splice(cacheIndex, 1);
    }
  }

  function updateVisitedView(view: TagView) {
    const targetView = visitedViews.value.find((item) => item.path === view.path);
    if (!targetView) {
      return;
    }

    const previousCacheKey = getTagCacheKey(targetView);
    Object.assign(targetView, view);
    const nextCacheKey = getTagCacheKey(targetView);

    if (previousCacheKey !== nextCacheKey) {
      const previousIndex = cachedViews.value.indexOf(previousCacheKey);
      if (previousIndex > -1) {
        cachedViews.value.splice(previousIndex, 1);
      }
    }

    if (targetView.keepAlive && nextCacheKey && !cachedViews.value.includes(nextCacheKey)) {
      cachedViews.value = appendCacheKeyWithLimit(cachedViews.value, nextCacheKey);
      return;
    }

    if (!targetView.keepAlive) {
      const index = cachedViews.value.indexOf(nextCacheKey);
      if (index > -1) {
        cachedViews.value.splice(index, 1);
      }
    }
  }

  function updateTagName(fullPath: string, title: string) {
    const tag = visitedViews.value.find((tag: TagView) => tag.fullPath === fullPath);

    if (tag) {
      tag.title = title;
    }
  }

  function addView(view: TagView) {
    addVisitedView(view);
    addCachedView(view);
  }

  function delView(view: TagView) {
    return new Promise<TagsViewChangeResult>((resolve) => {
      delVisitedView(view);
      delCachedView(view);
      resolve(createChangeResult(visitedViews.value, cachedViews.value));
    });
  }

  function delOtherViews(view: TagView) {
    return new Promise<TagsViewChangeResult>((resolve) => {
      delOtherVisitedViews(view);
      delOtherCachedViews(view);
      resolve(createChangeResult(visitedViews.value, cachedViews.value));
    });
  }

  function delLeftViews(view: TagView) {
    return new Promise<TagsViewChangeResult>((resolve) => {
      const currIndex = visitedViews.value.findIndex((v) => v.path === view.path);
      if (currIndex === -1) {
        resolve(createChangeResult(visitedViews.value, cachedViews.value));
        return;
      }
      visitedViews.value = visitedViews.value.filter((item, index) => {
        if (index >= currIndex || item?.affix) {
          return true;
        }

        removeCachedView(item);
        return false;
      });
      resolve(createChangeResult(visitedViews.value, cachedViews.value));
    });
  }

  function delRightViews(view: TagView) {
    return new Promise<TagsViewChangeResult>((resolve) => {
      const currIndex = visitedViews.value.findIndex((v) => v.path === view.path);
      if (currIndex === -1) {
        resolve(createChangeResult(visitedViews.value, cachedViews.value));
        return;
      }
      visitedViews.value = visitedViews.value.filter((item, index) => {
        if (index <= currIndex || item?.affix) {
          return true;
        }
        removeCachedView(item);
        return false;
      });
      resolve(createChangeResult(visitedViews.value, cachedViews.value));
    });
  }

  function delAllViews() {
    return new Promise<TagsViewChangeResult>((resolve) => {
      const affixTags = visitedViews.value.filter((tag) => tag?.affix);
      visitedViews.value = affixTags;
      cachedViews.value = [];
      resolve(createChangeResult(visitedViews.value, cachedViews.value));
    });
  }

  function delAllVisitedViews() {
    return new Promise<TagView[]>((resolve) => {
      const affixTags = visitedViews.value.filter((tag) => tag?.affix);
      visitedViews.value = affixTags;
      resolve([...visitedViews.value]);
    });
  }

  function delAllCachedViews() {
    return new Promise<string[]>((resolve) => {
      cachedViews.value = [];
      resolve([...cachedViews.value]);
    });
  }

  function closeCurrentView() {
    const tags: TagView = {
      name: route.name as string,
      title: route.meta.title as string,
      path: route.path,
      fullPath: route.fullPath,
      cacheKey: getRouteCacheKey(route),
      affix: route.meta?.affix,
      keepAlive: route.meta?.keepAlive,
      query: route.query,
    };
    delView(tags).then((res) => {
      if (isActive(tags)) {
        toLastView(res.visitedViews, tags);
      }
    });
  }

  function isActive(tag: TagView) {
    return tag.path === route.path;
  }

  function toLastView(visitedViews: TagView[], view?: TagView) {
    const latestView = visitedViews.slice(-1)[0];
    if (latestView && latestView.fullPath) {
      router.push(latestView.fullPath);
    } else {
      // now the default is to redirect to the home page if there is no tags-view,
      // you can adjust it according to your needs.
      if (view?.name === "Dashboard") {
        // to reload home page
        router.replace("/redirect" + view.fullPath);
      } else {
        router.push("/");
      }
    }
  }

  return {
    visitedViews,
    cachedViews,
    addVisitedView,
    addCachedView,
    delVisitedView,
    delCachedView,
    delOtherVisitedViews,
    delOtherCachedViews,
    updateVisitedView,
    addView,
    delView,
    delOtherViews,
    delLeftViews,
    delRightViews,
    delAllViews,
    delAllVisitedViews,
    delAllCachedViews,
    closeCurrentView,
    isActive,
    toLastView,
    updateTagName,
  };
});
