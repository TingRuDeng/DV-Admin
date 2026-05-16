export type LogLevel = "debug" | "info" | "warn" | "error";

interface LoggerOptions {
  debugEnabled?: boolean;
}

// 调试日志必须显式开启，避免生产环境持续输出 WebSocket 生命周期细节。
function isDebugLogEnabled() {
  return import.meta.env.DEV && import.meta.env.VITE_ENABLE_DEBUG_LOG === "true";
}

// warn/error 始终输出，避免连接失败被调试开关误吞；debug/info 只在调试开关开启时输出。
export function shouldEmitLog(level: LogLevel, debugEnabled = isDebugLogEnabled()) {
  return level === "warn" || level === "error" || debugEnabled;
}

function formatScope(scope: string) {
  return scope.startsWith("[") ? scope : `[${scope}]`;
}

function writeLog(scope: string, level: LogLevel, debugEnabled: boolean, args: unknown[]) {
  if (!shouldEmitLog(level, debugEnabled)) {
    return;
  }

  console[level](formatScope(scope), ...args);
}

// scope 让日志来源固定可读，便于后续接入远端日志或筛选 WebSocket 模块。
export function createLogger(scope: string, options: LoggerOptions = {}) {
  const debugEnabled = options.debugEnabled ?? isDebugLogEnabled();

  return {
    debug: (...args: unknown[]) => writeLog(scope, "debug", debugEnabled, args),
    info: (...args: unknown[]) => writeLog(scope, "info", debugEnabled, args),
    warn: (...args: unknown[]) => writeLog(scope, "warn", debugEnabled, args),
    error: (...args: unknown[]) => writeLog(scope, "error", debugEnabled, args),
  };
}
