interface ApiErrorEnvelope {
  code?: unknown;
  data?: unknown;
  errors?: unknown;
  msg?: unknown;
  message?: unknown;
}

export interface NormalizedApiErrorEnvelope {
  code?: number;
  message: string;
  data?: unknown;
  raw: unknown;
}

// 后端错误可能是字符串、数组或嵌套 detail 对象，统一压成可展示文本。
function normalizeErrorValue(value: unknown): string | undefined {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed || undefined;
  }

  if (Array.isArray(value)) {
    return value.map(normalizeErrorValue).filter(Boolean).join("；") || undefined;
  }

  if (value && typeof value === "object") {
    const detail = (value as { detail?: unknown }).detail;
    const message = (value as { message?: unknown }).message;
    return normalizeErrorValue(detail) || normalizeErrorValue(message) || JSON.stringify(value);
  }

  return undefined;
}

function normalizeCode(value: unknown): number | undefined {
  if (typeof value === "number" && Number.isSafeInteger(value)) {
    return value;
  }

  if (typeof value !== "string") {
    return undefined;
  }

  const trimmedCode = value.trim();
  if (!/^\d+$/.test(trimmedCode)) {
    return undefined;
  }

  const parsedCode = Number(trimmedCode);
  return Number.isSafeInteger(parsedCode) ? parsedCode : undefined;
}

function normalizeFastApiValidationErrors(data: unknown): string | undefined {
  if (!data || typeof data !== "object") {
    return undefined;
  }

  return normalizeErrorValue((data as { errors?: unknown }).errors);
}

export function normalizeApiErrorEnvelope(
  payload: unknown,
  fallback = "请求失败"
): NormalizedApiErrorEnvelope {
  if (!payload || typeof payload !== "object") {
    return { message: fallback, raw: payload };
  }

  const envelope = payload as ApiErrorEnvelope;
  const message =
    normalizeFastApiValidationErrors(envelope.data) ||
    normalizeErrorValue(envelope.errors) ||
    normalizeErrorValue(envelope.msg) ||
    normalizeErrorValue(envelope.message) ||
    fallback;

  return {
    code: normalizeCode(envelope.code),
    message,
    data: envelope.data,
    raw: payload,
  };
}

// Django 使用 msg/errors，FastAPI 使用 message；前端在边界层统一读取顺序。
export function getApiErrorMessage(payload: unknown, fallback = "请求失败") {
  return normalizeApiErrorEnvelope(payload, fallback).message;
}
