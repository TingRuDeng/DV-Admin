/** 将日志载荷格式化为便于排查的安全纯文本。 */
export function formatLogPayload(value: string): string {
  const normalized = value.trim();
  if (!normalized) return "-";

  try {
    return JSON.stringify(JSON.parse(normalized), null, 2);
  } catch {
    return normalized;
  }
}
