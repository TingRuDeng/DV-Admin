import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("my notice style migration", () => {
  it("uses PageShell, ProSearch and request-driven ProTable without legacy container classes", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/views/system/notice/components/MyNotice.vue"),
      "utf8"
    );

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain(':request="requestTableData"');
    expect(source).toContain('ref="tableRef"');
    expect(source).not.toContain("<FilterPanel");
    expect(source).not.toContain("<DataPanel");
    expect(source).not.toContain("search-container");
    expect(source).not.toContain("data-table");
    expect(source).not.toContain("minimal-");
  });
});
