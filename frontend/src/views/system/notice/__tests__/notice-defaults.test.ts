import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const NOTICE_FORM_SOURCE = resolve(
  process.cwd(),
  "src/views/system/notice/components/NoticeFormDrawer.vue"
);

describe("notice form defaults", () => {
  it("keeps create dialog defaults aligned with radio values", () => {
    const source = readFileSync(NOTICE_FORM_SOURCE, "utf8");

    expect(source).toContain("targetType: 1");
    expect(source).toContain('level: "L"');
    expect(source).not.toContain("Object.assign(formData, { level: 0, targetType: 0");
  });
});
