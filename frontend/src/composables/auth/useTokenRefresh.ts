import type { InternalAxiosRequestConfig } from "axios";
import { useUserStoreHook } from "@/store/modules/user-store";
import { AuthStorage, redirectToLogin } from "@/utils/auth";
import { createLogger } from "@/utils/logger";

const tokenRefreshLogger = createLogger("useTokenRefresh");

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
  httpRequest: any;
  resolve: (value: any) => void;
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
      httpRequest(config).then(resolve).catch(reject);
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

async function rejectPendingRequests(requests: PendingRequest[]) {
  try {
    await redirectToLogin("登录状态已失效，请重新登录");
  } finally {
    // 刷新失败必须拒绝所有等待请求，避免调用方 Promise 永久 pending。
    requests.forEach(({ reject }) => {
      reject(new Error("Token refresh failed"));
    });
  }
}

function startTokenRefresh(state: TokenRefreshState) {
  useUserStoreHook()
    .refreshToken()
    .then(() => {
      retryPendingRequests(drainPendingRequests(state));
    })
    .catch(async (error) => {
      tokenRefreshLogger.error("刷新 Token 失败:", error);
      await rejectPendingRequests(drainPendingRequests(state));
    })
    .finally(() => {
      state.isRefreshingToken = false;
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
    config: InternalAxiosRequestConfig,
    httpRequest: any
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      // 队列项必须保留 reject，刷新失败时才能显式结束每个等待请求。
      state.pendingRequests.push(
        createPendingRequest({
          config,
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
