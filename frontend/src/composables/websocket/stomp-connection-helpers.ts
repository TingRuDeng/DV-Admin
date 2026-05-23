import type { StompErrorFrame } from "./stomp-connection-types";

const RECOVERABLE_CLOSE_CODES = new Set([1000, 1006, 1008]);

interface ReconnectDelayOptions {
  maxReconnectDelay?: number;
  reconnectCount: number;
  reconnectDelay: number;
  useExponentialBackoff?: boolean;
}

export function isRecoverableCloseCode(code?: number) {
  return code !== undefined && RECOVERABLE_CLOSE_CODES.has(code);
}

export function calculateReconnectDelay(options: ReconnectDelayOptions) {
  if (!options.useExponentialBackoff) {
    return options.reconnectDelay;
  }
  return Math.min(
    options.reconnectDelay * Math.pow(2, options.reconnectCount - 1),
    options.maxReconnectDelay ?? Number.POSITIVE_INFINITY
  );
}

export function isUnauthorizedFrame(frame: StompErrorFrame) {
  return (
    frame.headers?.message?.includes("Unauthorized") ||
    frame.body?.includes("Unauthorized") ||
    frame.body?.includes("Token")
  );
}
