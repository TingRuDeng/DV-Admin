import { afterEach, describe, expect, it, vi } from "vitest";
import InformationAPI from "@/api/information-api";
import request from "@/utils/request";

vi.mock("@/utils/request", () => ({
  default: vi.fn(),
}));

describe("InformationAPI shared backend contract", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("uses the canonical password path and field names", () => {
    const data = {
      oldPassword: "oldpass123",
      newPassword: "newpass123",
      confirmPassword: "newpass123",
    };

    InformationAPI.changePassword(data);

    expect(request).toHaveBeenCalledWith({
      url: "/api/information/password",
      method: "put",
      data,
    });
  });

  it("uploads avatars through the shared file field", () => {
    const file = new File(["avatar"], "avatar.png", { type: "image/png" });

    InformationAPI.updateAvatar(file);

    const config = vi.mocked(request).mock.calls[0]?.[0] as {
      data?: unknown;
      method?: string;
      url?: string;
    };
    expect(config).toEqual(
      expect.objectContaining({
        url: "/api/information/change-avatar/",
        method: "post",
      })
    );
    expect(config?.data).toBeInstanceOf(FormData);
    expect((config?.data as FormData).get("file")).toBe(file);
    expect((config?.data as FormData).get("image")).toBeNull();
  });
});
