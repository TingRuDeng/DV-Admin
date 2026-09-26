/**
 * 登录后的跳转目标只允许站内相对路径，防止 ?redirect= 被用来跳到外部站点。
 *
 * @param value 路由 query 中的 redirect（vue-router 已解码一次，不能再次解码）
 * @param fallback 不合法时使用的默认路径
 */
export function resolveSafeRedirect(value: unknown, fallback = "/"): string {
  const target = Array.isArray(value) ? value[0] : value;
  if (typeof target !== "string" || !target.startsWith("/")) {
    return fallback;
  }
  // "//host" 和 "/\host" 会被浏览器当成协议相对地址
  if (target.startsWith("//") || target.startsWith("/\\")) {
    return fallback;
  }
  // 浏览器解析 URL 时会删掉制表符和换行，"/\t/host" 会变成 "//host"
  if ([...target].some((char) => char.charCodeAt(0) < 0x20 || char.charCodeAt(0) === 0x7f)) {
    return fallback;
  }
  return target;
}
