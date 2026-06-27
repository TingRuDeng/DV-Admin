import type { IMessage } from "@stomp/stompjs";
import {
  calculateReconnectDelay,
  isUnauthorizedFrame,
  isRecoverableCloseCode,
} from "@/composables/websocket/stomp-connection-helpers";
import { buildStompClient } from "@/composables/websocket/stomp-client-factory";
import { createStompConnectionTimers } from "@/composables/websocket/stomp-connection-timers";
import { createStompSubscriptionRegistry } from "@/composables/websocket/stomp-subscription-registry";
import type {
  StompClientLike,
  StompConnectionManagerOptions,
  StompConnectionSnapshot,
  StompErrorFrame,
} from "@/composables/websocket/stomp-connection-types";

export {
  calculateReconnectDelay,
  isRecoverableCloseCode,
  isUnauthorizedFrame,
} from "./stomp-connection-helpers";
export type {
  StompClientLike,
  StompConnectionManagerOptions,
  StompConnectionSnapshot,
  StompErrorFrame,
} from "./stomp-connection-types";

export function createStompConnectionManager(options: StompConnectionManagerOptions) {
  let brokerURL = options.brokerURL;
  let client: StompClientLike | null = null;
  let isConnected = false;
  let isConnecting = false;
  let isManualDisconnect = false;
  let reconnectCount = 0;
  const subscriptionRegistry = createStompSubscriptionRegistry(options.logger);
  const timers = createStompConnectionTimers();

  const setConnected = (value: boolean) => {
    isConnected = value;
    options.onConnectedChange?.(value);
  };

  const setReconnectCount = (value: number) => {
    reconnectCount = value;
    options.onReconnectCountChange?.(value);
  };

  const createClient = () => {
    if (client && (client.active || client.connected)) {
      options.logger.debug("STOMP客户端已存在且处于活动状态，跳过初始化");
      return;
    }

    if (!brokerURL) {
      options.logger.warn("WebSocket连接失败: 未配置WebSocket端点URL");
      return;
    }

    const currentToken = options.getToken();
    if (!currentToken) {
      options.logger.warn("WebSocket连接失败：授权令牌为空，请先登录");
      return;
    }

    cleanupOldClient();
    client = buildStompClient({
      brokerURL,
      clientFactory: options.clientFactory,
      debug: options.debug,
      logger: options.logger,
      token: currentToken,
    });
    bindClientEvents(client);
  };

  const cleanupOldClient = () => {
    if (!client) {
      return;
    }

    try {
      client.deactivate();
    } catch (error) {
      options.logger.warn("清理旧客户端时出错:", error);
    }
    client = null;
  };

  const bindClientEvents = (targetClient: StompClientLike) => {
    targetClient.onConnect = () => {
      setConnected(true);
      isConnecting = false;
      setReconnectCount(0);
      timers.clearConnectionTimeoutTimer();
      timers.clearReconnectTimer();
      options.logger.info("WebSocket连接已建立");
    };

    targetClient.onDisconnect = () => {
      setConnected(false);
      isConnecting = false;
      options.logger.info("WebSocket连接已断开");
      if (!isManualDisconnect && reconnectCount < options.maxReconnectAttempts) {
        scheduleReconnect();
      }
    };

    targetClient.onWebSocketClose = (event) => {
      handleWebSocketClose(event);
    };

    targetClient.onStompError = (frame) => {
      handleStompError(frame);
    };
  };

  const handleWebSocketClose = (event: CloseEvent) => {
    setConnected(false);
    isConnecting = false;
    options.logger.info(`WebSocket已关闭: ${event?.code} ${event?.reason}`);

    if (isManualDisconnect) {
      options.logger.debug("手动断开连接，不进行重连");
      return;
    }

    if (isRecoverableCloseCode(event?.code) && reconnectCount < options.maxReconnectAttempts) {
      options.logger.info("检测到连接异常关闭，将尝试重连");
      scheduleReconnect();
    }
  };

  const handleStompError = (frame: StompErrorFrame) => {
    options.logger.error("STOMP错误:", frame.headers, frame.body);
    isConnecting = false;

    if (isUnauthorizedFrame(frame)) {
      options.logger.warn("WebSocket授权错误，请检查登录状态");
      isManualDisconnect = true;
    }
  };

  const scheduleReconnect = () => {
    if (isConnecting || isManualDisconnect) {
      return;
    }

    if (reconnectCount >= options.maxReconnectAttempts) {
      options.logger.error(`已达到最大重连次数(${options.maxReconnectAttempts})，停止重连`);
      return;
    }

    setReconnectCount(reconnectCount + 1);
    options.logger.info(`准备重连(${reconnectCount}/${options.maxReconnectAttempts})...`);
    timers.startReconnectTimer(runReconnect, getReconnectDelay());
  };

  const runReconnect = () => {
    if (!isConnected && !isManualDisconnect && !isConnecting) {
      options.logger.info("开始重连...");
      connect();
    }
  };

  const getReconnectDelay = () => {
    return calculateReconnectDelay({
      maxReconnectDelay: options.maxReconnectDelay,
      reconnectCount,
      reconnectDelay: options.reconnectDelay,
      useExponentialBackoff: options.useExponentialBackoff,
    });
  };

  const connect = () => {
    isManualDisconnect = false;

    if (!brokerURL) {
      options.logger.error("WebSocket连接失败: 未配置WebSocket端点URL");
      return;
    }

    if (isConnecting) {
      options.logger.debug("WebSocket正在连接中，跳过重复连接请求");
      return;
    }

    if (!client) {
      createClient();
    }

    activateClient();
  };

  const activateClient = () => {
    if (!client) {
      options.logger.error("STOMP客户端初始化失败");
      return;
    }

    if (client.connected) {
      options.logger.debug("WebSocket已经连接,跳过重复连接");
      setConnected(true);
      return;
    }

    isConnecting = true;
    timers.startConnectionTimeoutTimer(handleConnectionTimeout, options.connectionTimeout);

    try {
      client.activate();
      options.logger.info("正在建立WebSocket连接...");
    } catch (error) {
      options.logger.error("激活WebSocket连接失败:", error);
      isConnecting = false;
    }
  };

  const handleConnectionTimeout = () => {
    if (!isConnected && isConnecting) {
      options.logger.warn("WebSocket连接超时");
      isConnecting = false;
      if (!isManualDisconnect && reconnectCount < options.maxReconnectAttempts) {
        scheduleReconnect();
      }
    }
  };

  const subscribe = (destination: string, callback: (_message: IMessage) => void): string => {
    return subscriptionRegistry.subscribe(client, destination, callback);
  };

  const unsubscribe = (subscriptionId: string) => {
    subscriptionRegistry.unsubscribe(subscriptionId);
  };

  const disconnect = () => {
    isManualDisconnect = true;
    timers.clearAllTimers();
    subscriptionRegistry.clear();
    deactivateClient();
    setConnected(false);
    isConnecting = false;
    setReconnectCount(0);
  };

  const deactivateClient = () => {
    if (!client) {
      return;
    }

    try {
      if (client.connected || client.active) {
        client.deactivate();
        options.logger.info("WebSocket连接已主动断开");
      }
    } catch (error) {
      options.logger.error("断开WebSocket连接时出错:", error);
    }
    client = null;
  };

  const updateBrokerURL = (nextBrokerURL: string) => {
    if (nextBrokerURL === brokerURL) {
      return;
    }
    options.logger.info(`brokerURL changed from ${brokerURL} to ${nextBrokerURL}`);
    if (client?.connected) {
      client.deactivate();
    }
    brokerURL = nextBrokerURL;
    createClient();
  };

  const getSnapshot = (): StompConnectionSnapshot => ({
    isConnected,
    reconnectCount,
  });

  createClient();

  return {
    connect,
    disconnect,
    getSnapshot,
    subscribe,
    unsubscribe,
    updateBrokerURL,
  };
}
