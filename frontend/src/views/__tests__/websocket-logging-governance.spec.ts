import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const WEBSOCKET_FILES = [
  "src/composables/websocket/useStomp.ts",
  "src/composables/websocket/useOnlineCount.ts",
  "src/composables/websocket/useDictSync.ts",
  "src/plugins/websocket.ts",
];

const DIRECT_CONSOLE_PATTERN = /console\.(log|debug|info|warn|error)\(/;

describe("websocket logging governance", () => {
  it("keeps WebSocket modules on the shared logger", () => {
    const offenders = WEBSOCKET_FILES.filter((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return DIRECT_CONSOLE_PATTERN.test(source) || !source.includes("createLogger");
    });

    expect(
      offenders,
      `Found WebSocket modules bypassing the shared logger:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
