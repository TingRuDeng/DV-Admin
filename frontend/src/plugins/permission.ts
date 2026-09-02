import type { RouteRecordRaw } from "vue-router";
import NProgress from "@/utils/nprogress";
import router from "@/router";
import { usePermissionStore, useUserStore } from "@/store";
import { hasRouteAccess } from "@/utils/route-access";
import { createLogger } from "@/utils/logger";

const permissionLogger = createLogger("permission");

export function setupPermission() {
  const whiteList = ["/login", "/401", "/403", "/404"];

  router.beforeEach(async (to) => {
    NProgress.start();

    try {
      const isLoggedIn = useUserStore().isLoggedIn();

      // 未登录处理
      if (!isLoggedIn) {
        if (whiteList.includes(to.path)) {
          return;
        }

        NProgress.done();
        return `/login?redirect=${encodeURIComponent(to.fullPath)}`;
      }

      // 已登录登录页重定向
      if (to.path === "/login") {
        return { path: "/" };
      }

      const permissionStore = usePermissionStore();
      const userStore = useUserStore();

      // 动态路由生成
      if (!permissionStore.isRouteGenerated) {
        if (!userStore.userInfo?.roles?.length) {
          await userStore.getUserInfo();
        }

        const dynamicRoutes = await permissionStore.generateRoutes();
        dynamicRoutes.forEach((route: RouteRecordRaw) => {
          router.addRoute(route);
        });

        return { ...to, replace: true };
      }

      // 路由404检查
      if (to.matched.length === 0) {
        return "/404";
      }

      // 路由级权限拦截：页面准入语义由 RouteMeta.perms/roles 决定
      const canAccessRoute = hasRouteAccess(to.matched, {
        userPerms: userStore.userInfo?.perms ?? [],
        userRoles: userStore.userInfo?.roles ?? [],
      });
      if (!canAccessRoute) {
        return "/403";
      }

      // 设置页面标题
      const title = (to.params.title as string) || (to.query.title as string);
      if (title) {
        to.meta.title = title;
      }
    } catch (error) {
      // 错误处理：重置状态并跳转登录
      permissionLogger.error("路由守卫异常:", error);
      await useUserStore().resetAllState();
      NProgress.done();
      return "/login";
    }
  });

  router.afterEach(() => {
    NProgress.done();
  });
}
