import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const STORAGE_SOURCE = resolve(process.cwd(), "src/utils/storage.ts");
const ANY_TYPE_PATTERN = /\bany\b/;

describe("storage type governance", () => {
  it("keeps storage utility boundaries free of any", () => {
    const source = readFileSync(STORAGE_SOURCE, "utf8");
    const offenders = source
      .split("\n")
      .map((line, index) => ({ line: index + 1, source: line.trim() }))
      .filter(({ source }) => ANY_TYPE_PATTERN.test(source));

    expect(
      offenders,
      `发现 storage.ts 重新引入 any:\n${offenders
        .map(({ line, source }) => `${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });
});
