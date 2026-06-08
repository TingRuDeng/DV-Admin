import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const readProjectFile = (relativePath: string) =>
  readFileSync(fileURLToPath(new URL(relativePath, import.meta.url)), "utf8");

describe("playwright local server governance", () => {
  it("fails instead of reusing an unrelated local server", () => {
    const config = readProjectFile("../../../playwright.config.ts");

    expect(config).toContain("--strictPort");
    expect(config).toContain("reuseExistingServer: false");
  });

  it("keeps local html reports out of git status", () => {
    const gitignore = readProjectFile("../../../../.gitignore");

    expect(gitignore).toContain("frontend/playwright-report/");
  });

  it("keeps local html reports out of prettier checks", () => {
    const prettierignore = readProjectFile("../../../.prettierignore");

    expect(prettierignore).toContain("playwright-report/");
  });
});
