import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { RouteLocationNormalizedLoaded } from "vue-router";
import { describe, expect, it } from "vitest";
import {
  getActiveLeftMenuPath,
  getMixTopMenuPath,
  resolveMixSideMenuPath,
} from "../useMixLayoutState";

type MixLayoutRoute = Pick<RouteLocationNormalizedLoaded, "meta" | "path">;

function createRoute(route: MixLayoutRoute) {
  return route;
}

describe("useMixLayoutState", () => {
  it("extracts top menu path from nested route paths", () => {
    expect(getMixTopMenuPath("/system/user")).toBe("/system");
    expect(getMixTopMenuPath("/dashboard")).toBe("/");
    expect(getMixTopMenuPath("/")).toBe("/");
  });

  it("resolves side menu paths with active top menu path", () => {
    expect(resolveMixSideMenuPath("/user", "/system")).toBe("/system/user");
    expect(resolveMixSideMenuPath("role", "/system")).toBe("/system/role");
    expect(resolveMixSideMenuPath("https://example.com", "/system")).toBe("https://example.com");
  });

  it("uses route meta activeMenu before current path", () => {
    expect(
      getActiveLeftMenuPath(
        createRoute({
          path: "/system/user/detail",
          meta: { activeMenu: "/system/user" },
        })
      )
    ).toBe("/system/user");

    expect(
      getActiveLeftMenuPath(
        createRoute({
          path: "/system/user",
          meta: {},
        })
      )
    ).toBe("/system/user");
  });

  it("keeps mix layout index as a composition surface", () => {
    const source = readFileSync(resolve(process.cwd(), "src/layouts/modes/mix/index.vue"), "utf8");

    expect(source).toContain("useMixLayoutState");
    expect(source).not.toContain("useAppStore");
    expect(source).not.toContain("usePermissionStore");
    expect(source).not.toContain("watch(");
  });

  it("keeps mix layout index below the file size hard limit", () => {
    const source = readFileSync(resolve(process.cwd(), "src/layouts/modes/mix/index.vue"), "utf8");

    expect(source.split("\n").length).toBeLessThan(300);
  });
});
