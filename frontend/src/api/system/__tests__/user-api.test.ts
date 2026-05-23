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
