import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("dict sync demo component split", () => {
  it("keeps dict sync demo page focused on orchestration", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/demo/dict-sync.vue"), "utf8");

    expect(source).toContain("<DictItemEditorCard");
    expect(source).toContain("<DictPreviewCard");
    expect(source).toContain("<DictCacheCard");
    expect(source).not.toContain("<el-form :model=");
    expect(source).not.toContain("<pre");
    expect(source).not.toContain(".dict-card");
  });
});
