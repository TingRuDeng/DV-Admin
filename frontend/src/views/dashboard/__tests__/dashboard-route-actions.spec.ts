import { describe, expect, it } from "vitest";
import type { RouteRecordRaw } from "vue-router";
import { collectDashboardActions } from "../dashboard-route-actions";

describe("dashboard route actions", () => {
  it("counts visible leaf routes beyond the displayed shortcut limit", () => {
    const routes = Array.from({ length: 9 }, (_, index) => ({
      path: `item-${index}`,
      meta: { title: `item-${index}` },
    })) as RouteRecordRaw[];

    const actions = collectDashboardActions(routes);

    expect(actions).toHaveLength(9);
  });

  it("skips hidden branches and preserves absolute or external paths", () => {
    const routes = [
      {
        path: "hidden",
        meta: { hidden: true },
        children: [{ path: "child", meta: { title: "Hidden child" } }],
      },
      { path: "/absolute", meta: { title: "Absolute" } },
      { path: "https://example.com", meta: { title: "External" } },
      {
        path: "https://docs.example.com/",
        children: [{ path: "guide", meta: { title: "Guide" } }],
      },
    ] as RouteRecordRaw[];

    expect(collectDashboardActions(routes).map((item) => item.path)).toEqual([
      "/absolute",
      "https://example.com",
      "https://docs.example.com/guide",
    ]);
  });
});
