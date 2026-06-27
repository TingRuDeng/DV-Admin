import { appendCacheKeyWithLimit, getTagCacheKey } from "@/utils/view-cache";
import type { TagsViewChangeResult } from "./tags-view-store";

export function createTagsViewChangeResult(
  visitedViews: TagView[],
  cachedViews: string[]
): TagsViewChangeResult {
  return {
    visitedViews: [...visitedViews],
    cachedViews: [...cachedViews],
  };
}

export function appendCachedTagView(cachedViews: string[], view: TagView) {
  const cacheKey = getTagCacheKey(view);

  if (!view.keepAlive || !cacheKey || cachedViews.includes(cacheKey)) {
    return cachedViews;
  }

  return appendCacheKeyWithLimit(cachedViews, cacheKey);
}

export function removeCachedTagView(cachedViews: string[], view: TagView) {
  const cacheKey = getTagCacheKey(view);
  return cachedViews.filter((item) => item !== cacheKey);
}

export function keepOnlyCachedTagView(cachedViews: string[], view: TagView) {
  const cacheKey = getTagCacheKey(view);
  return cachedViews.includes(cacheKey) ? [cacheKey] : [];
}

export function syncUpdatedCachedTagView(
  cachedViews: string[],
  previousView: TagView,
  nextView: TagView
) {
  const previousCacheKey = getTagCacheKey(previousView);
  const nextCacheKey = getTagCacheKey(nextView);
  const withoutPrevious =
    previousCacheKey === nextCacheKey
      ? cachedViews
      : cachedViews.filter((item) => item !== previousCacheKey);

  if (!nextView.keepAlive) {
    return withoutPrevious.filter((item) => item !== nextCacheKey);
  }

  if (!nextCacheKey || withoutPrevious.includes(nextCacheKey)) {
    return withoutPrevious;
  }

  return appendCacheKeyWithLimit(withoutPrevious, nextCacheKey);
}
