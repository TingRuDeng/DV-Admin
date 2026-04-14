import { describe, expect, it } from "vitest";
import { normalizeRouteMeta } from "@/utils/route-meta";

describe("normalizeRouteMeta", () => {
  it("normalizes booleans, fallback title, and string arrays", () => {
    const meta = normalizeRouteMeta(
      {
        hidden: 1,
        alwaysShow: "true",
        affix: "1",
        keepAlive: 0,
        breadcrumb: undefined,
        activeMenu: "/system/user",
        cacheKey: "SystemUserList",
        cacheByQuery: "1",
        cacheQueryKeys: "tab,mode",
        permissions: "system:users:list,system:users:view",
        roles: ["admin"],
      },
      { routeName: "UserList" }
    );

    expect(meta.title).toBe("UserList");
    expect(meta.hidden).toBe(true);
    expect(meta.alwaysShow).toBe(true);
    expect(meta.affix).toBe(true);
    expect(meta.keepAlive).toBe(false);
    expect(meta.breadcrumb).toBe(true);
    expect(meta.activeMenu).toBe("/system/user");
    expect(meta.cacheKey).toBe("SystemUserList");
    expect(meta.cacheByQuery).toBe(true);
    expect(meta.cacheQueryKeys).toEqual(["tab", "mode"]);
    expect(meta.perms).toEqual(["system:users:list", "system:users:view"]);
    expect(meta.roles).toEqual(["admin"]);
  });

  it("preserves explicit values and unknown meta fields", () => {
    const params = { id: 1 };
    const meta = normalizeRouteMeta({
      title: "用户管理",
      icon: "user",
      hidden: false,
      alwaysShow: false,
      affix: false,
      keepAlive: true,
      breadcrumb: false,
      layout: "mix",
      params,
    });

    expect(meta.title).toBe("用户管理");
    expect(meta.icon).toBe("user");
    expect(meta.hidden).toBe(false);
    expect(meta.alwaysShow).toBe(false);
    expect(meta.affix).toBe(false);
    expect(meta.keepAlive).toBe(true);
    expect(meta.breadcrumb).toBe(false);
    expect(meta.layout).toBe("mix");
    expect(meta.params).toBe(params);
  });
});
