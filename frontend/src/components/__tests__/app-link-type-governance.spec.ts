import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const APP_LINK_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/AppLink/index.vue"),
  "utf8"
);

describe("AppLink 跳转目标类型治理", () => {
  it("跳转目标构建不能回退到显式 any", () => {
    expect(APP_LINK_SOURCE).not.toMatch(/\bto:\s*any\b/);
    expect(APP_LINK_SOURCE).not.toMatch(/linkProps\s*=\s*\(to:\s*any\)/);
  });

  it("跳转目标必须显式表达当前支持的路径对象结构", () => {
    expect(APP_LINK_SOURCE).toContain("interface AppLinkTo");
    expect(APP_LINK_SOURCE).toContain("path: string;");
    expect(APP_LINK_SOURCE).toContain("query?: LocationQueryRaw;");
  });
});
