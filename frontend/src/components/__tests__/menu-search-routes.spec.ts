import type { RouteRecordRaw } from "vue-router";
import { describe, expect, it } from "vitest";
import { buildMenuSearchItems } from "@/components/MenuSearch/menu-search-routes";

const view = () => Promise.resolve({});

const routes: RouteRecordRaw[] = [
  { path: "/login", component: view, meta: { title: "登录" } },
  {
    path: "/",
    component: view,
    children: [
      { path: "dashboard", component: view, name: "Dashboard", meta: { title: "dashboard" } },
      { path: "profile", component: view, meta: { title: "个人中心", hidden: true } },
      { path: "my-notice", component: view, meta: { title: "我的通知", hidden: true } },
      // 没有 hidden 也要跳过：带参数的路由没法直接跳转
      { path: "/detail/:id(\\d+)", component: view, meta: { title: "详情页缓存" } },
    ],
  },
  {
    path: "/system",
    component: view,
    meta: { title: "系统管理" },
    children: [
      { path: "users", component: view, meta: { title: "用户管理", icon: "user" } },
      {
        path: "roles",
        component: view,
        meta: { title: "角色管理", params: { tab: "list" } },
      },
      { path: "https://example.com", component: view, meta: { title: "外部文档" } },
    ],
  },
  {
    path: "/archive",
    component: view,
    meta: { title: "归档", hidden: true },
    children: [{ path: "logs", component: view, meta: { title: "归档日志" } }],
  },
  {
    path: "/tenant/:tenantId",
    component: view,
    children: [{ path: "members", component: view, meta: { title: "租户成员" } }],
  },
];

describe("buildMenuSearchItems", () => {
  it("只收录可直接跳转的可见菜单", () => {
    const items = buildMenuSearchItems(routes);

    expect(items.map((item) => item.path)).toEqual([
      "/dashboard",
      "/system/users",
      "/system/roles",
    ]);
    expect(items.map((item) => item.title)).toEqual(["首页", "用户管理", "角色管理"]);
  });

  it("跳过隐藏路由及其子路由", () => {
    const titles = buildMenuSearchItems(routes).map((item) => item.title);

    expect(titles).not.toContain("个人中心");
    expect(titles).not.toContain("我的通知");
    expect(titles).not.toContain("归档日志");
  });

  it("跳过带参数的路由及其子路由", () => {
    const paths = buildMenuSearchItems(routes).map((item) => item.path);

    expect(paths.some((path) => path.includes(":"))).toBe(false);
  });

  it("复制路由参数，跳转时不共享路由表里的对象", () => {
    const roles = buildMenuSearchItems(routes).find((item) => item.path === "/system/roles");

    expect(roles?.params).toEqual({ tab: "list" });
    expect(roles?.params).not.toBe(routes[2].children?.[1].meta?.params);
  });
});
