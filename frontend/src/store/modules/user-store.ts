import { store } from "@/store";

import AuthAPI, { type LoginFormData, type OidcLoginData, type UserInfo } from "@/api/auth-api";

import { AuthStorage } from "@/utils/auth";
import { usePermissionStoreHook } from "@/store/modules/permission-store";
import { useTagsViewStore } from "@/store";
import { cleanupWebSocket } from "@/plugins/websocket";
import { createLogger } from "@/utils/logger";
import { resolveStaticAssetUrl } from "@/utils/static-asset-url";
import { isOidcEnabled } from "@/views/login/oidc-flow";

const userStoreLogger = createLogger("userStore");

function createEmptyUserInfo(): UserInfo {
  return {
    roles: [],
    perms: [],
  };
}

export const useUserStore = defineStore("user", () => {
  // 用户信息
  const userInfo = ref<UserInfo>(createEmptyUserInfo());
  // 记住我状态
  const rememberMe = ref(AuthStorage.getRememberMe());

  /**
   * 登录
   *
   * @param {LoginFormData}
   * @returns
   */
  function login(LoginFormData: LoginFormData) {
    return new Promise<void>((resolve, reject) => {
      AuthAPI.login(LoginFormData)
        .then((data) => {
          const { accessToken, refreshToken } = data;
          // 保存记住我状态和token
          rememberMe.value = LoginFormData.rememberMe;
          AuthStorage.setTokens(accessToken, refreshToken, rememberMe.value);
          resolve();
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  /**
   * 单点登录：用身份提供方回调的授权码换取本地令牌，存储方式沿用当前的记住我设置
   */
  async function loginWithOidc(data: OidcLoginData) {
    const { accessToken, refreshToken } = await AuthAPI.oidcLogin(data);
    AuthStorage.setTokens(accessToken, refreshToken, rememberMe.value);
  }

  /**
   * 获取用户信息
   *
   * @returns {UserInfo} 用户信息
   */
  function getUserInfo() {
    return new Promise<UserInfo>((resolve, reject) => {
      AuthAPI.getInfo()
        .then((data) => {
          if (!data) {
            reject("Verification failed, please Login again.");
            return;
          }
          userInfo.value = {
            ...data,
            avatar: resolveStaticAssetUrl(data.avatar),
            roles: Array.isArray(data.roles) ? data.roles : [],
            perms: Array.isArray(data.perms) ? data.perms : [],
          };
          resolve(data);
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  /**
   * 登出
   */
  /**
   * 退出登录；单点登录用户在本地退出后跳转到身份提供方的退出地址，结束 IdP 会话
   * @returns 需要跳转的 IdP 退出地址，没有时为 null
   */
  async function logout(): Promise<string | null> {
    // 先拿退出地址：本地令牌清掉之后就无法再调用需要认证的接口
    const endSessionUrl = isOidcEnabled()
      ? await AuthAPI.oidcEndSession()
          .then((data) => data.endSessionUrl)
          .catch(() => null)
      : null;
    try {
      await AuthAPI.logout(AuthStorage.getRefreshToken() || undefined);
    } finally {
      await resetAllState();
    }
    return endSessionUrl;
  }

  /**
   * 重置所有系统状态
   * 统一处理所有清理工作，包括用户凭证、路由、缓存等
   */
  function resetAllState() {
    // 1. 重置用户状态
    resetUserState();

    // 2. 重置其他模块状态
    // 重置路由
    usePermissionStoreHook().resetRouter();
    // 清除标签视图
    useTagsViewStore().delAllViews();

    // 3. 清理 WebSocket 连接
    cleanupWebSocket();

    return Promise.resolve();
  }

  /**
   * 重置用户状态
   * 仅处理用户模块内的状态
   */
  function resetUserState() {
    // 清除用户凭证
    AuthStorage.clearAuth();
    // 重置用户信息
    userInfo.value = createEmptyUserInfo();
  }

  /**
   * 刷新 token
   */
  function refreshToken() {
    const refreshToken = AuthStorage.getRefreshToken();

    if (!refreshToken) {
      return Promise.reject(new Error("没有有效的刷新令牌"));
    }

    return new Promise<void>((resolve, reject) => {
      AuthAPI.refreshToken(refreshToken)
        .then((data) => {
          const { accessToken, refreshToken: newRefreshToken } = data;
          // 更新令牌，保持当前记住我状态
          AuthStorage.setTokens(accessToken, newRefreshToken, AuthStorage.getRememberMe());
          resolve();
        })
        .catch((error) => {
          userStoreLogger.error("refreshToken 刷新失败:", error);
          reject(error);
        });
    });
  }

  return {
    userInfo,
    rememberMe,
    isLoggedIn: () => !!AuthStorage.getAccessToken(),
    getUserInfo,
    login,
    loginWithOidc,
    logout,
    resetAllState,
    resetUserState,
    refreshToken,
  };
});

/**
 * 在组件外部使用UserStore的钩子函数
 * @see https://pinia.vuejs.org/core-concepts/outside-component-usage.html
 */
export function useUserStoreHook() {
  return useUserStore(store);
}
