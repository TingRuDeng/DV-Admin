import { readdirSync, readFileSync } from "node:fs";
import { resolve, relative } from "node:path";
import { describe, expect, it } from "vitest";

const VIEWS_ROOT = resolve(process.cwd(), "src/views");
const RAW_OVERLAY_PATTERN = /<el-dialog\b|<el-drawer\b/g;

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

describe("page overlay convergence", () => {
  it("keeps view-layer dialogs and drawers on Pro abstractions", () => {
    const vueFiles = collectVueFiles(VIEWS_ROOT);
    const offenders: string[] = [];

    for (const file of vueFiles) {
      const source = readFileSync(file, "utf8");
      if (RAW_OVERLAY_PATTERN.test(source)) {
        offenders.push(relative(process.cwd(), file));
      }
      RAW_OVERLAY_PATTERN.lastIndex = 0;
    }

    expect(
      offenders,
      `Found raw el-dialog/el-drawer in view files:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
