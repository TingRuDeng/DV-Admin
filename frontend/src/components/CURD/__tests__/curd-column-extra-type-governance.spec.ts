import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const TYPES_SOURCE = readFileSync(resolve(__dirname, "../types.ts"), "utf8");

describe("CURD 表格列扩展类型治理", () => {
  it("keeps table column extension index away from explicit any", () => {
    expect(TYPES_SOURCE).not.toMatch(/\[key: string\]: any/);
    expect(TYPES_SOURCE).toMatch(/export type ICurdTableColumnExtraValue = unknown/);
    expect(TYPES_SOURCE).toMatch(/\[key: string\]: ICurdTableColumnExtraValue/);
  });
});
