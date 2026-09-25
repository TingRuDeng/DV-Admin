import type { RouteLocationNormalizedLoaded, RouteRecordRaw } from "vue-router";
import { isExternal } from "@/utils/index";
import { useAppStore, usePermissionStore } from "@/store";

const MOBILE_LOGO_COLLAPSE_WIDTH = 768;

type MixLayoutRoute = Pick<RouteLocationNormalizedLoaded, "meta" | "path">;

interface UseMixLayoutStateOptions {
  route: MixLayoutRoute;
  activeTopMenuPath: Ref<string>;
  viewportWidth: Ref<number>;
  isMobile: Ref<boolean>;
  routes: Ref<RouteRecordRaw[]>;
  sideMenuRoutes: Ref<RouteRecordRaw[]>;
}

export function getActiveLeftMenuPath(route: MixLayoutRoute) {
  const { meta, path } = route;

  if (typeof meta?.activeMenu === "string") {
    return meta.activeMenu;
  }

  return path;
}

export function getMixTopMenuPath(routePath: string) {
  const pathSegments = routePath.split("/").filter(Boolean);
  return pathSegments.length > 1 ? routePath.match(/^\/[^/]+/)?.[0] || "/" : "/";
}

export function resolveMixSideMenuPath(routePath: string, activeTopMenuPath: string) {
  if (isExternal(routePath)) {
    return routePath;
  }

  if (routePath.startsWith("/")) {
    return activeTopMenuPath + routePath;
  }

  return `${activeTopMenuPath}/${routePath}`;
}

// 完整菜单树的一级路由已是绝对路径，不能再拼接顶部菜单前缀。
export function resolveMixSidebarItemPath(
  routePath: string,
  activeTopMenuPath: string,
  isFullTree: boolean
) {
  return isFullTree ? routePath : resolveMixSideMenuPath(routePath, activeTopMenuPath);
}

export function useMixLayoutState({
  route,
  activeTopMenuPath,
  viewportWidth,
  isMobile,
  routes,
  sideMenuRoutes,
}: UseMixLayoutStateOptions) {
  const appStore = useAppStore();
  const permissionStore = usePermissionStore();

  // 移动端只展示 Logo 图标，减少顶部菜单横向挤压。
  const isLogoCollapsed = computed(() => viewportWidth.value < MOBILE_LOGO_COLLAPSE_WIDTH);
  const activeLeftMenuPath = computed(() => getActiveLeftMenuPath(route));

  // 移动端隐藏顶部菜单，侧栏抽屉改为完整菜单树，否则无法切换一级菜单。
  const sidebarMenuRoutes = computed(() => (isMobile.value ? routes.value : sideMenuRoutes.value));

  function resolvePath(routePath: string) {
    return resolveMixSidebarItemPath(routePath, activeTopMenuPath.value, isMobile.value);
  }

  // TagsView 切换可能绕过顶部菜单点击，需要把顶部菜单和左侧菜单同步到当前路由。
  function syncMixMenusByRoutePath(routePath: string) {
    if (routePath.startsWith(activeTopMenuPath.value)) {
      return;
    }

    const topMenuPath = getMixTopMenuPath(routePath);
    if (topMenuPath === activeTopMenuPath.value) {
      return;
    }

    appStore.activeTopMenu(topMenuPath);
    permissionStore.setMixLayoutSideMenus(topMenuPath);
  }

  watch(() => route.path, syncMixMenusByRoutePath, { immediate: true });

  return {
    activeLeftMenuPath,
    isLogoCollapsed,
    sidebarMenuRoutes,
    resolvePath,
  };
}
