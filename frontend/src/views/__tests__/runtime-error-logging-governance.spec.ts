import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const RUNTIME_ERROR_FILES = [
  "src/utils/request.ts",
  "src/utils/auth.ts",
  "src/plugins/permission.ts",
  "src/composables/auth/useTokenRefresh.ts",
  "src/store/modules/user-store.ts",
];

const DIRECT_CONSOLE_PATTERN = /console\.(log|debug|info|warn|error)\(/;

describe("runtime error logging governance", () => {
  it("keeps critical runtime modules on the shared logger", () => {
    const offenders = RUNTIME_ERROR_FILES.filter((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return DIRECT_CONSOLE_PATTERN.test(source) || !source.includes("createLogger");
    });

    expect(
      offenders,
      `Found critical runtime modules bypassing the shared logger:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
