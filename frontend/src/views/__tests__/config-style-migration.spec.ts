import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system config style migration", () => {
  it("uses PageShell, ProSearch, ProTable and ProFormDrawer without minimal-* classes", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/views/system/config/index.vue"),
      "utf8"
    );

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<ProFormDrawer");
    expect(source).not.toContain("minimal-");
    expect(source).not.toContain("glass-panel");
  });
});
