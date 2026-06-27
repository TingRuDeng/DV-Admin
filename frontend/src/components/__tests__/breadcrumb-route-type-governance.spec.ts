import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const BREADCRUMB_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/Breadcrumb/index.vue"),
  "utf8"
);

describe("Breadcrumb 路由项类型治理", () => {
  it("面包屑路由项不能回退到显式 any", () => {
    expect(BREADCRUMB_SOURCE).not.toMatch(/\bas any\b/);
    expect(BREADCRUMB_SOURCE).not.toMatch(/handleLink\(item:\s*any\)/);
  });

  it("面包屑必须使用本地路由项类型表达实际字段", () => {
    expect(BREADCRUMB_SOURCE).toContain("type BreadcrumbRoute");
    expect(BREADCRUMB_SOURCE).toContain("DASHBOARD_BREADCRUMB");
  });
});
