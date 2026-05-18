import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const TOKEN_REFRESH_SOURCE = resolve(process.cwd(), "src/composables/auth/useTokenRefresh.ts");
const ANY_TYPE_PATTERN = /\bany\b/;

describe("useTokenRefresh type governance", () => {
  it("keeps token refresh retry plumbing free of any", () => {
    const source = readFileSync(TOKEN_REFRESH_SOURCE, "utf8");
    const offenders = source
      .split("\n")
      .map((line, index) => ({ line: index + 1, source: line.trim() }))
      .filter(({ source }) => ANY_TYPE_PATTERN.test(source));

    expect(
      offenders,
      `发现 useTokenRefresh 重新引入 any:\n${offenders
        .map(({ line, source }) => `${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });
});
