import type { InternalAxiosRequestConfig } from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useTokenRefresh } from "@/composables/auth/useTokenRefresh";

const mocks = vi.hoisted(() => ({
  refreshToken: vi.fn<() => Promise<void>>(),
  getAccessToken: vi.fn<() => string>(),
  redirectToLogin: vi.fn<() => Promise<void>>(),
}));

vi.mock("@/store/modules/user-store", () => ({
  useUserStoreHook: () => ({
    refreshToken: mocks.refreshToken,
  }),
}));

vi.mock("@/utils/auth", () => ({
  AuthStorage: {
    getAccessToken: mocks.getAccessToken,
  },
  redirectToLogin: mocks.redirectToLogin,
}));

vi.mock("@/utils/logger", () => ({
  createLogger: () => ({
    error: vi.fn(),
  }),
}));

function createRequestConfig() {
  return {
    headers: {},
    url: "/api/test",
  } as InternalAxiosRequestConfig;
}

async function waitForSettlement(promise: Promise<unknown>) {
  return Promise.race([
    promise.then(
      () => "resolved",
      (error) => (error instanceof Error ? `rejected:${error.message}` : "rejected")
    ),
    new Promise((resolve) => setTimeout(() => resolve("pending"), 0)),
  ]);
}

describe("useTokenRefresh", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.getAccessToken.mockReturnValue("new-access-token");
    mocks.redirectToLogin.mockResolvedValue();
  });

  it("rejects queued requests when token refresh fails", async () => {
    mocks.refreshToken.mockRejectedValue(new Error("refresh failed"));

    const { refreshTokenAndRetry } = useTokenRefresh();
    const request = vi.fn();
    const result = await waitForSettlement(refreshTokenAndRetry(createRequestConfig(), request));

    expect(result).toBe("rejected:Token refresh failed");
    expect(mocks.redirectToLogin).toHaveBeenCalledWith("登录状态已失效，请重新登录");
    expect(request).not.toHaveBeenCalled();
  });

  it("retries queued requests with the new token when token refresh succeeds", async () => {
    mocks.refreshToken.mockResolvedValue();

    const { refreshTokenAndRetry } = useTokenRefresh();
    const request = vi.fn().mockResolvedValue("ok");
    await expect(refreshTokenAndRetry(createRequestConfig(), request)).resolves.toBe("ok");

    expect(request).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer new-access-token",
        }),
      })
    );
  });
});
