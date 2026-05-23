import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system role style migration", () => {
  it("uses PageShell, ProSearch, ProTable and split drawer components without minimal-* classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/role/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<RoleFormDrawer");
    expect(source).toContain("<RolePermissionDrawer");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain("<ProFormDrawer");
    expect(source).not.toContain("<ProDrawer");
    expect(source).not.toContain(':data="roleList"');
    expect(source).not.toContain("minimal-btn");
    expect(source).not.toContain("glass-panel");
  });

  it("keeps drawer implementation behind explicit component APIs", () => {
    const formSource = readFileSync(
      resolve(process.cwd(), "src/views/system/role/components/RoleFormDrawer.vue"),
      "utf8"
    );
    const permissionSource = readFileSync(
      resolve(process.cwd(), "src/views/system/role/components/RolePermissionDrawer.vue"),
      "utf8"
    );

    expect(formSource).toContain("<ProFormDrawer");
    expect(formSource).toContain("defineExpose");
    expect(formSource).toContain("openCreate");
    expect(formSource).toContain("openEdit");
    expect(permissionSource).toContain("<ProDrawer");
    expect(permissionSource).toContain("defineExpose");
    expect(permissionSource).toContain("open");
  });
});
