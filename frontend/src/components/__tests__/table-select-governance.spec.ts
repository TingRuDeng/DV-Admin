import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const componentRoot = resolve(__dirname, "../TableSelect");

function readTableSelectFile(fileName: string) {
  return readFileSync(resolve(componentRoot, fileName), "utf-8");
}

describe("table select governance", () => {
  it("keeps the root component focused on orchestration", () => {
    const source = readTableSelectFile("index.vue");

    expect(source).toContain("TableSelectSearchForm");
    expect(source).toContain("TableSelectDataTable");
    expect(source).toContain("TableSelectFooter");
    expect(source).not.toContain("<el-form");
    expect(source).not.toContain("<el-table");
    expect(source).not.toContain("export interface ISelectConfig");
  });

  it("keeps shared table select types free of explicit any", () => {
    const source = readTableSelectFile("types.ts");

    expect(source).not.toMatch(/\bany\b/);
    expect(source).toContain("unknown");
    expect(source).toContain("TableSelectConfig");
  });
});
