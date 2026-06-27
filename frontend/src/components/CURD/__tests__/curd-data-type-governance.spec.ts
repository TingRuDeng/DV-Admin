import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const CURD_ROOT = resolve(process.cwd(), "src/components/CURD");
const TYPES_SOURCE = readFileSync(resolve(CURD_ROOT, "types.ts"), "utf8");
const DATA_SOURCE = readFileSync(resolve(CURD_ROOT, "usePageContentData.ts"), "utf8");

const DATA_ANY_PATTERNS = [
  /IContentConfig<T\s*=\s*any/,
  /indexAction:\s*\(queryParams:\s*T\)\s*=>\s*Promise<any>/,
  /parseData\?:\s*\(res:\s*any\)/,
  /deleteAction\?:\s*\(ids:\s*string\)\s*=>\s*Promise<any>/,
  /exportAction\?:\s*\(queryParams:\s*T\)\s*=>\s*Promise<any>/,
  /importsAction\?:\s*\(data:\s*IObject\[\]\)\s*=>\s*Promise<any>/,
  /formAction\?:\s*\(data:\s*T\)\s*=>\s*Promise<any>/,
];

describe("CURD data type governance", () => {
  it("keeps data actions and parser away from explicit any", () => {
    const offenders = DATA_ANY_PATTERNS.filter((pattern) => pattern.test(TYPES_SOURCE));

    expect(
      offenders.map((pattern) => pattern.source),
      `发现 CURD 数据链路重新引入 any:\n${offenders.map((pattern) => pattern.source).join("\n")}`
    ).toEqual([]);
  });

  it("keeps page data application free of any response parameters", () => {
    expect(DATA_SOURCE).not.toMatch(/applyPageData\(data:\s*any\)/);
  });
});
