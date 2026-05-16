import axios, { type InternalAxiosRequestConfig, type AxiosResponse } from "axios";
import qs from "qs";
import { ApiCodeEnum } from "@/enums/api/code-enum";
import { AuthStorage, redirectToLogin } from "@/utils/auth";
import { useTokenRefresh } from "@/composables/auth/useTokenRefresh";
import { authConfig } from "@/settings";
import { getApiErrorMessage } from "@/utils/api-error";

// 初始化token刷新组合式函数
const { refreshTokenAndRetry } = useTokenRefresh();

// 获取 API 版本前缀
const apiVersion = import.meta.env.VITE_APP_API_VERSION;

/**
 * 创建 HTTP 请求实例
 */
const httpRequest = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 50000,
  headers: { "Content-Type": "application/json;charset=utf-8" },
  paramsSerializer: (params) => qs.stringify(params),
});

/**
 * 请求拦截器 - 添加 Authorization 头
 */
httpRequest.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = AuthStorage.getAccessToken();

    // 如果 Authorization 设置为 no-auth，则不携带 Token
    if (config.headers.Authorization !== "no-auth" && accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    } else {
      delete config.headers.Authorization;
    }

    // 自动添加版本前缀
    if (apiVersion && config.url?.startsWith("/api/") && !config.url.includes(`/${apiVersion}/`)) {
      config.url = config.url.replace("/api/", `/api/${apiVersion}/`);
    }

    return config;
  },
  (error) => {
    console.error("Request interceptor error:", error);
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器 - 统一处理响应和错误
 */
httpRequest.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 如果响应是二进制数据，则直接返回response对象（用于文件下载、Excel导出、图片显示等）
    if (response.config.responseType === "blob" || response.config.responseType === "arraybuffer") {
      return response;
    }

    // 新增：处理204状态码（无内容）的DELETE请求
    if (response.status === 204 && response.config.method?.toUpperCase() === "DELETE") {
      // 返回模拟的成功响应数据
      return { success: true };
    }

    const { code, data } = response.data || {}; // 增加空对象默认值防止解构错误

    // 请求成功
    if (code === ApiCodeEnum.SUCCESS) {
      return data;
    }

    // 业务错误
    const errorMessage = getApiErrorMessage(response.data, "系统出错");
    ElMessage.error(errorMessage);
    return Promise.reject(new Error(errorMessage));
  },
  async (error) => {
    console.error("Response interceptor error:", error);

    const { config, response } = error;

    // 网络错误或服务器无响应
    if (!response) {
      ElMessage.error("网络连接失败，请检查网络设置");
      return Promise.reject(error);
    }

    const responseData = response.data as ApiResponse | undefined;
    const code = responseData?.code;
    const errorMessage = getApiErrorMessage(responseData, "请求失败");

    switch (code) {
      case ApiCodeEnum.ACCESS_TOKEN_INVALID:
        // Access Token 过期
        if (authConfig.enableTokenRefresh) {
          // 启用了token刷新，尝试刷新
          return refreshTokenAndRetry(config, httpRequest);
        } else {
          // 未启用token刷新，直接跳转登录页
          await redirectToLogin("登录已过期");
          return Promise.reject(
            new Error(getApiErrorMessage(responseData, "Access Token Invalid"))
          );
        }

      case ApiCodeEnum.REFRESH_TOKEN_INVALID:
        // Refresh Token 过期，跳转登录页
        await redirectToLogin("登录已过期");
        return Promise.reject(new Error(getApiErrorMessage(responseData, "Refresh Token Invalid")));

      default:
        console.error("Response interceptor error:", response.data);
        ElMessage.error(errorMessage);
        return Promise.reject(new Error(errorMessage));
    }
  }
);

export default httpRequest;
