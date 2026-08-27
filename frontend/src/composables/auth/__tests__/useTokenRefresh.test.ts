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
    url: "/api/mock-token-refresh",
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
        _tokenRefreshRetried: true,
        headers: expect.objectContaining({
          Authorization: "Bearer new-access-token",
        }),
      })
    );
  });

  it("stops after one retry when the access token is still invalid", async () => {
    const { refreshTokenAndRetry } = useTokenRefresh();
    const config = createRequestConfig() as InternalAxiosRequestConfig & {
      _tokenRefreshRetried?: boolean;
    };
    config._tokenRefreshRetried = true;
    const request = vi.fn();

    await expect(refreshTokenAndRetry(config, request)).rejects.toThrow(
      "Access token remained invalid after refresh"
    );

    expect(mocks.refreshToken).not.toHaveBeenCalled();
    expect(request).not.toHaveBeenCalled();
    expect(mocks.redirectToLogin).toHaveBeenCalledWith("登录状态已失效，请重新登录");
  });

  it("rejects the original promise when retry throws synchronously", async () => {
    mocks.refreshToken.mockResolvedValue();
    const { refreshTokenAndRetry } = useTokenRefresh();
    const request = vi.fn(() => {
      throw new Error("synchronous request failure");
    });

    await expect(refreshTokenAndRetry(createRequestConfig(), request)).rejects.toThrow(
      "synchronous request failure"
    );
  });

  it("rejects queued requests before an unfinished login redirect", async () => {
    mocks.refreshToken.mockRejectedValue(new Error("refresh failed"));
    mocks.redirectToLogin.mockReturnValue(new Promise(() => undefined));
    const { refreshTokenAndRetry } = useTokenRefresh();

    const result = await waitForSettlement(refreshTokenAndRetry(createRequestConfig(), vi.fn()));

    expect(result).toBe("rejected:Token refresh failed");
  });

  it("deduplicates concurrent refreshes and retries every queued request", async () => {
    let resolveRefresh: (() => void) | undefined;
    mocks.refreshToken.mockReturnValue(
      new Promise<void>((resolve) => {
        resolveRefresh = resolve;
      })
    );
    const { refreshTokenAndRetry, getRefreshStatus } = useTokenRefresh();
    const firstRequest = vi.fn().mockResolvedValue("first");
    const secondRequest = vi.fn().mockResolvedValue("second");

    const first = refreshTokenAndRetry(createRequestConfig(), firstRequest);
    const second = refreshTokenAndRetry(createRequestConfig(), secondRequest);
    await Promise.resolve();

    expect(mocks.refreshToken).toHaveBeenCalledTimes(1);
    expect(getRefreshStatus()).toEqual({
      isRefreshing: true,
      pendingCount: 2,
    });

    resolveRefresh?.();
    await expect(first).resolves.toBe("first");
    await expect(second).resolves.toBe("second");
    expect(firstRequest).toHaveBeenCalledTimes(1);
    expect(secondRequest).toHaveBeenCalledTimes(1);
    expect(getRefreshStatus()).toEqual({
      isRefreshing: false,
      pendingCount: 0,
    });
  });
});
