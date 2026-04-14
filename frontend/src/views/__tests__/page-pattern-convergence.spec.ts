import { readdirSync, readFileSync } from "node:fs";
import { resolve, relative } from "node:path";
import { describe, expect, it } from "vitest";

const VIEWS_ROOT = resolve(process.cwd(), "src/views");
const LEGACY_CURD_PATTERN = /components\/CURD|<PageSearch\b|<PageContent\b|<PageModal\b/g;
const REQUEST_TABLE_PATTERN = /<ProTable\b[\s\S]*?:request="[^"]+"/m;

const SYSTEM_TABLE_PAGES = [
  "src/views/system/config/index.vue",
  "src/views/system/dept/index.vue",
  "src/views/system/dict/dict-item.vue",
  "src/views/system/dict/index.vue",
  "src/views/system/log/index.vue",
  "src/views/system/menu/index.vue",
  "src/views/system/notice/components/MyNotice.vue",
  "src/views/system/notice/index.vue",
  "src/views/system/role/index.vue",
  "src/views/system/user/index.vue",
] as const;

function collectVueFiles(dir: string): string[] {
  const entries = readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];

  for (const entry of entries) {
    const absolutePath = resolve(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectVueFiles(absolutePath));
      continue;
    }
    if (entry.isFile() && entry.name.endsWith(".vue")) {
      files.push(absolutePath);
    }
  }

  return files;
}

describe("page pattern convergence", () => {
  it("keeps view-layer pages away from legacy CURD page components", () => {
    const vueFiles = collectVueFiles(VIEWS_ROOT);
    const offenders: string[] = [];

    for (const file of vueFiles) {
      const source = readFileSync(file, "utf8");
      if (LEGACY_CURD_PATTERN.test(source)) {
        offenders.push(relative(process.cwd(), file));
      }
      LEGACY_CURD_PATTERN.lastIndex = 0;
    }

    expect(
      offenders,
      `Found legacy CURD page component usage in view files:\n${offenders.join("\n")}`
    ).toEqual([]);
  });

  it("keeps system list pages on request-driven ProTable", () => {
    const offenders: string[] = [];

    for (const file of SYSTEM_TABLE_PAGES) {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      if (!REQUEST_TABLE_PATTERN.test(source)) {
        offenders.push(file);
      }
    }

    expect(
      offenders,
      `Found system table pages not using request-driven ProTable:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
