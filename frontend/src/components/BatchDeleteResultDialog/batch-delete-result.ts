import type { BatchDeleteFailure, BatchDeleteResult } from "@/api/system/batch-delete";

/** 只接受协议定义的布尔 true，避免旧代理返回字符串造成误显示。 */
export function isRetryableBatchDeleteFailure(
  failure: Pick<BatchDeleteFailure, "retryable">
): boolean {
  return failure.retryable === true;
}

/** 判断异步重试响应是否仍属于当前结果批次。 */
export function isCurrentBatchToken(requestToken: unknown, currentToken: unknown): boolean {
  return requestToken === currentToken;
}

function getStatus(successCount: number, failedCount: number): BatchDeleteResult["status"] {
  if (failedCount === 0) return "succeeded";
  if (successCount === 0) return "failed";
  return "partial_failed";
}

/** 将单条重试结果合并回原批次，保持原始 totalCount 不变。 */
export function mergeBatchDeleteRetryResult(
  current: BatchDeleteResult,
  objectId: string,
  retryResult: BatchDeleteResult
): BatchDeleteResult {
  const retriedSuccess = retryResult.successItems.find((item) => item.objectId === objectId);
  const retriedFailure = retryResult.failures.find((item) => item.objectId === objectId);

  // 后端没有返回目标项时不改变当前明细，避免误删失败记录。
  if (!retriedSuccess && !retriedFailure) return current;

  const successItems = current.successItems.filter((item) => item.objectId !== objectId);
  if (retriedSuccess) successItems.push(retriedSuccess);

  const failures = current.failures.flatMap((item) => {
    if (item.objectId !== objectId) return [item];
    return retriedFailure ? [retriedFailure] : [];
  });
  const successCount = successItems.length;
  const failedCount = failures.length;

  return {
    ...current,
    status: getStatus(successCount, failedCount),
    successCount,
    failedCount,
    processedCount: successCount + failedCount,
    successItems,
    failures,
  };
}

export function shouldNotifyBatchDeleteRetrySuccess(
  result: BatchDeleteResult,
  objectId: string
): boolean {
  return result.successItems.some((item) => item.objectId === objectId);
}
