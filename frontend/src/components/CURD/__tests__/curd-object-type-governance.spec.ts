import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const CURD_ROOT = resolve(__dirname, "..");
const TYPES_SOURCE = readFileSync(resolve(CURD_ROOT, "types.ts"), "utf8");

describe("CURD 通用对象类型治理", () => {
  it("共享对象值类型不能回退到显式 any", () => {
    expect(TYPES_SOURCE).not.toMatch(/IObject\s*=\s*Record<string,\s*any>/);
    expect(TYPES_SOURCE).toMatch(/IObject\s*=\s*Record<string,\s*unknown>/);
  });
});
