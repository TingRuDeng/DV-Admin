import type { StompConnectionSnapshot } from "./stomp-connection-types";

interface StompConnectionStateOptions {
  onConnectedChange?: (_value: boolean) => void;
  onReconnectCountChange?: (_value: number) => void;
}

export function createStompConnectionState(options: StompConnectionStateOptions) {
  let isConnected = false;
  let reconnectCount = 0;

  const setConnected = (value: boolean) => {
    isConnected = value;
    options.onConnectedChange?.(value);
  };

  const setReconnectCount = (value: number) => {
    reconnectCount = value;
    options.onReconnectCountChange?.(value);
  };

  const getConnected = () => isConnected;

  const getReconnectCount = () => reconnectCount;

  const getSnapshot = (): StompConnectionSnapshot => ({
    isConnected,
    reconnectCount,
  });

  return {
    getConnected,
    getReconnectCount,
    getSnapshot,
    setConnected,
    setReconnectCount,
  };
}
