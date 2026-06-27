import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system notice style migration", () => {
  it("uses PageShell, ProSearch, ProTable and split form drawer without minimal-* classes", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/views/system/notice/index.vue"),
      "utf8"
    );

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<NoticeFormDrawer");
    expect(source).toContain("<NoticeDetailDialog");
    expect(source).toContain("<NoticeStatusTag");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain("<ProFormDrawer");
    expect(source).not.toContain("<ProDialog");
    expect(source).not.toContain("<FilterPanel");
    expect(source).not.toContain("<DataPanel");
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
    expect(source.split("\n").length).toBeLessThan(300);
  });

  it("keeps notice form implementation behind an explicit component API", () => {
    const drawerSource = readFileSync(
      resolve(process.cwd(), "src/views/system/notice/components/NoticeFormDrawer.vue"),
      "utf8"
    );

    expect(drawerSource).toContain("<ProFormDrawer");
    expect(drawerSource).toContain("defineExpose");
    expect(drawerSource).toContain("openCreate");
    expect(drawerSource).toContain("openEdit");
  });

  it("keeps notice detail implementation behind an explicit component API", () => {
    const detailSource = readFileSync(
      resolve(process.cwd(), "src/views/system/notice/components/NoticeDetailDialog.vue"),
      "utf8"
    );

    expect(detailSource).toContain("<ProDialog");
    expect(detailSource).toContain("<SafeHtml");
    expect(detailSource).toContain("defineExpose");
    expect(detailSource).toContain("open");
  });

  it("keeps notice status label mapping behind a dedicated display component", () => {
    const statusSource = readFileSync(
      resolve(process.cwd(), "src/views/system/notice/components/NoticeStatusTag.vue"),
      "utf8"
    );

    expect(statusSource).toContain("NoticeStatusTag");
    expect(statusSource).toContain("STATUS_META_MAP");
    expect(statusSource).toContain("kind: NoticeStatusKind");
    expect(statusSource).toContain('class="ff-status-tag"');
  });
});
