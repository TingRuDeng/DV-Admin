import { useEventListener } from "@vueuse/core";

type NavigatorWithUAData = Navigator & { userAgentData?: { platform?: string } };

/**
 * 快捷键提示：苹果设备显示 ⌘K，其他平台显示 Ctrl K
 */
export function resolveShortcutLabel(nav: NavigatorWithUAData = navigator) {
  const platform = nav.userAgentData?.platform || nav.platform || "";
  return /mac|iphone|ipad|ipod/i.test(platform) ? "⌘K" : "Ctrl K";
}

// 对话框、抽屉、消息框打开时不抢焦点；关闭后的遮罩以 display:none 留在 DOM 里，只算可见的
function hasOpenOverlay() {
  return Array.from(document.querySelectorAll<HTMLElement>(".el-overlay")).some(
    (overlay) => getComputedStyle(overlay).display !== "none"
  );
}

/**
 * 注册全局 ⌘/Ctrl+K；输入法组字中或有模态浮层时不触发
 */
export function useMenuSearchShortcut(onTrigger: () => void) {
  useEventListener(document, "keydown", (event: KeyboardEvent) => {
    if (event.isComposing || event.altKey || event.shiftKey) return;
    // 浏览器自动填充派发的 keydown 没有 key
    if (!(event.metaKey || event.ctrlKey) || event.key?.toLowerCase() !== "k") return;
    if (hasOpenOverlay()) return;

    event.preventDefault();
    onTrigger();
  });

  return { shortcutLabel: resolveShortcutLabel() };
}
