import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const NOTICE_SOURCE = resolve(process.cwd(), "src/views/system/notice/index.vue");

describe("notice form defaults", () => {
  it("keeps create dialog defaults aligned with radio values", () => {
    const source = readFileSync(NOTICE_SOURCE, "utf8");

    expect(source).toContain("targetType: 1, // 默认目标类型为全体");
    expect(source).toContain('Object.assign(formData, { level: "L", targetType: 1');
    expect(source).not.toContain("Object.assign(formData, { level: 0, targetType: 0");
  });
});
