import { describe, expect, it } from "vitest";
import { resolveSafeRedirect } from "../safe-redirect";

describe("resolveSafeRedirect", () => {
  it.each(["/", "/system/users", "/system/users?page=2#top", "/detail/1", "/search?q=a b"])(
    "keeps in-site path %s",
    (value) => {
      expect(resolveSafeRedirect(value)).toBe(value);
    }
  );

  it.each([
    undefined,
    null,
    "",
    "dashboard",
    "https://evil.example",
    "//evil.example",
    "/\\evil.example",
    "javascript:alert(1)",
    "/\u0000//evil.example",
    "/\t/evil.example",
    "/\n/evil.example",
  ])("falls back for unsafe value %s", (value) => {
    expect(resolveSafeRedirect(value)).toBe("/");
  });

  it("uses the first value of a repeated query parameter", () => {
    expect(resolveSafeRedirect(["/system/roles", "https://evil.example"])).toBe("/system/roles");
    expect(resolveSafeRedirect(["//evil.example"])).toBe("/");
  });

  it("honours a custom fallback", () => {
    expect(resolveSafeRedirect("https://evil.example", "/dashboard")).toBe("/dashboard");
  });
});
