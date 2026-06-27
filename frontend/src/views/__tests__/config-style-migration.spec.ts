import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = resolve(process.cwd(), "..");

function readRepoFile(relativePath: string) {
  return readFileSync(resolve(repoRoot, relativePath), "utf8");
}

function hasRepoFile(relativePath: string) {
  return existsSync(resolve(repoRoot, relativePath));
}

describe("system config orphan governance", () => {
  it("does not ship system config frontend code before backend route and permission contract exist", () => {
    const fastapiRoutes = readRepoFile("fastapi/app/api/v1/system/__init__.py");
    const djangoRoutes = readRepoFile("backend/drf_admin/apps/system/urls.py");
    const permissionSeeds = readRepoFile(
      ["fastapi", "tests", "fixtures", "permissions.py"].join("/")
    );
    const pageStyles = readRepoFile("frontend/src/styles/pages/index.scss");

    expect(fastapiRoutes).not.toContain("configs_router");
    expect(djangoRoutes).not.toContain("configs");
    expect(permissionSeeds).not.toContain("system:configs");
    expect(hasRepoFile("frontend/src/api/system/config-api.ts")).toBe(false);
    expect(hasRepoFile("frontend/src/views/system/config/index.vue")).toBe(false);
    expect(hasRepoFile("frontend/src/styles/pages/_system-config.scss")).toBe(false);
    expect(pageStyles).not.toContain("system-config");
  });
});
