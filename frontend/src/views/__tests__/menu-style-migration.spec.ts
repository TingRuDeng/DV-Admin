import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system menu style migration", () => {
  it("uses PageShell, ProSearch, ProTable and ProFormDrawer without minimal-* classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/menu/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<ProFormDrawer");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain(':data="menuTableData"');
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
  });
});
