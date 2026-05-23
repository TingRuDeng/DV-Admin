import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system dict style migration", () => {
  it("uses PageShell, ProSearch, ProTable and split form drawer without minimal-* classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/dict/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<DictFormDrawer");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain("<ProFormDrawer");
    expect(source).not.toContain(':data="tableData"');
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
  });

  it("keeps dict form implementation behind explicit component APIs", () => {
    const drawerSource = readFileSync(
      resolve(process.cwd(), "src/views/system/dict/components/DictFormDrawer.vue"),
      "utf8"
    );

    expect(drawerSource).toContain("<ProFormDrawer");
    expect(drawerSource).toContain("defineExpose");
    expect(drawerSource).toContain("openCreate");
    expect(drawerSource).toContain("openEdit");
  });
});
