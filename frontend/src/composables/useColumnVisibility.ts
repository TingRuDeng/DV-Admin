import { useStorage } from "@vueuse/core";

/**
 * 列显示/隐藏状态管理
 *
 * @param key       存储键，建议用页面名+":columns"，如 "sys-user:columns"
 * @param allColumns 全量列 key 列表（顺序即默认顺序）
 * @param defaultHidden 默认隐藏的列 key，不传则全部显示
 */
export function useColumnVisibility(
  key: string,
  allColumns: string[],
  defaultHidden: string[] = []
) {
  const defaultVisible = allColumns.filter((c) => !defaultHidden.includes(c));

  const visibleColumns = useStorage<string[]>(key, defaultVisible, sessionStorage);

  /** 某列是否可见 */
  function isVisible(col: string): boolean {
    return visibleColumns.value.includes(col);
  }

  /** 切换某列的显示/隐藏 */
  function toggle(col: string) {
    const idx = visibleColumns.value.indexOf(col);
    if (idx >= 0) {
      visibleColumns.value.splice(idx, 1);
    } else {
      // 按 allColumns 的顺序插入，保持列序稳定
      const insertAt = allColumns.reduce((pos, c, i) => {
        return visibleColumns.value.includes(c) || c === col ? pos : i;
      }, visibleColumns.value.length);
      const ordered = allColumns.filter((c) => visibleColumns.value.includes(c) || c === col);
      visibleColumns.value = ordered;
    }
  }

  /** 重置为默认 */
  function reset() {
    visibleColumns.value = [...defaultVisible];
  }

  return { visibleColumns, isVisible, toggle, reset, allColumns };
}
