import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const ICON_SELECT_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/IconSelect/index.vue"),
  "utf8"
);

describe("IconSelect 标签页事件类型治理", () => {
  it("标签页点击事件不能回退到显式 any", () => {
    expect(ICON_SELECT_SOURCE).not.toMatch(/handleTabClick\(tabPane:\s*any\)/);
  });

  it("标签页点击事件必须使用 Element Plus 事件上下文类型", () => {
    expect(ICON_SELECT_SOURCE).toContain("TabsPaneContext");
    expect(ICON_SELECT_SOURCE).toContain("TabPaneName");
  });
});
