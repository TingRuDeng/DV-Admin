import type { RouteRecordRaw } from "vue-router";
import { normalizeAppIconName } from "@/components/AppIcon/icon-map";
import { isExternal } from "@/utils";
import { translateRouteTitle } from "@/utils/i18n";
import type { DashboardQuickAction } from "./components/DashboardQuickActions.vue";

function joinRoutePath(parentPath: string, path: string) {
  if (isExternal(path) || path.startsWith("/")) return path;

  if (isExternal(parentPath)) {
    return `${parentPath.replace(/\/$/, "")}/${path}`;
  }

  const joined = `${parentPath}/${path}`.replace(/\/+/g, "/");
  return joined.startsWith("/") ? joined : `/${joined}`;
}

export function collectDashboardActions(
  routeRecords: RouteRecordRaw[],
  parentPath = ""
): DashboardQuickAction[] {
  const result: DashboardQuickAction[] = [];

  routeRecords.forEach((route) => {
    const meta = route.meta ?? {};
    if (meta.hidden) return;

    const fullPath = joinRoutePath(parentPath, route.path);
    const children = route.children ?? [];

    if (children.length > 0) {
      result.push(...collectDashboardActions(children, fullPath));
      return;
    }

    if (fullPath === "/dashboard" || !meta.title) return;

    result.push({
      title: translateRouteTitle(String(meta.title)) ?? String(meta.title),
      path: fullPath,
      icon: typeof meta.icon === "string" ? normalizeAppIconName(meta.icon) : "menu",
    });
  });

  return result;
}
