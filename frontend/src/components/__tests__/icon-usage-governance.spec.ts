import { readdirSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

function collectVueFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? collectVueFiles(path) : path.endsWith(".vue") ? [path] : [];
  });
}

const legacyElementPlusIconPattern =
  /<(?:ArrowDown|ArrowLeft|ArrowRight|ArrowUp|Back|Calendar|CaretRight|CaretTop|Check|CircleCheck|CircleCheckFilled|CircleClose|CircleCloseFilled|Clock|Close|DArrowLeft|DArrowRight|Delete|Document|FullScreen|Hide|InfoFilled|Loading|Minus|More|MoreFilled|Image|QuestionFilled|RefreshLeft|RefreshRight|ScaleToOriginal|Search|SortDown|SortUp|Star|StarFilled|SuccessFilled|Eye|View|PictureFilled|WarningFilled|ZoomIn|ZoomOut|Plus)(?:\s|\/|>)/;

describe("Lucide icon usage governance", () => {
  it("uses the maintained Lucide Vue package", () => {
    const packageJson = JSON.parse(
      readFileSync(resolve(process.cwd(), "package.json"), "utf8")
    ) as {
      dependencies?: Record<string, string>;
    };

    expect(packageJson.dependencies?.["@lucide/vue"]).toBeDefined();
    expect(packageJson.dependencies?.["lucide-vue-next"]).toBeUndefined();
    expect(packageJson.dependencies?.["@element-plus/icons-vue"]).toBeUndefined();
  });

  it("does not pass string icon names to Element Plus controls", () => {
    const iconAttributes = collectVueFiles(resolve(process.cwd(), "src"))
      .flatMap((file) => {
        const source = readFileSync(file, "utf8");
        return [...source.matchAll(/<el-(?:button|link|switch)\b[^>]*>/g)].map((match) => ({
          file,
          tag: match[0],
        }));
      })
      .filter(({ tag }) => /(?:^|\s)(?:icon|active-icon|inactive-icon)="/.test(tag));

    expect(iconAttributes).toEqual([]);
  });

  it("does not place emoji characters in Vue templates", () => {
    const emojiPattern = /[\u{1f000}-\u{1faff}\u{2600}-\u{27bf}]/u;
    const emojiTemplates = collectVueFiles(resolve(process.cwd(), "src"))
      .flatMap((file) => {
        const source = readFileSync(file, "utf8");
        return [...source.matchAll(/<template[^>]*>([\s\S]*?)<\/template>/g)].map((match) => ({
          file,
          template: match[1],
        }));
      })
      .filter(({ template }) => emojiPattern.test(template));

    expect(emojiTemplates).toEqual([]);
  });

  it("does not auto-import legacy Element Plus icon components", () => {
    const legacyIconTemplates = collectVueFiles(resolve(process.cwd(), "src"))
      .flatMap((file) => {
        const source = readFileSync(file, "utf8");
        return [...source.matchAll(/<template[^>]*>([\s\S]*?)<\/template>/g)].map((match) => ({
          file,
          template: match[1],
        }));
      })
      .filter(({ template }) => legacyElementPlusIconPattern.test(template));

    expect(legacyIconTemplates).toEqual([]);
  });
});
