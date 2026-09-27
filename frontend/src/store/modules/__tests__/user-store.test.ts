import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AuthAPI from "@/api/auth-api";
import { cleanupWebSocket } from "@/plugins/websocket";
import { useUserStore } from "@/store/modules/user-store";
import { AuthStorage } from "@/utils/auth";

vi.mock("@/api/auth-api", () => ({
  default: {
    getInfo: vi.fn(),
    getRoutes: vi.fn(),
    login: vi.fn(),
    logout: vi.fn(),
    oidcEndSession: vi.fn(),
    refreshToken: vi.fn(),
  },
}));

vi.mock("@/plugins/websocket", () => ({
  cleanupWebSocket: vi.fn(),
}));

const loginResult = {
  accessToken: "access-token",
  refreshToken: "refresh-token",
  tokenType: "Bearer",
  expiresIn: 1800,
};

describe("useUserStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it("stores access and refresh tokens after login", async () => {
    vi.mocked(AuthAPI.login).mockResolvedValue(loginResult);
    const setTokensSpy = vi.spyOn(AuthStorage, "setTokens");
    const userStore = useUserStore();

    await userStore.login({
      username: "admin",
      password: "123456",
      captchaKey: "captcha-key",
      captchaCode: "0000",
      rememberMe: true,
    });

    expect(setTokensSpy).toHaveBeenCalledWith("access-token", "refresh-token", true);
    expect(userStore.rememberMe).toBe(true);
  });

  it("merges fetched user info into store state", async () => {
    vi.mocked(AuthAPI.getInfo).mockResolvedValue({
      id: "1",
      username: "admin",
      name: "管理员",
      roles: ["ROOT"],
      perms: ["system:user:list"],
    });
    const userStore = useUserStore();

    await userStore.getUserInfo();

    expect(userStore.userInfo).toMatchObject({
      username: "admin",
      roles: ["ROOT"],
      perms: ["system:user:list"],
    });
  });

  it("clears credentials and websocket state when resetting all state", async () => {
    const clearAuthSpy = vi.spyOn(AuthStorage, "clearAuth");
    const userStore = useUserStore();
    userStore.userInfo = {
      username: "admin",
      roles: ["ROOT"],
      perms: ["system:user:list"],
    };

    await userStore.resetAllState();

    expect(clearAuthSpy).toHaveBeenCalled();
    expect(cleanupWebSocket).toHaveBeenCalled();
    expect(userStore.userInfo).toEqual({
      roles: [],
      perms: [],
    });
  });

  it("refreshes token with current remember-me preference", async () => {
    vi.spyOn(AuthStorage, "getRefreshToken").mockReturnValue("old-refresh-token");
    vi.spyOn(AuthStorage, "getRememberMe").mockReturnValue(true);
    const setTokensSpy = vi.spyOn(AuthStorage, "setTokens");
    vi.mocked(AuthAPI.refreshToken).mockResolvedValue({
      accessToken: "new-access-token",
      refreshToken: "new-refresh-token",
      tokenType: "Bearer",
      expiresIn: 1800,
    });
    const userStore = useUserStore();

    await userStore.refreshToken();

    expect(AuthAPI.refreshToken).toHaveBeenCalledWith("old-refresh-token");
    expect(setTokensSpy).toHaveBeenCalledWith("new-access-token", "new-refresh-token", true);
  });

  it("sends the session refresh token on logout so the server can revoke it", async () => {
    vi.mocked(AuthAPI.logout).mockResolvedValue({} as Awaited<ReturnType<typeof AuthAPI.logout>>);
    vi.spyOn(AuthStorage, "getRefreshToken").mockReturnValue("session-refresh-token");
    const clearAuthSpy = vi.spyOn(AuthStorage, "clearAuth");
    const userStore = useUserStore();

    await userStore.logout();

    expect(AuthAPI.logout).toHaveBeenCalledWith("session-refresh-token");
    expect(clearAuthSpy).toHaveBeenCalled();
  });

  it("returns the IdP end-session URL for single sign-on users when OIDC is enabled", async () => {
    vi.stubEnv("VITE_OIDC_ENABLED", "true");
    vi.mocked(AuthAPI.oidcEndSession).mockResolvedValue({
      endSessionUrl: "https://idp.example/logout?post_logout_redirect_uri=x",
    });
    vi.mocked(AuthAPI.logout).mockResolvedValue({} as Awaited<ReturnType<typeof AuthAPI.logout>>);
    const userStore = useUserStore();

    await expect(userStore.logout()).resolves.toBe(
      "https://idp.example/logout?post_logout_redirect_uri=x"
    );
    // 退出地址必须在本地令牌清除之前取到
    expect(vi.mocked(AuthAPI.oidcEndSession).mock.invocationCallOrder[0]).toBeLessThan(
      vi.mocked(AuthAPI.logout).mock.invocationCallOrder[0]
    );
    vi.unstubAllEnvs();
  });

  it("skips the end-session lookup when OIDC is disabled or the lookup fails", async () => {
    vi.mocked(AuthAPI.logout).mockResolvedValue({} as Awaited<ReturnType<typeof AuthAPI.logout>>);
    vi.stubEnv("VITE_OIDC_ENABLED", "false");
    await expect(useUserStore().logout()).resolves.toBeNull();
    expect(AuthAPI.oidcEndSession).not.toHaveBeenCalled();

    vi.stubEnv("VITE_OIDC_ENABLED", "true");
    vi.mocked(AuthAPI.oidcEndSession).mockRejectedValue(new Error("offline"));
    await expect(useUserStore().logout()).resolves.toBeNull();
    expect(AuthAPI.logout).toHaveBeenCalledTimes(2);
    vi.unstubAllEnvs();
  });

  it("clears local credentials on explicit logout even when revocation fails", async () => {
    const unavailable = Object.assign(new Error("Service unavailable"), { status: 503 });
    vi.mocked(AuthAPI.logout).mockRejectedValue(unavailable);
    const clearAuthSpy = vi.spyOn(AuthStorage, "clearAuth");
    const userStore = useUserStore();
    await expect(userStore.logout()).rejects.toBe(unavailable);
    expect(clearAuthSpy).toHaveBeenCalled();
    expect(cleanupWebSocket).toHaveBeenCalled();
    expect(userStore.userInfo).toEqual({ roles: [], perms: [] });
  });
});
