import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it, vi } from "vitest";
import request from "@/utils/request";
import UserAPI from "@/api/system/user-api";

vi.mock("@/utils/request", () => ({
  default: vi.fn(),
}));

describe("UserAPI.resetPassword", () => {
  it("sends password fields in request body", () => {
    UserAPI.resetPassword("1", "Newpass123", "Newpass123");

    expect(request).toHaveBeenCalledWith(
      expect.objectContaining({
        data: {
          password: "Newpass123",
          confirm_password: "Newpass123",
        },
      })
    );
    expect(vi.mocked(request).mock.calls[0]?.[0]).not.toHaveProperty("params");
  });
});

describe("system user api governance", () => {
  it("keeps profile legacy API comments out of the user module", () => {
    const source = readFileSync(resolve(process.cwd(), "src/api/system/user-api.ts"), "utf8");

    expect(source).not.toContain("UserProfileVO");
    expect(source).not.toContain("UserProfileForm");
    expect(source).not.toContain("PasswordChangeForm");
    expect(source).not.toContain("sendMobileCode");
    expect(source).not.toContain("bindOrChangeEmail");
  });
});
