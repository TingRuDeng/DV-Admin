import { AuthStorage } from "@/utils/auth";
import { createLogger } from "@/utils/logger";

interface WebSocketRegistryInstance {
  disconnect?: () => void;
  closeWebSocket?: () => void;
}

const websocketInstances = new Map<string, WebSocketRegistryInstance>();
let isInitialized = false;
const logger = createLogger("WebSocketPlugin");

export function registerWebSocketInstance(key: string, instance: WebSocketRegistryInstance) {
  websocketInstances.set(key, instance);
  logger.debug(`Registered WebSocket instance: ${key}`);
}

export function getWebSocketInstance(key: string) {
  return websocketInstances.get(key);
}

export function setupWebSocket() {
  logger.info("开始初始化WebSocket服务...");
  if (isInitialized) {
    logger.debug("WebSocket服务已经初始化，跳过重复初始化");
    return;
  }

  const wsEndpoint = import.meta.env.VITE_APP_WS_ENDPOINT;
  if (!wsEndpoint) {
    logger.debug("未配置WebSocket端点，跳过WebSocket初始化");
    return;
  }
  if (!AuthStorage.getAccessToken()) {
    logger.warn("未找到访问令牌，WebSocket初始化已跳过。用户登录后将自动重新连接。");
    return;
  }

  try {
    setTimeout(() => {
      import("@/composables/websocket/useOnlineCount").then(({ useOnlineCount }) => {
        const onlineCountInstance = useOnlineCount({ autoInit: false });
        registerWebSocketInstance("onlineCount", onlineCountInstance);
        onlineCountInstance.initWebSocket();
        logger.info("在线用户计数WebSocket初始化完成");
      });

      window.addEventListener("beforeunload", handleWindowClose);
      logger.info("WebSocket服务初始化完成");
      isInitialized = true;
    }, 1000);
  } catch (error) {
    logger.error("初始化WebSocket服务失败:", error);
  }
}

function handleWindowClose() {
  logger.info("窗口即将关闭，断开WebSocket连接");
  cleanupWebSocket();
}

export function cleanupWebSocket() {
  websocketInstances.forEach((instance, key) => {
    try {
      if (typeof instance.disconnect === "function") {
        instance.disconnect();
      } else if (typeof instance.closeWebSocket === "function") {
        instance.closeWebSocket();
      }
      logger.info(`${key} WebSocket连接已断开`);
    } catch (error) {
      logger.error(`断开 ${key} WebSocket连接失败:`, error);
    }
  });
  websocketInstances.clear();
  window.removeEventListener("beforeunload", handleWindowClose);
  isInitialized = false;
}

export function reinitializeWebSocket() {
  cleanupWebSocket();
  setTimeout(() => setupWebSocket(), 500);
}
