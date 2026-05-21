import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useTagsViewStore } from "@/store/modules/tags-view-store";

const routerMocks = vi.hoisted(() => ({
  push: vi.fn(),
  replace: vi.fn(),
  route: {
    name: "Dashboard",
    title: "首页",
    path: "/dashboard",
    fullPath: "/dashboard",
    meta: {
      title: "首页",
      affix: true,
      keepAlive: true,
    },
    query: {},
  },
}));

describe("useTagsViewStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    Object.assign(globalThis, {
      useRoute: () => routerMocks.route,
      useRouter: () => ({
        push: routerMocks.push,
        replace: routerMocks.replace,
      }),
    });
  });

  it("adds visited views and cache keys once", () => {
    const tagsViewStore = useTagsViewStore();
    const view = {
      name: "UserManagement",
      title: "用户管理",
      path: "/system/users",
      fullPath: "/system/users?page=1",
      cacheKey: "system-users",
      keepAlive: true,
    };

    tagsViewStore.addView(view);
    tagsViewStore.addView(view);

    expect(tagsViewStore.visitedViews).toEqual([view]);
    expect(tagsViewStore.cachedViews).toEqual(["system-users"]);
  });

  it("updates cache key when a visited view changes", () => {
    const tagsViewStore = useTagsViewStore();
    tagsViewStore.addView({
      name: "UserManagement",
      title: "用户管理",
      path: "/system/users",
      fullPath: "/system/users?page=1",
      cacheKey: "system-users-page-1",
      keepAlive: true,
    });

    tagsViewStore.updateVisitedView({
      name: "UserManagement",
      title: "用户管理",
      path: "/system/users",
      fullPath: "/system/users?page=2",
      cacheKey: "system-users-page-2",
      keepAlive: true,
    });

    expect(tagsViewStore.cachedViews).toEqual(["system-users-page-2"]);
  });

  it("deletes current and other views while preserving affix tags", async () => {
    const tagsViewStore = useTagsViewStore();
    const dashboard = {
      name: "Dashboard",
      title: "首页",
      path: "/dashboard",
      fullPath: "/dashboard",
      affix: true,
      keepAlive: true,
    };
    const users = {
      name: "UserManagement",
      title: "用户管理",
      path: "/system/users",
      fullPath: "/system/users",
      cacheKey: "system-users",
      keepAlive: true,
    };
    const roles = {
      name: "RoleManagement",
      title: "角色管理",
      path: "/system/roles",
      fullPath: "/system/roles",
      cacheKey: "system-roles",
      keepAlive: true,
    };
    tagsViewStore.addView(dashboard);
    tagsViewStore.addView(users);
    tagsViewStore.addView(roles);

    await tagsViewStore.delOtherViews(users);

    expect(tagsViewStore.visitedViews.map((item) => item.name)).toEqual([
      "Dashboard",
      "UserManagement",
    ]);
    expect(tagsViewStore.cachedViews).toEqual(["system-users"]);

    const result = await tagsViewStore.delView(users);
    expect(result.visitedViews.map((item) => item.name)).toEqual(["Dashboard"]);
    expect(result.cachedViews).toEqual([]);
  });
});
