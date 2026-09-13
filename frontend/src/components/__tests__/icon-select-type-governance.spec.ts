import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const ICON_SELECT_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/IconSelect/index.vue"),
  "utf8"
);

describe("IconSelect 图标来源治理", () => {
  it("只通过 AppIcon 渲染 Lucide 图标", () => {
    expect(ICON_SELECT_SOURCE).toContain("APP_ICON_NAMES");
    expect(ICON_SELECT_SOURCE).toContain("<AppIcon");
    expect(ICON_SELECT_SOURCE).not.toContain("@element-plus/icons-vue");
    expect(ICON_SELECT_SOURCE).not.toContain("i-svg:");
  });
});
