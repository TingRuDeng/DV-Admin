import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("dashboard style migration", () => {
  it("uses the shared page shell instead of glass-panel markup", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/dashboard/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain('class="ff-page-shell__hero');
    expect(source).not.toContain("glass-panel");
  });
});
