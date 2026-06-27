import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const DICT_ROOT = resolve(process.cwd(), "src/components/Dict");
const DICT_SOURCE = readFileSync(resolve(DICT_ROOT, "index.vue"), "utf8");
const DICT_LABEL_SOURCE = readFileSync(resolve(DICT_ROOT, "DictLabel.vue"), "utf8");
const TYPES_SOURCE = readFileSync(resolve(DICT_ROOT, "types.ts"), "utf8");

describe("Dict 字典值类型治理", () => {
  it("字典组件值类型不能回退到显式 any", () => {
    const sources = `${DICT_SOURCE}\n${DICT_LABEL_SOURCE}`;

    expect(sources).not.toMatch(/ref<any>/);
    expect(sources).not.toMatch(/handleChange\(val:\s*any\)/);
    expect(sources).not.toMatch(/value:\s*any/);
  });

  it("字典值类型必须集中表达字符串、数字和复选数组", () => {
    expect(TYPES_SOURCE).toContain("export type DictValue = string | number;");
    expect(TYPES_SOURCE).toContain(
      "export type DictModelValue = DictValue | DictValue[] | undefined;"
    );
  });
});
