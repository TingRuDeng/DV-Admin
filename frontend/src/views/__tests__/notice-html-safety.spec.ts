import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const NOTICE_HTML_FILES = [
  "src/views/system/notice/index.vue",
  "src/views/system/notice/components/MyNotice.vue",
  "src/components/Notification/index.vue",
];

describe("notice html safety", () => {
  it("renders notice rich text through SafeHtml instead of raw v-html", () => {
    const offenders = NOTICE_HTML_FILES.filter((file) => {
      const source = readFileSync(resolve(process.cwd(), file), "utf8");
      return source.includes("v-html") || !source.includes("<SafeHtml");
    });

    expect(
      offenders,
      `Found notice rich text entries not using SafeHtml:\n${offenders.join("\n")}`
    ).toEqual([]);
  });
});
