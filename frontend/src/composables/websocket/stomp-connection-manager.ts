import { Client, type IMessage, type StompConfig, type StompSubscription } from "@stomp/stompjs";

interface StompLogger {
  debug: (...args: unknown[]) => void;
  error: (...args: unknown[]) => void;
  info: (...args: unknown[]) => void;
  warn: (...args: unknown[]) => void;
}

interface StompErrorFrame {
  body?: string;
  headers?: Record<string, string | undefined>;
}

export interface StompClientLike {
  active: boolean;
  connected: boolean;
  onConnect?: (..._args: unknown[]) => void;
  onDisconnect?: (..._args: unknown[]) => void;
  onStompError?: (_frame: StompErrorFrame) => void;
  onWebSocketClose?: (_event: CloseEvent) => void;
  activate: () => void;
  deactivate: () => void;
  subscribe: (destination: string, callback: (_message: IMessage) => void) => StompSubscription;
}

export interface StompConnectionManagerOptions {
  brokerURL: string;
  clientFactory?: (_config: StompConfig) => StompClientLike;
  connectionTimeout: number;
  debug?: boolean;
  getToken: () => string;
  logger: StompLogger;
  maxReconnectAttempts: number;
  maxReconnectDelay?: number;
  onConnectedChange?: (_value: boolean) => void;
  onReconnectCountChange?: (_value: number) => void;
  reconnectDelay: number;
  useExponentialBackoff?: boolean;
}

export interface StompConnectionSnapshot {
  isConnected: boolean;
  reconnectCount: number;
}

const DEFAULT_HEARTBEAT_MS = 4000;
const NO_RECONNECT_DELAY = 0;

export function createStompConnectionManager(options: StompConnectionManagerOptions) {
  let brokerURL = options.brokerURL;
  let client: StompClientLike | null = null;
  let isConnected = false;
  let isConnecting = false;
  let isManualDisconnect = false;
  let reconnectCount = 0;
  let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
  let connectionTimeoutTimer: ReturnType<typeof setTimeout> | undefined;
  const subscriptions = new Map<string, StompSubscription>();

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
    client = buildClient(currentToken);
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

  const buildClient = (token: string) => {
    const config: StompConfig = {
      brokerURL,
      connectHeaders: { Authorization: `Bearer ${token}` },
      debug: options.debug ? (message) => options.logger.debug(message) : () => {},
      heartbeatIncoming: DEFAULT_HEARTBEAT_MS,
      heartbeatOutgoing: DEFAULT_HEARTBEAT_MS,
      reconnectDelay: NO_RECONNECT_DELAY,
    };
    return options.clientFactory
      ? options.clientFactory(config)
      : (new Client(config) as StompClientLike);
  };

  const bindClientEvents = (targetClient: StompClientLike) => {
    targetClient.onConnect = () => {
      setConnected(true);
      isConnecting = false;
      setReconnectCount(0);
      clearTimeout(connectionTimeoutTimer);
      clearTimeout(reconnectTimer);
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

    if ([1000, 1006, 1008].includes(event?.code) && reconnectCount < options.maxReconnectAttempts) {
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
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(runReconnect, getReconnectDelay());
  };

  const runReconnect = () => {
    if (!isConnected && !isManualDisconnect && !isConnecting) {
      options.logger.info("开始重连...");
      connect();
    }
  };

  const getReconnectDelay = () => {
    if (!options.useExponentialBackoff) {
      return options.reconnectDelay;
    }
    return Math.min(
      options.reconnectDelay * Math.pow(2, reconnectCount - 1),
      options.maxReconnectDelay ?? Number.POSITIVE_INFINITY
    );
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
    clearTimeout(connectionTimeoutTimer);
    connectionTimeoutTimer = setTimeout(handleConnectionTimeout, options.connectionTimeout);

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
    if (!client || !client.connected) {
      options.logger.warn(`尝试订阅 ${destination} 失败: 客户端未连接`);
      return "";
    }

    try {
      const subscription = client.subscribe(destination, callback);
      subscriptions.set(subscription.id, subscription);
      options.logger.info(`订阅成功: ${destination}, ID: ${subscription.id}`);
      return subscription.id;
    } catch (error) {
      options.logger.error(`订阅 ${destination} 失败:`, error);
      return "";
    }
  };

  const unsubscribe = (subscriptionId: string) => {
    const subscription = subscriptions.get(subscriptionId);
    if (!subscription) {
      return;
    }
    subscription.unsubscribe();
    subscriptions.delete(subscriptionId);
    options.logger.debug(`已取消订阅: ${subscriptionId}`);
  };

  const disconnect = () => {
    isManualDisconnect = true;
    clearManagedTimers();
    clearSubscriptions();
    deactivateClient();
    setConnected(false);
    isConnecting = false;
    setReconnectCount(0);
  };

  const clearManagedTimers = () => {
    clearTimeout(reconnectTimer);
    clearTimeout(connectionTimeoutTimer);
    reconnectTimer = undefined;
    connectionTimeoutTimer = undefined;
  };

  const clearSubscriptions = () => {
    for (const [id, subscription] of subscriptions.entries()) {
      try {
        subscription.unsubscribe();
      } catch (error) {
        options.logger.warn(`取消订阅 ${id} 时出错:`, error);
      }
    }
    subscriptions.clear();
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

function isUnauthorizedFrame(frame: StompErrorFrame) {
  return (
    frame.headers?.message?.includes("Unauthorized") ||
    frame.body?.includes("Unauthorized") ||
    frame.body?.includes("Token")
  );
}
