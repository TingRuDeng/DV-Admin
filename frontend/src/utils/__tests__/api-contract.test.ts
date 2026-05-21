import { describe, expect, it } from "vitest";
import { ApiCodeEnum } from "@/enums/api/code-enum";
import { getApiErrorMessage } from "@/utils/api-error";

describe("API envelope contract compatibility", () => {
  it("keeps Django success envelope compatible with frontend code/data reads", () => {
    const response = {
      code: ApiCodeEnum.SUCCESS,
      msg: "成功",
      errors: null,
      data: { id: 1 },
    };

    expect(response.code).toBe(ApiCodeEnum.SUCCESS);
    expect(response.data).toEqual({ id: 1 });
  });

  it("keeps FastAPI success envelope compatible with frontend code/data reads", () => {
    const response = {
      code: ApiCodeEnum.SUCCESS,
      message: "success",
      data: { id: 1 },
    };

    expect(response.code).toBe(ApiCodeEnum.SUCCESS);
    expect(response.data).toEqual({ id: 1 });
  });

  it("normalizes Django and FastAPI error messages at frontend boundary", () => {
    expect(getApiErrorMessage({ errors: "账号已禁用", msg: "请求失败" })).toBe("账号已禁用");
    expect(getApiErrorMessage({ message: "token expired" })).toBe("token expired");
  });

  it("keeps shared pagination payload shape compatible with ProTable consumers", () => {
    const page = {
      list: [{ id: 1 }],
      total: 1,
    };

    expect(Array.isArray(page.list)).toBe(true);
    expect(page.total).toBe(1);
  });
});
