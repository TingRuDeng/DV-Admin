import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const OPERATION_COLUMN_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/OperationColumn/index.vue"),
  "utf8"
);

describe("OperationColumn 类型治理", () => {
  it("DOM 宽度测量不能回退到显式 any", () => {
    expect(OPERATION_COLUMN_SOURCE).not.toMatch(/totalWidth:\s*any/);
    expect(OPERATION_COLUMN_SOURCE).not.toMatch(/button:\s*any/);
    expect(OPERATION_COLUMN_SOURCE).toContain('querySelectorAll<HTMLElement>(".el-button")');
  });
});
