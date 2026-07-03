import { describe, expect, it } from "vitest";
import { ApiCodeEnum } from "@/enums/api/code-enum";
import { getApiErrorMessage, normalizeApiErrorEnvelope } from "@/utils/api-error";

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

  it("normalizes FastAPI validation error details before generic message", () => {
    const payload = {
      code: 42200,
      message: "请求参数验证失败",
      data: {
        errors: [
          { field: "username", message: "用户名不能为空" },
          { field: "password", message: "密码不能为空" },
        ],
      },
    };

    expect(normalizeApiErrorEnvelope(payload, "兜底错误")).toEqual({
      code: 42200,
      message: "用户名不能为空；密码不能为空",
      data: payload.data,
      raw: payload,
    });
    expect(getApiErrorMessage(payload, "兜底错误")).toBe("用户名不能为空；密码不能为空");
  });

  it("normalizes numeric string code for shared auth error handling", () => {
    expect(
      normalizeApiErrorEnvelope({
        code: "40001",
        message: "token expired",
      }).code
    ).toBe(ApiCodeEnum.ACCESS_TOKEN_INVALID);
  });
});
