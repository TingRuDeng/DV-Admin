import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const WEBSOCKET_PLUGIN_SOURCE = resolve(process.cwd(), "src/plugins/websocket.ts");
const ANY_TYPE_PATTERN = /\bany\b/;

describe("websocket registry type governance", () => {
  it("keeps WebSocket instance registry free of any", () => {
    const source = readFileSync(WEBSOCKET_PLUGIN_SOURCE, "utf8");
    const offenders = source
      .split("\n")
      .map((line, index) => ({ line: index + 1, source: line.trim() }))
      .filter(({ source }) => ANY_TYPE_PATTERN.test(source));

    expect(
      offenders,
      `发现 WebSocket 实例注册表重新使用 any:\n${offenders
        .map(({ line, source }) => `${line}: ${source}`)
        .join("\n")}`
    ).toEqual([]);
  });
});
