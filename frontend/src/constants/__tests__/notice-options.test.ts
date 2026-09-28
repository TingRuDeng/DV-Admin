import { describe, expect, it } from "vitest";

import {
  getNoticeOption,
  NOTICE_LEVEL_OPTIONS,
  NOTICE_TYPE_OPTIONS,
} from "@/constants/notice-options";

describe("notice options", () => {
  it("keeps the persisted type and level values", () => {
    expect(NOTICE_TYPE_OPTIONS.map((option) => option.value)).toEqual([1, 2, 3, 4, 5, 99]);
    expect(NOTICE_LEVEL_OPTIONS.map((option) => option.value)).toEqual(["L", "M", "H"]);
  });

  it("resolves values across numeric and string payloads", () => {
    expect(getNoticeOption("type", "1")?.label).toBe("系统升级");
    expect(getNoticeOption("level", "H")?.tagType).toBe("danger");
    expect(getNoticeOption("type", 777)).toBeUndefined();
  });
});
