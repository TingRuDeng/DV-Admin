import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("dashboard style migration", () => {
  it("composes the focused dashboard modules instead of glass-panel markup", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/dashboard/index.vue"), "utf8");

    expect(source).toContain("<PageShell");
    expect(source).toContain("<DashboardHero");
    expect(source).toContain("<DashboardQuickActions");
    expect(source).not.toContain("glass-panel");
    expect(source).not.toContain("visitTrend");
    expect(source).not.toContain("visitStats");
    expect(source).not.toContain("fetchVisit");
    expect(source).not.toContain("useOnlineCount");
    expect(source).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u);
    expect(source).not.toContain("GithubCorner");
  });
});
