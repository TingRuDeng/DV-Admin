import type { RouteRecordRaw } from "vue-router";
import { describe, expect, it } from "vitest";
import { hasSubMenus } from "../../../components/Menu/useTopMenuNavigation";

const route = (children: Array<Partial<RouteRecordRaw>>, meta: RouteRecordRaw["meta"] = {}) =>
  ({ path: "/system", meta, children }) as RouteRecordRaw;

describe("double column layout", () => {
  it("shows the second column only when a top menu has several visible children", () => {
    expect(hasSubMenus(route([{ path: "users" }, { path: "roles" }]))).toBe(true);
    expect(hasSubMenus(route([{ path: "dashboard" }]))).toBe(false);
    expect(
      hasSubMenus(route([{ path: "dashboard" }, { path: "401", meta: { hidden: true } }]))
    ).toBe(false);
    expect(hasSubMenus(route([]))).toBe(false);
  });

  it("keeps a single-child top menu as a column when alwaysShow is set", () => {
    expect(hasSubMenus(route([{ path: "dashboard" }], { alwaysShow: true }))).toBe(true);
  });
});
