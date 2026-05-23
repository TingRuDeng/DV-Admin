import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const SETTINGS_TYPE_FILES = [
  "src/store/modules/settings-store.ts",
  "src/layouts/components/Settings/index.vue",
  "src/layouts/components/Settings/ThemeSection.vue",
  "src/layouts/components/Settings/InterfaceSection.vue",
  "src/layouts/components/Settings/LayoutSection.vue",
  "src/layouts/components/Settings/SettingsActions.vue",
  "src/layouts/components/Settings/types.ts",
];

const SETTINGS_ANY_PATTERNS = [/\bRef<any>/, /\bval:\s*any\b/];

describe("settings type governance", () => {
  it("keeps settings store and panel boundaries free of any", () => {
    const offenders = SETTINGS_TYPE_FILES.flatMap((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return source
        .split("\n")
        .map((line, index) => ({ file, line: index + 1, source: line.trim() }))
        .filter(({ source }) => SETTINGS_ANY_PATTERNS.some((pattern) => pattern.test(source)));
    });

    expect(
      offenders,
      `发现设置面板类型边界重新使用 any:\n${offenders
        .map(({ file, line, source }) => `${file}:${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });

  it("keeps settings drawer as an orchestration shell", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/layouts/components/Settings/index.vue"),
      "utf8"
    );

    expect(source).toContain("<ThemeSection");
    expect(source).toContain("<InterfaceSection");
    expect(source).toContain("<LayoutSection");
    expect(source).toContain("<SettingsActions");
    expect(source).not.toContain("<el-color-picker");
    expect(source).not.toContain("layoutOptions");
    expect(source).not.toContain("DocumentCopy");
  });
});
