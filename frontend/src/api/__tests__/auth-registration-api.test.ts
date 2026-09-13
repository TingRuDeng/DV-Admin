import { describe, expect, it, vi } from "vitest";
import AuthAPI from "@/api/auth-api";
import request from "@/utils/request";

vi.mock("@/utils/request", () => ({
  default: vi.fn(),
}));

describe("AuthAPI public authentication flows", () => {
  it("keeps the shared camelCase request contract", () => {
    AuthAPI.sendEmailCode({
      purpose: "register",
      email: "user@example.com",
      captchaKey: "captcha-key",
      captchaCode: "1234",
    });
    AuthAPI.register({
      purpose: "register",
      username: "user",
      email: "user@example.com",
      password: "a sufficiently long passphrase",
      confirmPassword: "a sufficiently long passphrase",
      emailCode: "123456",
      captchaKey: "captcha-key",
      captchaCode: "1234",
    });
    AuthAPI.resetPassword({
      purpose: "reset_password",
      username: "user",
      email: "user@example.com",
      newPassword: "another sufficiently long passphrase",
      confirmPassword: "another sufficiently long passphrase",
      emailCode: "654321",
      captchaKey: "captcha-key",
      captchaCode: "1234",
    });

    const calls = vi
      .mocked(request)
      .mock.calls.map(([config]) => config as { url?: string; data?: unknown });
    expect(calls.map((config) => config.url)).toEqual([
      "/api/oauth/email-code/",
      "/api/oauth/register/",
      "/api/oauth/password/reset/",
    ]);
    expect(calls[1]?.data).toMatchObject({ confirmPassword: "a sufficiently long passphrase" });
    expect(calls[2]?.data).toMatchObject({ newPassword: "another sufficiently long passphrase" });
  });
});
