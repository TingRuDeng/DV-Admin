import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const TAGS_VIEW_TYPE_FILES = [
  "src/store/modules/tags-view-store.ts",
  "src/layouts/components/TagsView/index.vue",
  "src/layouts/components/TagsView/TagItem.vue",
  "src/layouts/components/TagsView/TagsContextMenu.vue",
  "src/layouts/components/TagsView/useAffixTags.ts",
  "src/layouts/components/TagsView/useTagsContextMenu.ts",
  "src/layouts/components/TagsView/useTagsRouteSync.ts",
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

  it("keeps TagsView index as the orchestration surface", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/layouts/components/TagsView/index.vue"),
      "utf8"
    );

    expect(source).toContain("<TagItem");
    expect(source).toContain("<TagsContextMenu");
    expect(source).toContain("useTagsRouteSync");
    expect(source).not.toContain("<el-tag");
    expect(source).not.toContain("<Teleport");
    expect(source).not.toContain("RouteRecordRaw");
  });

  it("keeps TagsView index below the file size hard limit", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/layouts/components/TagsView/index.vue"),
      "utf8"
    );

    expect(source.split("\n").length).toBeLessThan(300);
  });
});
