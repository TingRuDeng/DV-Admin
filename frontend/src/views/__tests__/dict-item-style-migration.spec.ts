import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system dict item style migration", () => {
  it("uses PageShell, FilterPanel, and DataPanel without minimal-* classes", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/views/system/dict/dict-item.vue"),
      "utf8"
    );

    expect(source).toContain("<PageShell");
    expect(source).toContain("<FilterPanel");
    expect(source).toContain("<DataPanel");
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
  });
});
