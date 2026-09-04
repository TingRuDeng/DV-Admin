"""结果化批量删除的共享输入与结果工具。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from app.core.exceptions import ValidationError
from app.schemas.system import (
    BatchDeleteFailure,
    BatchDeleteResult,
    BatchDeleteSuccessItem,
)


def normalize_batch_ids(raw_ids: Any, *, resource_name: str) -> list[int]:
    """校验、去重并保留首次出现顺序的批量 ID。"""
    if not isinstance(raw_ids, list) or not raw_ids:
        raise ValidationError(f"{resource_name} ID 列表不能为空")

    normalized: list[int] = []
    seen: set[int] = set()
    for value in raw_ids:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValidationError(f"{resource_name} ID 必须为正整数")
        if value not in seen:
            normalized.append(value)
            seen.add(value)
    return normalized


def build_batch_delete_result(
    ids: Sequence[int],
    success_items: Sequence[BatchDeleteSuccessItem],
    failures: Sequence[BatchDeleteFailure],
) -> BatchDeleteResult:
    """根据逐条结果构造统一批量删除响应。"""
    total_count = len(ids)
    success_count = len(success_items)
    failed_count = len(failures)
    if failed_count == 0:
        result_status: Literal["succeeded", "partial_failed", "failed"] = "succeeded"
    elif success_count == 0:
        result_status = "failed"
    else:
        result_status = "partial_failed"
    return BatchDeleteResult(
        status=result_status,
        total_count=total_count,
        success_count=success_count,
        failed_count=failed_count,
        processed_count=success_count + failed_count,
        success_items=list(success_items),
        failures=list(failures),
    )
