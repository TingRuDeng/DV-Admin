import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const API_EXTRA_FIELD_FILES = [
  "src/api/system/dict-items-api.ts",
  "src/api/test/project-api.ts",
  "src/api/test/cases-api.ts",
];

const ANY_INDEX_SIGNATURE_PATTERN = /\[key:\s*string\]:\s*any\b/;

describe("api extra fields type governance", () => {
  it("keeps API extension fields free of any", () => {
    const offenders = API_EXTRA_FIELD_FILES.flatMap((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return source
        .split("\n")
        .map((line, index) => ({ file, line: index + 1, source: line.trim() }))
        .filter(({ source }) => ANY_INDEX_SIGNATURE_PATTERN.test(source));
    });

    expect(
      offenders,
      `发现 API 扩展字段重新使用 any:\n${offenders
        .map(({ file, line, source }) => `${file}:${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });
});
