import { readdirSync, readFileSync } from "node:fs";
import { resolve, relative } from "node:path";
import { describe, expect, it } from "vitest";

const COMPONENTS_ROOT = resolve(process.cwd(), "src/components");
const RAW_OVERLAY_PATTERN = /<el-dialog\b|<el-drawer\b/g;

const ALLOWED_OVERLAY_FILES = [
  "src/components/CURD/PageContent.vue",
  "src/components/CURD/PageModal.vue",
  "src/components/ProDialog/index.vue",
  "src/components/ProDrawer/index.vue",
  "src/components/ProFormDrawer/index.vue",
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

describe("component overlay governance", () => {
  it("keeps raw element overlays scoped to wrapper and legacy compatibility components only", () => {
    const vueFiles = collectVueFiles(COMPONENTS_ROOT);
    const offenders: string[] = [];

    for (const file of vueFiles) {
      const source = readFileSync(file, "utf8");
      if (RAW_OVERLAY_PATTERN.test(source)) {
        offenders.push(relative(process.cwd(), file));
      }
      RAW_OVERLAY_PATTERN.lastIndex = 0;
    }

    offenders.sort();
    expect(
      offenders,
      `Unexpected raw el-dialog/el-drawer usage in components:\n${offenders.join("\n")}`
    ).toEqual([...ALLOWED_OVERLAY_FILES]);
  });
});
