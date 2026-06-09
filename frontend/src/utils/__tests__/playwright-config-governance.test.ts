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

  it("runs core business flow in smoke E2E", () => {
    const packageJson = readProjectFile("../../../package.json");

    expect(packageJson).toContain("e2e/user-management.spec.ts");
    expect(packageJson).toContain("e2e/role-management.spec.ts");
    expect(packageJson).toContain("e2e/menu-management.spec.ts");
    expect(packageJson).toContain("e2e/file-upload-delete.spec.ts");
    expect(packageJson).toContain("e2e/dept-management.spec.ts");
    expect(packageJson).toContain("e2e/dict-management.spec.ts");
  });

  it("runs smoke E2E serially to avoid login mock races", () => {
    const packageJson = readProjectFile("../../../package.json");

    expect(packageJson).toContain("test:e2e:smoke");
    expect(packageJson).toContain("--workers=1");
  });
});
