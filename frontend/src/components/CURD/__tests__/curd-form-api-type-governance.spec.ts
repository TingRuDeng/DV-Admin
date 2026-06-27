import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const CURD_ROOT = resolve(__dirname, "..");
const TYPES_SOURCE = readFileSync(resolve(CURD_ROOT, "types.ts"), "utf8");
const PAGE_MODAL_SOURCE = readFileSync(resolve(CURD_ROOT, "PageModal.vue"), "utf8");

describe("CURD 表单 API 类型治理", () => {
  it("keeps modal slots and exposed setters away from explicit any", () => {
    expect(PAGE_MODAL_SOURCE).not.toMatch(
      /defineSlots<\{ \[key: string\]: \(_args: any\) => any \}>/
    );
    expect(PAGE_MODAL_SOURCE).not.toMatch(/setFormItemData:\s*\(key: string, value: any\)/);
  });

  it("keeps form item API fields away from explicit any", () => {
    const forbiddenPatterns = [
      /options\?: Array<\{ label: string; value: any; \[key: string\]: any \}>/,
      /Ref<any\[]>/,
      /initialValue\?: any/,
      /events\?: Record<string, \(\.\.\.args: any\) => void>/,
    ];

    const offenders = forbiddenPatterns.filter((pattern) => pattern.test(TYPES_SOURCE));

    expect(
      offenders,
      `发现 CURD 表单 API 重新引入 any:\n${offenders.map((pattern) => pattern.source).join("\n")}`
    ).toEqual([]);
  });
});
