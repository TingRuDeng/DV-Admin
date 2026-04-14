import { describe, expect, it } from "vitest";
import { getRouteCacheKey, getRouteRenderKey, getTagCacheKey } from "@/utils/view-cache";

describe("view-cache utils", () => {
  it("prefers explicit meta.cacheKey for keep-alive routes", () => {
    const route = {
      name: "UserList",
      path: "/system/user",
      fullPath: "/system/user?page=2",
      query: { page: "2" },
      meta: {
        keepAlive: true,
        cacheKey: "SystemUserList",
      },
    };

    expect(getRouteCacheKey(route)).toBe("SystemUserList");
    expect(getRouteRenderKey(route)).toBe("SystemUserList");
  });

  it("falls back to route name for query-only keep-alive routes", () => {
    const route = {
      name: "Dashboard",
      path: "/dashboard",
      fullPath: "/dashboard?tab=analytics",
      query: { tab: "analytics" },
      meta: {
        keepAlive: true,
      },
    };

    expect(getRouteCacheKey(route)).toBe("Dashboard");
    expect(getRouteRenderKey(route)).toBe("Dashboard");
  });

  it("falls back to fullPath for dynamic-params keep-alive routes without explicit cacheKey", () => {
    const route = {
      name: "DemoDetail",
      path: "/detail/1",
      fullPath: "/detail/1",
      params: { id: "1" },
      meta: {
        keepAlive: true,
      },
    };

    expect(getRouteCacheKey(route)).toBe("/detail/1");
    expect(getRouteRenderKey(route)).toBe("/detail/1");
  });

  it("supports explicit query-dimension cache with cacheByQuery", () => {
    const route = {
      name: "SystemNotice",
      path: "/system/notice",
      fullPath: "/system/notice?status=1&page=2",
      query: {
        page: "2",
        status: "1",
      },
      meta: {
        keepAlive: true,
        cacheByQuery: true,
      },
    };

    expect(getRouteCacheKey(route)).toBe("SystemNotice::page=2&status=1");
    expect(getRouteRenderKey(route)).toBe("SystemNotice::page=2&status=1");
  });

  it("supports scoped query-dimension cache with cacheQueryKeys", () => {
    const route = {
      name: "SystemNotice",
      path: "/system/notice",
      fullPath: "/system/notice?status=1&page=2&tab=todo",
      query: {
        page: "2",
        status: "1",
        tab: "todo",
      },
      meta: {
        keepAlive: true,
        cacheQueryKeys: ["status", "tab"],
      },
    };

    expect(getRouteCacheKey(route)).toBe("SystemNotice::status=1&tab=todo");
    expect(getRouteRenderKey(route)).toBe("SystemNotice::status=1&tab=todo");
  });

  it("keeps non-cached routes keyed by fullPath", () => {
    const route = {
      name: "Profile",
      path: "/profile",
      fullPath: "/profile?tab=security",
      query: { tab: "security" },
      meta: {
        keepAlive: false,
      },
    };

    expect(getRouteRenderKey(route)).toBe("/profile?tab=security");
  });

  it("derives tag cache key from cacheKey first, then route name", () => {
    expect(
      getTagCacheKey({
        name: "RoleList",
        path: "/system/role",
        fullPath: "/system/role?page=3",
        cacheKey: "SystemRoleList",
      })
    ).toBe("SystemRoleList");

    expect(
      getTagCacheKey({
        name: "RoleList",
        path: "/system/role",
        fullPath: "/system/role?page=3",
      })
    ).toBe("RoleList");
  });
});
