import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system notice style migration", () => {
  it("uses PageShell, ProSearch and request-driven ProTable without minimal-* classes", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/views/system/notice/index.vue"),
      "utf8"
    );

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain("<FilterPanel");
    expect(source).not.toContain("<DataPanel");
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
  });
});
