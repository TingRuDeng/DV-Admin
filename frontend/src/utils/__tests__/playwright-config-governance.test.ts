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

  it("keeps environment-bound real backend specs out of the default config", () => {
    const config = readProjectFile("../../../playwright.config.ts");

    expect(config).toContain("testIgnore");
    expect(config).toContain("real-backend-smoke.spec.ts");
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
    expect(packageJson).toContain("e2e/profile.spec.ts");
    expect(packageJson).toContain("e2e/role-management.spec.ts");
    expect(packageJson).toContain("e2e/menu-management.spec.ts");
    expect(packageJson).toContain("e2e/file-upload-delete.spec.ts");
    expect(packageJson).toContain("e2e/dept-management.spec.ts");
    expect(packageJson).toContain("e2e/dict-management.spec.ts");
    expect(packageJson).toContain("e2e/dict-item-management.spec.ts");
    expect(packageJson).toContain("e2e/notice-management.spec.ts");
    expect(packageJson).toContain("e2e/log-management.spec.ts");
    expect(packageJson).toContain("e2e/shell-layout.spec.ts");
  });

  it("runs smoke E2E serially to avoid login mock races", () => {
    const packageJson = readProjectFile("../../../package.json");

    expect(packageJson).toContain("test:e2e:smoke");
    expect(packageJson).toContain("--workers=1");
  });

  it("waits for department login bootstrap before asserting redirected page", () => {
    const deptSpec = readProjectFile("../../../e2e/dept-management.spec.ts");

    expect(deptSpec).toContain("waitForDepartmentLoginBootstrap");
    expect(deptSpec).toContain("/api/v1/oauth/info/");
    expect(deptSpec).toContain("/api/v1/oauth/menus/routes/");
  });

  it("keeps a separate no-mock smoke for both real backends", () => {
    const packageJson = readProjectFile("../../../package.json");
    const realBackendConfig = readProjectFile("../../../playwright.real-backend.config.ts");
    const realBackendSpec = readProjectFile("../../../e2e/real-backend-smoke.spec.ts");
    const workflow = readProjectFile("../../../../.github/workflows/quality-gates.yml");

    expect(packageJson).toContain("test:e2e:real-backend");
    expect(realBackendConfig).toContain("REAL_BACKEND_URL");
    expect(realBackendConfig).toContain("reuseExistingServer: false");
    expect(realBackendConfig).toContain("playwright-report");
    expect(realBackendSpec).not.toContain("page.route(");
    expect(realBackendSpec).toContain("/api/v1/information/change-avatar/");
    expect(realBackendSpec).toContain("/api/v1/system/users/");
    expect(realBackendSpec).toContain("/api/v1/system/notices/page");
    expect(realBackendSpec).toContain("/my-notice");
    expect(workflow).toContain("actions/upload-artifact@v4");
    expect(workflow).toContain("frontend/test-results/");
  });
});
