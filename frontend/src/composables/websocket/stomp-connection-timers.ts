type TimerHandle = ReturnType<typeof setTimeout>;

export function createStompConnectionTimers() {
  let reconnectTimer: TimerHandle | undefined;
  let connectionTimeoutTimer: TimerHandle | undefined;

  const startReconnectTimer = (callback: () => void, delay: number) => {
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(callback, delay);
  };

  const startConnectionTimeoutTimer = (callback: () => void, timeout: number) => {
    clearTimeout(connectionTimeoutTimer);
    connectionTimeoutTimer = setTimeout(callback, timeout);
  };

  const clearReconnectTimer = () => {
    clearTimeout(reconnectTimer);
    reconnectTimer = undefined;
  };

  const clearConnectionTimeoutTimer = () => {
    clearTimeout(connectionTimeoutTimer);
    connectionTimeoutTimer = undefined;
  };

  const clearAllTimers = () => {
    clearReconnectTimer();
    clearConnectionTimeoutTimer();
  };

  return {
    clearAllTimers,
    clearConnectionTimeoutTimer,
    clearReconnectTimer,
    startConnectionTimeoutTimer,
    startReconnectTimer,
  };
}
