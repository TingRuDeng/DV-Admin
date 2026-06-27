import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const WEBSOCKET_TIMER_FILES = [
  "src/composables/websocket/stomp-connection-manager.ts",
  "src/composables/websocket/stomp-connection-state.ts",
  "src/composables/websocket/stomp-connection-timers.ts",
  "src/composables/websocket/useStomp.ts",
  "src/composables/websocket/useOnlineCount.ts",
  "src/composables/websocket/useDictSync.ts",
];

const TIMER_ANY_PATTERN = /\b(?:reconnectTimer|connectionTimeoutTimer|retryTimer)\s*:\s*any\b/;

describe("websocket timer type governance", () => {
  it("keeps WebSocket timer handles free of any", () => {
    const offenders = WEBSOCKET_TIMER_FILES.flatMap((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return source
        .split("\n")
        .map((line, index) => ({ file, line: index + 1, source: line.trim() }))
        .filter(({ source }) => TIMER_ANY_PATTERN.test(source));
    });

    expect(
      offenders,
      `发现 WebSocket 定时器重新使用 any:\n${offenders
        .map(({ file, line, source }) => `${file}:${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });

  it("keeps Stomp connection manager below the file size hard limit", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/composables/websocket/stomp-connection-manager.ts"),
      "utf8"
    );

    expect(source.split("\n").length).toBeLessThan(300);
  });

  it("keeps Stomp connection state behind a focused helper", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/composables/websocket/stomp-connection-state.ts"),
      "utf8"
    );

    expect(source).toContain("createStompConnectionState");
    expect(source).toContain("getSnapshot");
    expect(source).toContain("setConnected");
    expect(source).toContain("setReconnectCount");
  });
});
