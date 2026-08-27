import type { InternalAxiosRequestConfig } from "axios";
import { useUserStoreHook } from "@/store/modules/user-store";
import { AuthStorage, redirectToLogin } from "@/utils/auth";
import { createLogger } from "@/utils/logger";

const tokenRefreshLogger = createLogger("useTokenRefresh");

type TokenRefreshHttpRequest = (config: InternalAxiosRequestConfig) => Promise<unknown>;

export type TokenRefreshRequestConfig = InternalAxiosRequestConfig & {
  _tokenRefreshRetried?: boolean;
};

/**
 * 等待刷新结果的请求队列项
 */
interface PendingRequest {
  retry: () => void;
  reject: (error: Error) => void;
}

interface TokenRefreshState {
  isRefreshingToken: boolean;
  pendingRequests: PendingRequest[];
}

interface PendingRequestOptions {
  config: InternalAxiosRequestConfig;
  httpRequest: TokenRefreshHttpRequest;
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
}

function createPendingRequest(options: PendingRequestOptions): PendingRequest {
  const { config, httpRequest, resolve, reject } = options;

  return {
    retry: () => {
      const newToken = AuthStorage.getAccessToken();
      if (newToken && config.headers) {
        config.headers.Authorization = `Bearer ${newToken}`;
      }
      try {
        httpRequest(config).then(resolve).catch(reject);
      } catch (error) {
        reject(error);
      }
    },
    reject: (error) => reject(error),
  };
}

function drainPendingRequests(state: TokenRefreshState) {
  return state.pendingRequests.splice(0);
}

function retryPendingRequests(requests: PendingRequest[]) {
  requests.forEach(({ retry }) => {
    try {
      retry();
    } catch (error) {
      tokenRefreshLogger.error("重试请求失败:", error);
    }
  });
}

function rejectPendingRequests(requests: PendingRequest[]) {
  // 先结束所有等待请求；导航失败或挂起不能阻塞调用方 Promise。
  requests.forEach(({ reject }) => {
    reject(new Error("Token refresh failed"));
  });
  void redirectToLogin("登录状态已失效，请重新登录").catch((error) => {
    tokenRefreshLogger.error("跳转登录页失败:", error);
  });
}

function startTokenRefresh(state: TokenRefreshState) {
  Promise.resolve()
    .then(() => useUserStoreHook().refreshToken())
    .then(() => {
      const requests = drainPendingRequests(state);
      // 重试可能立刻触发新的响应拦截器，必须先结束刷新态。
      state.isRefreshingToken = false;
      retryPendingRequests(requests);
    })
    .catch((error) => {
      tokenRefreshLogger.error("刷新 Token 失败:", error);
      const requests = drainPendingRequests(state);
      state.isRefreshingToken = false;
      rejectPendingRequests(requests);
    });
}

/**
 * Token刷新组合式函数
 */
export function useTokenRefresh() {
  // Token 刷新相关状态
  const state: TokenRefreshState = {
    isRefreshingToken: false,
    pendingRequests: [],
  };

  /**
   * 刷新 Token 并重试请求
   */
  async function refreshTokenAndRetry(
    config: InternalAxiosRequestConfig | undefined,
    httpRequest: TokenRefreshHttpRequest
  ): Promise<unknown> {
    const retryConfig = config as TokenRefreshRequestConfig | undefined;
    if (!retryConfig || retryConfig._tokenRefreshRetried) {
      await redirectToLogin("登录状态已失效，请重新登录");
      throw new Error("Access token remained invalid after refresh");
    }

    // 标记必须在发起刷新前写入，确保重试请求再次返回 40001 时直接终止。
    retryConfig._tokenRefreshRetried = true;

    return new Promise((resolve, reject) => {
      // 队列项必须保留 reject，刷新失败时才能显式结束每个等待请求。
      state.pendingRequests.push(
        createPendingRequest({
          config: retryConfig,
          httpRequest,
          resolve,
          reject,
        })
      );

      if (state.isRefreshingToken) {
        return;
      }

      state.isRefreshingToken = true;
      startTokenRefresh(state);
    });
  }

  /**
   * 获取刷新状态（用于外部判断）
   */
  function getRefreshStatus() {
    return {
      isRefreshing: state.isRefreshingToken,
      pendingCount: state.pendingRequests.length,
    };
  }

  return {
    refreshTokenAndRetry,
    getRefreshStatus,
  };
}
