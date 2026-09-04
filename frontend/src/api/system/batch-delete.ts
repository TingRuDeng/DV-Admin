/** 批量删除接口支持的对象 ID 类型。 */
export type BatchDeleteObjectId = string | number;

/** 批量删除结果状态。 */
export type BatchDeleteStatus = "succeeded" | "partial_failed" | "failed";

/** 批量删除成功项。 */
export interface BatchDeleteSuccessItem {
  objectId: string;
  objectName: string;
}

/** 批量删除失败项。 */
export interface BatchDeleteFailure {
  objectId: string;
  objectName: string;
  errorCode: string;
  message: string;
  retryable: boolean;
}

/** 用户、角色和通知共享的批量删除结果。 */
export interface BatchDeleteResult {
  status: BatchDeleteStatus;
  totalCount: number;
  successCount: number;
  failedCount: number;
  processedCount: number;
  successItems: BatchDeleteSuccessItem[];
  failures: BatchDeleteFailure[];
}

/** 将页面行 ID 转换为后端契约要求的去重正整数列表。 */
export function normalizeBatchDeleteIds(ids: readonly BatchDeleteObjectId[]): number[] {
  if (!Array.isArray(ids) || ids.length === 0) {
    throw new Error("批量删除 ID 列表不能为空");
  }

  const normalized = ids.map((value) => (typeof value === "number" ? value : Number(value)));
  if (normalized.some((value) => !Number.isSafeInteger(value) || value < 1)) {
    throw new Error("批量删除 ID 必须为正整数");
  }

  return [...new Set(normalized)];
}

/** 构造批量删除请求体，确保三类页面使用同一请求参数形状。 */
export function batchDeleteRequest(ids: readonly BatchDeleteObjectId[]) {
  return { ids: normalizeBatchDeleteIds(ids) };
}
