/** 浏览器支持 View Transitions 且用户没有要求减少动效时，主题切换才做圆形扩散 */
export function supportsThemeReveal(
  doc: Pick<Document, "startViewTransition"> | undefined = typeof document === "undefined"
    ? undefined
    : document,
  matchMedia: ((query: string) => { matches: boolean }) | undefined = typeof window === "undefined"
    ? undefined
    : window.matchMedia?.bind(window)
) {
  if (typeof doc?.startViewTransition !== "function") return false;
  return !matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}

/** 圆心到视口最远角的距离，保证扩散结束时新主题覆盖整个屏幕 */
export function revealRadius(x: number, y: number, width: number, height: number) {
  return Math.ceil(Math.hypot(Math.max(x, width - x), Math.max(y, height - y)));
}
