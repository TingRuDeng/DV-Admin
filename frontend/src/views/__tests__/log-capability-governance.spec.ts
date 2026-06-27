import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  isOperationLogUnsupportedError,
  OPERATION_LOG_UNSUPPORTED_MESSAGE,
} from "../system/log/logCapability";

describe("log capability governance", () => {
  it("only treats unsupported HTTP status as operation log capability gap", () => {
    expect(isOperationLogUnsupportedError({ status: 404 })).toBe(true);
    expect(isOperationLogUnsupportedError({ response: { status: 405 } })).toBe(true);
    expect(isOperationLogUnsupportedError({ status: 500 })).toBe(false);
    expect(isOperationLogUnsupportedError(new Error("请求失败"))).toBe(false);
  });

  it("keeps the log page explicit about Django operation log capability gap", () => {
    const source = readFileSync(resolve(process.cwd(), "src/views/system/log/index.vue"), "utf8");
    const requestSource = readFileSync(resolve(process.cwd(), "src/utils/request.ts"), "utf8");

    expect(source).toContain("logCapability.unsupported");
    expect(source).toContain("isOperationLogUnsupportedError(error)");
    expect(source).toContain("throw error");
    expect(source).toContain("OPERATION_LOG_UNSUPPORTED_MESSAGE");
    expect(requestSource).toContain("httpError.status = response.status");
    expect(OPERATION_LOG_UNSUPPORTED_MESSAGE).toContain("当前后端未提供可查询操作日志能力");
  });
});
