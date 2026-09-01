import { describe, expect, it } from "vitest";

import { resolveStaticAssetUrl } from "@/utils/static-asset-url";

describe("resolveStaticAssetUrl", () => {
  it("joins backend media paths with the configured static origin", () => {
    expect(resolveStaticAssetUrl("/media/avatar/user.png", "http://127.0.0.1:8769/")).toBe(
      "http://127.0.0.1:8769/media/avatar/user.png"
    );
  });

  it("keeps absolute and browser-owned URLs unchanged", () => {
    expect(resolveStaticAssetUrl("https://cdn.example.com/avatar.png", "http://backend")).toBe(
      "https://cdn.example.com/avatar.png"
    );
    expect(resolveStaticAssetUrl("data:image/gif;base64,AAAA", "http://backend")).toBe(
      "data:image/gif;base64,AAAA"
    );
  });

  it("keeps the original relative path when no static origin is configured", () => {
    expect(resolveStaticAssetUrl("/media/avatar/user.png", "")).toBe("/media/avatar/user.png");
    expect(resolveStaticAssetUrl(undefined, "http://backend")).toBeUndefined();
  });
});
