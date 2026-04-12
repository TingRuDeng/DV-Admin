import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("profile style migration", () => {
  it("uses PageShell and semantic panels without glass-panel classes", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/profile/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("ff-side-panel");
    expect(source).toContain("<DataPanel");
    expect(source).not.toContain("glass-panel");
  });
});
