import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("system user style migration", () => {
  it("uses the shared page shells and no longer depends on glass-panel or minimal-* hooks", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/user/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<ProSearch");
    expect(source).toContain("<ProTable");
    expect(source).toContain("<ProFormDrawer");
    expect(source).toContain('class="ff-side-panel');
    expect(source).not.toContain("glass-panel");
    expect(source).not.toContain("minimal-");
  });
});
