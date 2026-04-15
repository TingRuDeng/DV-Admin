import { readdirSync, readFileSync } from "node:fs";
import { resolve, relative } from "node:path";
import { describe, expect, it } from "vitest";

const SRC_ROOT = resolve(process.cwd(), "src");
const LEGACY_CURD_IMPORT_PATTERN = /components\/CURD\//g;
const LEGACY_CURD_TAG_PATTERN = /<CURD\b|<PageSearch\b|<PageContent\b|<PageModal\b/g;

function collectSourceFiles(dir: string): string[] {
  const entries = readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];

  for (const entry of entries) {
    const absolutePath = resolve(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectSourceFiles(absolutePath));
      continue;
    }
    if (entry.isFile() && (entry.name.endsWith(".vue") || entry.name.endsWith(".ts"))) {
      files.push(absolutePath);
    }
  }

  return files;
}

function shouldSkip(path: string) {
  return (
    path.startsWith("src/components/CURD/") ||
    path.includes("/__tests__/") ||
    path === "src/types/components.d.ts"
  );
}

describe("curd deprecation governance", () => {
  it("forbids CURD imports and tags outside the CURD compatibility layer", () => {
    const files = collectSourceFiles(SRC_ROOT);
    const offenders: string[] = [];

    for (const file of files) {
      const relativePath = relative(process.cwd(), file);
      if (shouldSkip(relativePath)) {
        continue;
      }

      const source = readFileSync(file, "utf8");
      if (LEGACY_CURD_IMPORT_PATTERN.test(source) || LEGACY_CURD_TAG_PATTERN.test(source)) {
        offenders.push(relativePath);
      }

      LEGACY_CURD_IMPORT_PATTERN.lastIndex = 0;
      LEGACY_CURD_TAG_PATTERN.lastIndex = 0;
    }

    offenders.sort();
    expect(
      offenders,
      `Found CURD usage outside compatibility layer:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
