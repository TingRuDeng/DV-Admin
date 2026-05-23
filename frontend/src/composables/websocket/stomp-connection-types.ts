import type { IMessage, StompConfig, StompSubscription } from "@stomp/stompjs";

export interface StompLogger {
  debug: (...args: unknown[]) => void;
  error: (...args: unknown[]) => void;
  info: (...args: unknown[]) => void;
  warn: (...args: unknown[]) => void;
}

export interface StompErrorFrame {
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
