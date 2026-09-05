import { describe, expect, it } from "vitest";
import { formatLogPayload } from "../log-detail-utils";

describe("formatLogPayload", () => {
  it("formats JSON payloads for inspection", () => {
    expect(formatLogPayload('{"ok":true,"count":2}')).toBe('{\n  "ok": true,\n  "count": 2\n}');
  });

  it("keeps plain text and normalizes empty values", () => {
    expect(formatLogPayload("request failed")).toBe("request failed");
    expect(formatLogPayload("   ")).toBe("-");
  });

  it("formats structured request context without requiring a JSON string", () => {
    expect(formatLogPayload({ pathParams: { userId: "7" }, truncated: false })).toBe(
      '{\n  "pathParams": {\n    "userId": "7"\n  },\n  "truncated": false\n}'
    );
  });
});
