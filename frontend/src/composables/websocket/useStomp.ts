import type { IMessage } from "@stomp/stompjs";
import { AuthStorage } from "@/utils/auth";
import { createLogger } from "@/utils/logger";
import { createStompConnectionManager } from "@/composables/websocket/stomp-connection-manager";

export interface UseStompOptions {
  /** WebSocket 地址，不传时使用 VITE_APP_WS_ENDPOINT 环境变量 */
  brokerURL?: string;
  /** 用于鉴权的 token，不传时使用 getAccessToken() 的返回值 */
  token?: string;
  /** 重连延迟，单位毫秒，默认为 8000 */
  reconnectDelay?: number;
  /** 连接超时时间，单位毫秒，默认为 10000 */
  connectionTimeout?: number;
  /** 是否开启指数退避重连策略 */
  useExponentialBackoff?: boolean;
  /** 最大重连次数，默认为 5 */
  maxReconnectAttempts?: number;
  /** 最大重连延迟，单位毫秒，默认为 60000 */
  maxReconnectDelay?: number;
  /** 是否开启调试日志 */
  debug?: boolean;
}

const DEFAULT_RECONNECT_DELAY = 15000;
const DEFAULT_CONNECTION_TIMEOUT = 10000;
const DEFAULT_MAX_RECONNECT_ATTEMPTS = 3;
const DEFAULT_MAX_RECONNECT_DELAY = 60000;

/**
 * STOMP WebSocket 组合式函数，负责把 Vue 响应式状态映射到连接管理器。
 */
export function useStomp(options: UseStompOptions = {}) {
  const logger = createLogger("useStomp", { debugEnabled: options.debug });
  const brokerURL = ref(options.brokerURL ?? import.meta.env.VITE_APP_WS_ENDPOINT ?? "");
  const isConnected = ref(false);
  const reconnectCount = ref(0);

  const manager = createStompConnectionManager({
    brokerURL: brokerURL.value,
    connectionTimeout: options.connectionTimeout ?? DEFAULT_CONNECTION_TIMEOUT,
    debug: options.debug,
    getToken: () => options.token || AuthStorage.getAccessToken(),
    logger,
    maxReconnectAttempts: options.maxReconnectAttempts ?? DEFAULT_MAX_RECONNECT_ATTEMPTS,
    maxReconnectDelay: options.maxReconnectDelay ?? DEFAULT_MAX_RECONNECT_DELAY,
    onConnectedChange: (value) => {
      isConnected.value = value;
    },
    onReconnectCountChange: (value) => {
      reconnectCount.value = value;
    },
    reconnectDelay: options.reconnectDelay ?? DEFAULT_RECONNECT_DELAY,
    useExponentialBackoff: options.useExponentialBackoff ?? false,
  });

  watch(brokerURL, (newURL) => {
    manager.updateBrokerURL(newURL);
  });

  const subscribe = (destination: string, callback: (_message: IMessage) => void): string => {
    return manager.subscribe(destination, callback);
  };

  return {
    isConnected,
    connect: manager.connect,
    subscribe,
    unsubscribe: manager.unsubscribe,
    disconnect: manager.disconnect,
  };
}
