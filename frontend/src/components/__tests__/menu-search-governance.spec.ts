import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const MENU_SEARCH_FILES = [
  "src/components/MenuSearch/index.vue",
  "src/components/MenuSearch/MenuSearchFooter.vue",
  "src/components/MenuSearch/MenuSearchHistory.vue",
  "src/components/MenuSearch/MenuSearchResultList.vue",
  "src/components/MenuSearch/menu-search-routes.ts",
  "src/components/MenuSearch/useMenuSearchHistory.ts",
  "src/components/MenuSearch/types.ts",
];

describe("menu search governance", () => {
  it("keeps MenuSearch index as the orchestration surface", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/components/MenuSearch/index.vue"),
      "utf8"
    );

    expect(source).toContain("<MenuSearchHistory");
    expect(source).toContain("<MenuSearchResultList");
    expect(source).toContain("<MenuSearchFooter");
    expect(source).not.toContain('class="search-history"');
    expect(source).not.toContain('class="shortcuts-group"');
    expect(source).not.toContain("function loadRoutes");
    expect(source).not.toContain("localStorage.");
  });

  it("keeps MenuSearch files below the component size limit", () => {
    const oversizedFiles = MENU_SEARCH_FILES.flatMap((file) => {
      const lineCount = readFileSync(resolve(process.cwd(), file), "utf8").split("\n").length;
      return lineCount > 300 ? [`${file}: ${lineCount}`] : [];
    });

    expect(oversizedFiles).toEqual([]);
  });
});
