import { createPinia, setActivePinia } from "pinia";
import type { RouteRecordRaw } from "vue-router";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AuthAPI, { type RouteVO } from "@/api/auth-api";
import router, { constantRoutes } from "@/router";
import { usePermissionStore } from "@/store/modules/permission-store";

vi.mock("@/api/auth-api", () => ({
  default: {
    getInfo: vi.fn(),
    getRoutes: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn(),
  },
}));

describe("usePermissionStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("generates dynamic routes and normalizes route meta", async () => {
    vi.mocked(AuthAPI.getRoutes).mockResolvedValue([
      {
        path: "/system",
        name: "System",
        component: "Layout",
        meta: {
          title: "系统管理",
          keepAlive: "1",
          hidden: "0",
          perms: "system:user:list,system:role:list",
        },
        children: [
          {
            path: "users",
            name: "UserManagement",
            component: "system/user/index",
            meta: {
              title: "用户管理",
              cacheByQuery: "true",
              cacheQueryKeys: "page,keyword",
            },
            children: [],
          },
        ],
      },
    ] as unknown as RouteVO[]);
    const permissionStore = usePermissionStore();

    const routes = await permissionStore.generateRoutes();

    expect(permissionStore.isRouteGenerated).toBe(true);
    expect(permissionStore.routes).toHaveLength(constantRoutes.length + 1);
    expect(routes[0].meta).toMatchObject({
      title: "系统管理",
      keepAlive: true,
      hidden: false,
      perms: ["system:user:list", "system:role:list"],
    });
    expect(routes[0].children?.[0].meta).toMatchObject({
      cacheByQuery: true,
      cacheQueryKeys: ["page", "keyword"],
    });
  });

  it("sets mix layout side menus from generated routes", () => {
    const permissionStore = usePermissionStore();
    const routes = [
      {
        path: "/system",
        name: "System",
        children: [{ path: "users", name: "UserManagement" }],
      },
    ] as RouteRecordRaw[];
    permissionStore.routes = [...constantRoutes, ...routes];

    permissionStore.setMixLayoutSideMenus("/system");

    expect(permissionStore.mixLayoutSideMenus).toEqual([{ path: "users", name: "UserManagement" }]);
  });

  it("removes dynamic route names when resetting router state", () => {
    const removeRouteSpy = vi.spyOn(router, "removeRoute").mockImplementation(() => {});
    const permissionStore = usePermissionStore();
    const dynamicRoutes = [
      { path: "/system", name: "System" },
      { path: "/audit", name: "Audit" },
    ] as RouteRecordRaw[];
    permissionStore.routes = [...constantRoutes, ...dynamicRoutes];
    permissionStore.isRouteGenerated = true;

    permissionStore.resetRouter();

    expect(removeRouteSpy).toHaveBeenCalledWith("System");
    expect(removeRouteSpy).toHaveBeenCalledWith("Audit");
    expect(permissionStore.routes).toEqual(constantRoutes);
    expect(permissionStore.isRouteGenerated).toBe(false);
  });
});
