import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const DEMO_ICONS_SOURCE = readFileSync(resolve(process.cwd(), "src/views/demo/icons.vue"), "utf8");

describe("demo icons 类型治理", () => {
  it("图标代码生成函数不能回退到显式 any", () => {
    expect(DEMO_ICONS_SOURCE).not.toMatch(/generateIconCode\(symbol:\s*any\)/);
    expect(DEMO_ICONS_SOURCE).not.toMatch(/generateElementIconCode\(symbol:\s*any\)/);
  });
});
