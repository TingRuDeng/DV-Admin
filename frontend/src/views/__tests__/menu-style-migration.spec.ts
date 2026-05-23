import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system menu style migration", () => {
  it("uses PageShell, ProSearch, ProTable and split form drawer without minimal-* classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/menu/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<MenuFormDrawer");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain("<ProFormDrawer");
    expect(source).not.toContain(':data="menuTableData"');
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
  });

  it("keeps menu form implementation behind explicit component APIs", () => {
    const drawerSource = readFileSync(
      resolve(process.cwd(), "src/views/system/menu/components/MenuFormDrawer.vue"),
      "utf8"
    );
    const routeParamsSource = readFileSync(
      resolve(process.cwd(), "src/views/system/menu/components/MenuRouteParamsEditor.vue"),
      "utf8"
    );
    const routeFieldsSource = readFileSync(
      resolve(process.cwd(), "src/views/system/menu/components/MenuRouteFields.vue"),
      "utf8"
    );

    expect(drawerSource).toContain("<ProFormDrawer");
    expect(drawerSource).toContain("<MenuRouteFields");
    expect(drawerSource).toContain("defineExpose");
    expect(drawerSource).toContain("openCreate");
    expect(drawerSource).toContain("openEdit");
    expect(routeFieldsSource).toContain("<MenuRouteParamsEditor");
    expect(routeFieldsSource).toContain("defineProps");
    expect(routeParamsSource).toContain("defineModel");
  });
});
