import { beforeEach, describe, expect, it, vi } from "vitest";
import { createLogger, shouldEmitLog } from "@/utils/logger";

describe("logger", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("keeps debug and info silent when debug is disabled", () => {
    const debugSpy = vi.spyOn(console, "debug").mockImplementation(() => undefined);
    const infoSpy = vi.spyOn(console, "info").mockImplementation(() => undefined);
    const logger = createLogger("WebSocket", { debugEnabled: false });

    logger.debug("连接中");
    logger.info("已连接");

    expect(debugSpy).not.toHaveBeenCalled();
    expect(infoSpy).not.toHaveBeenCalled();
  });

  it("always emits warn and error", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const logger = createLogger("WebSocket", { debugEnabled: false });

    logger.warn("连接超时");
    logger.error("连接失败");

    expect(warnSpy).toHaveBeenCalledWith("[WebSocket]", "连接超时");
    expect(errorSpy).toHaveBeenCalledWith("[WebSocket]", "连接失败");
  });

  it("emits debug logs when debug is enabled", () => {
    const debugSpy = vi.spyOn(console, "debug").mockImplementation(() => undefined);
    const logger = createLogger("DictSync", { debugEnabled: true });

    logger.debug("订阅成功");

    expect(debugSpy).toHaveBeenCalledWith("[DictSync]", "订阅成功");
  });

  it("uses the shared emission policy", () => {
    expect(shouldEmitLog("debug", false)).toBe(false);
    expect(shouldEmitLog("info", false)).toBe(false);
    expect(shouldEmitLog("warn", false)).toBe(true);
    expect(shouldEmitLog("error", false)).toBe(true);
  });
});
