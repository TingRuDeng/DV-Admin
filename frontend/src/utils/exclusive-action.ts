/** 可被异步操作占用的布尔状态。兼容 Vue 的 Ref<boolean>。 */
export interface ExclusiveState {
  value: boolean;
}

/**
 * 在状态已占用时拒绝并发操作，并确保同步/异步异常后释放占用。
 * 返回 undefined 表示本次调用未取得执行权。
 */
export async function runExclusive<T>(
  state: ExclusiveState,
  action: () => Promise<T>
): Promise<T | undefined> {
  if (state.value) return undefined;

  state.value = true;
  try {
    return await action();
  } finally {
    state.value = false;
  }
}
