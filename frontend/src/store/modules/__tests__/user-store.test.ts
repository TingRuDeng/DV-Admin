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
});
