export const OPERATION_LOG_UNSUPPORTED_MESSAGE =
  "当前后端未提供可查询操作日志能力，请切换到 FastAPI 后端或联系管理员补齐 Django 操作日志实现。";

const UNSUPPORTED_OPERATION_LOG_STATUS = new Set([404, 405]);

interface HttpStatusError {
  status?: unknown;
  response?: {
    status?: unknown;
  };
}

/** 从未知错误中读取 HTTP 状态码，避免日志页按错误文案判断后端能力。 */
function getHttpStatus(error: unknown): number | undefined {
  if (!error || typeof error !== "object") {
    return undefined;
  }

  const statusError = error as HttpStatusError;
  if (typeof statusError.status === "number") {
    return statusError.status;
  }
  if (typeof statusError.response?.status === "number") {
    return statusError.response.status;
  }
  return undefined;
}

/** 判断日志管理接口是否是后端能力不支持，而不是普通运行时失败。 */
export function isOperationLogUnsupportedError(error: unknown) {
  const status = getHttpStatus(error);
  return status !== undefined && UNSUPPORTED_OPERATION_LOG_STATUS.has(status);
}
