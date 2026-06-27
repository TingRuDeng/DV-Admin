import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const INPUT_TAG_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/InputTag/index.vue"),
  "utf8"
);

describe("InputTag 配置属性类型治理", () => {
  it("配置属性不能使用显式 any", () => {
    expect(INPUT_TAG_SOURCE).not.toMatch(/Record<string,\s*any>/);
    expect(INPUT_TAG_SOURCE).not.toMatch(/\bas any\b/);
  });

  it("配置属性使用 Element Plus 组件 props 类型", () => {
    expect(INPUT_TAG_SOURCE).toMatch(/ButtonProps/);
    expect(INPUT_TAG_SOURCE).toMatch(/InputProps/);
    expect(INPUT_TAG_SOURCE).toMatch(/TagProps/);
  });
});
