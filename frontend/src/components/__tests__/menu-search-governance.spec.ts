import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const MENU_SEARCH_FILES = [
  "src/components/MenuSearch/index.vue",
  "src/components/MenuSearch/MenuSearchHistory.vue",
  "src/components/MenuSearch/MenuSearchResultList.vue",
  "src/components/MenuSearch/menu-search-routes.ts",
  "src/components/MenuSearch/useMenuSearchHistory.ts",
  "src/components/MenuSearch/useMenuSearchShortcut.ts",
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
    expect(source).toContain('role="combobox"');
    expect(source).toContain('role="listbox"');
    expect(source).not.toContain("<ProDialog");
    expect(source).not.toContain("<el-popover");
    expect(source).not.toContain("<el-autocomplete");
    expect(source).not.toContain('class="search-history"');
    expect(source).not.toContain('class="shortcuts-group"');
    expect(source).not.toContain("function loadRoutes");
    expect(source).not.toContain("localStorage.");
    // default-passive-events 让 mousedown 监听默认 passive，阻止失焦必须写在 pointerdown 上
    expect(source).toContain("@pointerdown.prevent");
    expect(source).not.toContain("@mousedown.prevent");
    expect(
      existsSync(resolve(process.cwd(), "src/components/MenuSearch/MenuSearchFooter.vue"))
    ).toBe(false);
  });

  it("keeps listbox options free of focusable controls", () => {
    for (const file of [
      "src/components/MenuSearch/MenuSearchHistory.vue",
      "src/components/MenuSearch/MenuSearchResultList.vue",
    ]) {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");

      expect(source, file).toContain('role="option"');
      expect(source, file).not.toContain("<button");
      expect(source, file).not.toContain("<el-button");
      expect(source, file).not.toContain("tabindex");
    }
  });

  it("keeps MenuSearch files below the component size limit", () => {
    const oversizedFiles = MENU_SEARCH_FILES.flatMap((file) => {
      const lineCount = readFileSync(resolve(process.cwd(), file), "utf8").split("\n").length;
      return lineCount > 300 ? [`${file}: ${lineCount}`] : [];
    });

    expect(oversizedFiles).toEqual([]);
  });
});
