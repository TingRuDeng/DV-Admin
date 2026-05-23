import type { RouteRecordRaw } from "vue-router";
import { isExternal } from "@/utils";
import type { SearchItem } from "./types";

const EXCLUDED_ROUTES = ["/redirect", "/login", "/401", "/404"];

function joinRoutePath(parentPath: string, routePath: string) {
  if (routePath.startsWith("/")) return routePath;
  return `${parentPath}${parentPath.endsWith("/") ? "" : "/"}${routePath}`;
}

function cloneRouteParams(route: RouteRecordRaw) {
  if (!route.meta?.params) return undefined;
  return JSON.parse(JSON.stringify(toRaw(route.meta.params)));
}

function createSearchItem(route: RouteRecordRaw, path: string): SearchItem | null {
  if (!route.meta?.title) return null;

  const title = route.meta.title === "dashboard" ? "首页" : route.meta.title;
  return {
    title,
    path,
    name: typeof route.name === "string" ? route.name : undefined,
    icon: route.meta.icon,
    redirect: typeof route.redirect === "string" ? route.redirect : undefined,
    params: cloneRouteParams(route),
  };
}

export function buildMenuSearchItems(
  routes: RouteRecordRaw[],
  options: { excludedRoutes?: string[]; parentPath?: string } = {}
): SearchItem[] {
  const { excludedRoutes = EXCLUDED_ROUTES, parentPath = "" } = options;

  return routes.flatMap((route) => {
    const path = joinRoutePath(parentPath, route.path);
    if (excludedRoutes.includes(route.path) || isExternal(route.path)) return [];

    if (route.children?.length) {
      return buildMenuSearchItems(route.children, {
        excludedRoutes,
        parentPath: path,
      });
    }

    const item = createSearchItem(route, path);
    return item ? [item] : [];
  });
}
