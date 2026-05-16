interface ApiErrorEnvelope {
  errors?: unknown;
  msg?: unknown;
  message?: unknown;
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
    return normalizeErrorValue(detail) || JSON.stringify(value);
  }

  return undefined;
}

// Django 使用 msg/errors，FastAPI 使用 message；前端在边界层统一读取顺序。
export function getApiErrorMessage(payload: unknown, fallback = "请求失败") {
  if (!payload || typeof payload !== "object") {
    return fallback;
  }

  const envelope = payload as ApiErrorEnvelope;
  return (
    normalizeErrorValue(envelope.errors) ||
    normalizeErrorValue(envelope.msg) ||
    normalizeErrorValue(envelope.message) ||
    fallback
  );
}
