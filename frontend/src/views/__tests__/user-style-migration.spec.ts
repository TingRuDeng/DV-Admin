import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system user style migration", () => {
  it("uses the shared page shells and no longer depends on glass-panel or minimal-* hooks", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/user/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<UserFormDrawer");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain(':data="pageData"');
    expect(source).toContain('class="ff-side-panel');
    expect(source).not.toContain("glass-panel");
    expect(source).not.toContain("minimal-");
  });

  it("keeps the user form drawer in a focused child component", () => {
    const pageSource = readFileSync(
      resolve(process.cwd(), "src/views/system/user/index.vue"),
      "utf8"
    );
    const drawerSource = readFileSync(
      resolve(process.cwd(), "src/views/system/user/components/UserFormDrawer.vue"),
      "utf8"
    );

    expect(pageSource).not.toContain("<ProFormDrawer");
    expect(drawerSource).toContain("<ProFormDrawer");
    expect(drawerSource).toContain("defineExpose");
    expect(drawerSource).toContain("openCreate");
    expect(drawerSource).toContain("openEdit");
  });
});
