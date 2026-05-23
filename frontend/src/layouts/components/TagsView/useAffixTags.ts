import { resolve } from "path-browserify";
import type { RouteRecordRaw } from "vue-router";
import { getRouteCacheKey } from "@/utils/view-cache";

export function extractAffixTags(routes: RouteRecordRaw[], basePath = "/"): TagView[] {
  const affixTags: TagView[] = [];

  function traverse(routeList: RouteRecordRaw[], currentBasePath: string) {
    routeList.forEach((route) => {
      const fullPath = resolve(currentBasePath, route.path);

      if (route.meta?.affix) {
        affixTags.push({
          path: fullPath,
          fullPath,
          name: String(route.name || ""),
          title: route.meta.title || "no-name",
          cacheKey: getRouteCacheKey({
            name: route.name,
            path: fullPath,
            fullPath,
            meta: route.meta,
          }),
          affix: true,
          keepAlive: route.meta.keepAlive || false,
        });
      }

      if (route.children?.length) {
        traverse(route.children, fullPath);
      }
    });
  }

  traverse(routes, basePath);
  return affixTags;
}
