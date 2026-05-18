import { readdirSync, readFileSync, statSync } from "node:fs";
import { relative, resolve } from "node:path";
import { describe, expect, it } from "vitest";

const API_ROOT = resolve(process.cwd(), "src/api");
const ANY_REQUEST_GENERIC_PATTERN = /request<any,/;

function collectTypeScriptFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((entry) => {
    const entryPath = resolve(dir, entry);
    const stat = statSync(entryPath);

    if (stat.isDirectory()) {
      return collectTypeScriptFiles(entryPath);
    }

    return entryPath.endsWith(".ts") ? [entryPath] : [];
  });
}

function toApiPath(filePath: string) {
  return relative(API_ROOT, filePath).replaceAll("\\", "/");
}

describe("api request type governance", () => {
  it("keeps API request calls away from any as the raw response generic", () => {
    const offenders = collectTypeScriptFiles(API_ROOT)
      .filter((filePath) => ANY_REQUEST_GENERIC_PATTERN.test(readFileSync(filePath, "utf8")))
      .map(toApiPath);

    expect(offenders, `发现 API 层 request<any, T> 类型逃逸:\n${offenders.join("\n")}`).toEqual([]);
  });
});
