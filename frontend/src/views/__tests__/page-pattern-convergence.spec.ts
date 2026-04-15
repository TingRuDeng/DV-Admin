import { readdirSync, readFileSync } from "node:fs";
import { resolve, relative } from "node:path";
import { describe, expect, it } from "vitest";

const VIEWS_ROOT = resolve(process.cwd(), "src/views");
const LEGACY_CURD_PATTERN = /components\/CURD|<PageSearch\b|<PageContent\b|<PageModal\b/g;
const PRO_TABLE_PATTERN = /<ProTable\b/;
const REQUEST_TABLE_PATTERN = /<ProTable\b[\s\S]*?:request\s*=\s*["'][^"']+["']/m;
const REQUEST_ADAPTER_PATTERN = /const\s+requestTableData\s*=\s*create(?:Page|List)Request\b/m;

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

  it("keeps view-layer ProTable usage on request-driven mode", () => {
    const vueFiles = collectVueFiles(VIEWS_ROOT);
    const offenders: string[] = [];

    for (const file of vueFiles) {
      const source = readFileSync(file, "utf8");
      if (!PRO_TABLE_PATTERN.test(source)) {
        continue;
      }

      if (!REQUEST_TABLE_PATTERN.test(source)) {
        offenders.push(relative(process.cwd(), file));
      }
      REQUEST_TABLE_PATTERN.lastIndex = 0;
    }

    expect(
      offenders,
      `Found view pages not using request-driven ProTable:\n${offenders.join("\n")}`
    ).toEqual([]);
  });

  it("keeps view-layer requestTableData on shared request adapters", () => {
    const vueFiles = collectVueFiles(VIEWS_ROOT);
    const offenders: string[] = [];

    for (const file of vueFiles) {
      const source = readFileSync(file, "utf8");
      if (!PRO_TABLE_PATTERN.test(source)) {
        continue;
      }

      if (!REQUEST_ADAPTER_PATTERN.test(source)) {
        offenders.push(relative(process.cwd(), file));
      }
      REQUEST_ADAPTER_PATTERN.lastIndex = 0;
    }

    expect(
      offenders,
      `Found view pages not using shared ProTable request adapters:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
