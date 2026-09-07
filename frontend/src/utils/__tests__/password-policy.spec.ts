import { describe, expect, it } from "vitest";
import { passwordLengthError } from "../password-policy";

const policy = { minLength: 15, maxLength: 128 };

describe("new-password length policy", () => {
  it("counts Unicode code points, preserving spaces", () => {
    expect(passwordLengthError("夜晚沿着湖边散步然后回家喝热茶", policy)).toBeUndefined();
    expect(passwordLengthError(" a long quiet walk ", policy)).toBeUndefined();
    expect(passwordLengthError("\u{1f600}".repeat(8), policy)).toBeDefined();
    expect(passwordLengthError("\u{1f600}".repeat(128), policy)).toBeUndefined();
    expect(passwordLengthError("x".repeat(129), policy)).toBeDefined();
  });

  it("does not allow a missing policy to silently disable validation", () => {
    expect(passwordLengthError("a long enough passphrase", null)).toBeDefined();
    expect(passwordLengthError("short123", { minLength: NaN, maxLength: 128 })).toBeDefined();
    expect(passwordLengthError("short123", { minLength: 6, maxLength: 128 })).toBeDefined();
    expect(passwordLengthError("short123", policy)).toBeDefined();
  });
});
