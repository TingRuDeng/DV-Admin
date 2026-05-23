import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("permission white list", () => {
  it("includes error page paths beside login", () => {
    const source = readFileSync(resolve(process.cwd(), "src/plugins/permission.ts"), "utf8");

    expect(source).toContain('"/401"');
    expect(source).toContain('"/403"');
    expect(source).toContain('"/404"');
  });
});
