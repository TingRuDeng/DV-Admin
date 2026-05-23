import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const TEXT_SCROLL_FILES = [
  "src/components/TextScroll/index.vue",
  "src/components/TextScroll/useTextScroll.ts",
  "src/components/TextScroll/types.ts",
];

describe("text scroll governance", () => {
  it("keeps TextScroll index focused on rendering", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/components/TextScroll/index.vue"),
      "utf8"
    );

    expect(source).toContain("useTextScroll(props)");
    expect(source).not.toContain("useElementHover");
    expect(source).not.toContain("sanitizeHtml");
    expect(source).not.toContain("setTimeout(type");
    expect(source).not.toContain("window.addEventListener");
  });

  it("keeps TextScroll files below the component size limit", () => {
    const oversizedFiles = TEXT_SCROLL_FILES.flatMap((file) => {
      const lineCount = readFileSync(resolve(process.cwd(), file), "utf8").split("\n").length;
      return lineCount > 300 ? [`${file}: ${lineCount}`] : [];
    });

    expect(oversizedFiles).toEqual([]);
  });
});
