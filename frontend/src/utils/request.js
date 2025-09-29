import axios from "axios";
import qs from "qs";
import { useUserStoreHook } from "@/store/modules/user.store";
import { isSuccessCode, ResultEnum } from "@/enums/api/result.enum";
import { getAccessToken } from "@/utils/auth";
import router from "@/router";
import { ElMessage } from "element-plus";

// 创建 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 50000,
  headers: { "Content-Type": "application/json;charset=utf-8" },
  paramsSerializer: (params) => qs.stringify(params),
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const accessToken = getAccessToken();
    // 如果 Authorization 设置为 no-auth，则不携带 Token
    if (config.headers.Authorization !== "no-auth" && accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    } else {
      delete config.headers.Authorization;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    // 如果响应是二进制流，则直接返回，用于下载文件、Excel 导出等
    if (response.config.responseType === "blob") {
      return response;
    }

    // 新增：处理204状态码（无内容）的DELETE请求
    if (response.status === 204 && response.config.method?.toUpperCase() === "DELETE") {
      // 返回模拟的成功响应数据
      return { success: true };
    }

    const { code, data, msg, errors } = response.data || {}; // 增加空对象默认值防止解构错误
    // 使用工具函数检查是否成功
    if (isSuccessCode(code)) {
      return data;
    }
    ElMessage.error(errors || "系统出错");
    return Promise.reject(new Error(msg || "Error"));
  },
  async (error) => {
    const { config, response } = error;
    if (response) {
      const { code, errors } = response.data;
      if (code === ResultEnum.ACCESS_TOKEN_INVALID) {
        // Token 过期，刷新 Token
        return handleTokenRefresh(config);
      } else if (code === ResultEnum.REFRESH_TOKEN_INVALID) {
        // 刷新 Token 过期，跳转登录页
        await handleSessionExpired();
        return Promise.reject(new Error(errors || "Error"));
      } else {
        ElMessage.error(errors || "系统出错");
      }
    }
    return Promise.reject(error.message);
  }
);

export default service;

// 是否正在刷新标识，避免重复刷新
let isRefreshing = false;
// 因 Token 过期导致的请求等待队列
const waitingQueue = [];

// 刷新 Token 处理
async function handleTokenRefresh(config) {
  return new Promise((resolve) => {
    // 封装需要重试的请求
    const retryRequest = () => {
      config.headers.Authorization = `Bearer ${getAccessToken()}`;
      resolve(service(config));
    };
    waitingQueue.push(retryRequest);
    if (!isRefreshing) {
      isRefreshing = true;
      useUserStoreHook()
        .refreshToken()
        .then(() => {
          // 依次重试队列中所有请求, 重试后清空队列
          waitingQueue.forEach((callback) => callback());
          waitingQueue.length = 0;
        })
        .catch(async (error) => {
          console.error("handleTokenRefresh error", error);
          // 刷新 Token 失败，跳转登录页
          await handleSessionExpired();
        })
        .finally(() => {
          isRefreshing = false;
        });
    }
  });
}

// 处理会话过期
async function handleSessionExpired() {
  ElNotification({
    title: "提示",
    message: "您的会话已过期，请重新登录",
    type: "info",
  });
  await useUserStoreHook().clearSessionAndCache();
  router.push("/login");
}
