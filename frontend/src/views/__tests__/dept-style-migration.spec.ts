import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system dept style migration", () => {
  it("uses PageShell, ProSearch, ProTable and ProFormDrawer without minimal-* classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/dept/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<ProFormDrawer");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain("<FilterPanel");
    expect(source).not.toContain("<DataPanel");
    expect(source).not.toContain("<el-dialog");
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
  });
});
