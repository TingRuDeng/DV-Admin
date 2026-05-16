import { describe, expect, it } from "vitest";
import { getApiErrorMessage } from "@/utils/api-error";

describe("getApiErrorMessage", () => {
  it("prefers Django errors field", () => {
    expect(getApiErrorMessage({ errors: "账号已禁用", msg: "请求失败" })).toBe("账号已禁用");
  });

  it("supports Django msg field", () => {
    expect(getApiErrorMessage({ msg: "参数错误" })).toBe("参数错误");
  });

  it("supports FastAPI message field", () => {
    expect(getApiErrorMessage({ message: "token expired" })).toBe("token expired");
  });

  it("normalizes nested detail errors", () => {
    expect(getApiErrorMessage({ errors: { detail: "权限不足" } })).toBe("权限不足");
  });

  it("uses fallback when payload is empty", () => {
    expect(getApiErrorMessage(null, "兜底错误")).toBe("兜底错误");
  });
});
