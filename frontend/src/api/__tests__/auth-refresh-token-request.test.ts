import { describe, expect, it, vi } from "vitest";
import AuthAPI from "@/api/auth-api";
import request from "@/utils/request";

vi.mock("@/utils/request", () => ({
  default: vi.fn(),
}));

describe("AuthAPI.refreshToken", () => {
  it("uses request body instead of query params for refresh token", () => {
    AuthAPI.refreshToken("refresh-token");

    expect(request).toHaveBeenCalledWith(
      expect.objectContaining({
        data: { refreshToken: "refresh-token" },
      })
    );
    expect(vi.mocked(request).mock.calls[0]?.[0]).not.toHaveProperty("params");
  });
});
