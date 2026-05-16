import { readdirSync, readFileSync, statSync } from "node:fs";
import { relative, resolve } from "node:path";
import { describe, expect, it } from "vitest";

const SOURCE_ROOT = resolve(process.cwd(), "src");
const DIRECT_CONSOLE_PATTERN = /console\.(log|debug|info|warn|error)\s*\(/;
const SOURCE_FILE_PATTERN = /\.(ts|tsx|vue)$/;

const ALLOWED_FILES = new Set(["utils/logger.ts"]);

function toSourcePath(filePath: string) {
  return relative(SOURCE_ROOT, filePath).replaceAll("\\", "/");
}

function shouldScanFile(filePath: string) {
  const sourcePath = toSourcePath(filePath);
  return (
    SOURCE_FILE_PATTERN.test(filePath) &&
    !sourcePath.includes("__tests__/") &&
    !sourcePath.endsWith(".test.ts") &&
    !sourcePath.endsWith(".spec.ts") &&
    !sourcePath.endsWith(".d.ts") &&
    !ALLOWED_FILES.has(sourcePath)
  );
}

function collectSourceFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((entry) => {
    const entryPath = resolve(dir, entry);
    const stat = statSync(entryPath);

    return stat.isDirectory() ? collectSourceFiles(entryPath) : [entryPath];
  });
}

describe("direct console governance", () => {
  it("keeps frontend source logs behind the shared logger", () => {
    const offenders = collectSourceFiles(SOURCE_ROOT)
      .filter(shouldScanFile)
      .filter((filePath) => DIRECT_CONSOLE_PATTERN.test(readFileSync(filePath, "utf8")))
      .map(toSourcePath);

    expect(
      offenders,
      `发现生产源码绕过统一 logger 直接调用 console:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
