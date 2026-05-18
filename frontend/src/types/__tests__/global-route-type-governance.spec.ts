import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const GLOBAL_ROUTE_TYPE_FILES = ["src/types/global.d.ts", "src/utils/i18n.ts"];
const ANY_TYPE_PATTERN = /\bany\b/;

describe("global route type governance", () => {
  it("keeps shared route and API utility boundaries free of any", () => {
    const offenders = GLOBAL_ROUTE_TYPE_FILES.flatMap((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return source
        .split("\n")
        .map((line, index) => ({ file, line: index + 1, source: line.trim() }))
        .filter(({ source }) => ANY_TYPE_PATTERN.test(source));
    });

    expect(
      offenders,
      `发现全局路由/API 类型边界重新使用 any:\n${offenders
        .map(({ file, line, source }) => `${file}:${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });
});
