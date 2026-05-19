import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const TAGS_VIEW_TYPE_FILES = [
  "src/store/modules/tags-view-store.ts",
  "src/layouts/components/TagsView/index.vue",
];

const TAGS_VIEW_ANY_PATTERNS = [
  /\b(?:res|result)\s*:\s*any\b/,
  /\(event\s+as\s+any\)\.wheelDelta\b/,
];

describe("tags view type governance", () => {
  it("keeps TagsView close result and wheel event boundaries free of any", () => {
    const offenders = TAGS_VIEW_TYPE_FILES.flatMap((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return source
        .split("\n")
        .map((line, index) => ({ file, line: index + 1, source: line.trim() }))
        .filter(({ source }) => TAGS_VIEW_ANY_PATTERNS.some((pattern) => pattern.test(source)));
    });

    expect(
      offenders,
      `发现 TagsView 类型边界重新使用 any:\n${offenders
        .map(({ file, line, source }) => `${file}:${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });
});
