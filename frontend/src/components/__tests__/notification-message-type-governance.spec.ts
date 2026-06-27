import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const NOTIFICATION_SOURCE = readFileSync(
  resolve(process.cwd(), "src/components/Notification/index.vue"),
  "utf8"
);

describe("Notification 订阅消息类型治理", () => {
  it("订阅消息不能回退到显式 any", () => {
    expect(NOTIFICATION_SOURCE).not.toMatch(/message:\s*any/);
  });

  it("订阅消息必须使用 STOMP 消息类型并在解析边界校验", () => {
    expect(NOTIFICATION_SOURCE).toContain("IMessage");
    expect(NOTIFICATION_SOURCE).toContain("parseNotificationMessage");
    expect(NOTIFICATION_SOURCE).toContain("toNotificationMessagePayload");
  });
});
