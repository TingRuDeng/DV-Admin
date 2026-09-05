import { describe, expect, it } from "vitest";

import type { BatchDeleteResult } from "@/api/system/batch-delete";
import {
  isCurrentBatchToken,
  isRetryableBatchDeleteFailure,
  mergeBatchDeleteRetryResult,
  shouldNotifyBatchDeleteRetrySuccess,
} from "@/components/BatchDeleteResultDialog/batch-delete-result";

const initialResult: BatchDeleteResult = {
  status: "partial_failed",
  totalCount: 2,
  successCount: 1,
  failedCount: 1,
  processedCount: 2,
  successItems: [{ objectId: "1", objectName: "已删除对象" }],
  failures: [
    {
      objectId: "2",
      objectName: "待重试对象",
      errorCode: "PUBLISHED_OBJECT",
      message: "对象已发布",
      retryable: true,
    },
  ],
};

describe("mergeBatchDeleteRetryResult", () => {
  it("moves a successful retry into successItems and recalculates the status", () => {
    const result = mergeBatchDeleteRetryResult(initialResult, "2", {
      status: "succeeded",
      totalCount: 1,
      successCount: 1,
      failedCount: 0,
      processedCount: 1,
      successItems: [{ objectId: "2", objectName: "待重试对象" }],
      failures: [],
    });

    expect(result).toMatchObject({
      status: "succeeded",
      totalCount: 2,
      successCount: 2,
      failedCount: 0,
      processedCount: 2,
    });
    expect(result.failures).toEqual([]);
    expect(result.successItems.map((item) => item.objectId)).toEqual(["1", "2"]);
  });

  it("replaces a still-failing item without losing its retry state", () => {
    const result = mergeBatchDeleteRetryResult(initialResult, "2", {
      status: "failed",
      totalCount: 1,
      successCount: 0,
      failedCount: 1,
      processedCount: 1,
      successItems: [],
      failures: [
        {
          objectId: "2",
          objectName: "待重试对象",
          errorCode: "ALREADY_DELETED",
          message: "对象已经删除",
          retryable: false,
        },
      ],
    });

    expect(result.status).toBe("partial_failed");
    expect(result.successCount).toBe(1);
    expect(result.failedCount).toBe(1);
    expect(result.failures[0]).toMatchObject({
      objectId: "2",
      errorCode: "ALREADY_DELETED",
      retryable: false,
    });
  });

  it("does not treat a retry response for another object as success", () => {
    const result = mergeBatchDeleteRetryResult(initialResult, "2", {
      status: "succeeded",
      totalCount: 1,
      successCount: 1,
      failedCount: 0,
      processedCount: 1,
      successItems: [{ objectId: "unexpected", objectName: "其他对象" }],
      failures: [],
    });

    expect(result).toEqual(initialResult);
    expect(shouldNotifyBatchDeleteRetrySuccess(result, "2")).toBe(false);
  });
});

describe("batch delete retry guards", () => {
  it("accepts only a literal boolean true as retryable", () => {
    expect(isRetryableBatchDeleteFailure({ retryable: true })).toBe(true);
    expect(isRetryableBatchDeleteFailure({ retryable: false })).toBe(false);
    expect(isRetryableBatchDeleteFailure({ retryable: "false" as unknown as boolean })).toBe(false);
  });

  it("rejects retry responses from an older dialog batch", () => {
    const firstBatch = Symbol("first");
    const nextBatch = Symbol("next");

    expect(isCurrentBatchToken(firstBatch, firstBatch)).toBe(true);
    expect(isCurrentBatchToken(firstBatch, nextBatch)).toBe(false);
  });
});
