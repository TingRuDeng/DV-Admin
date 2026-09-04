"""Django 结果化批量删除的共享输入、预检和结果工具。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError


def normalize_batch_ids(raw_ids: Any, *, resource_name: str) -> list[int]:
    """校验、去重并保留首次出现顺序的批量 ID。"""
    if not isinstance(raw_ids, list) or not raw_ids:
        raise ValidationError(f"{resource_name} ID 列表不能为空")

    normalized: list[int] = []
    seen: set[int] = set()
    for value in raw_ids:
        # bool 是 int 的子类，必须显式排除，避免 True 被当成 ID 1。
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValidationError(f"{resource_name} ID 必须为正整数")
        if value not in seen:
            normalized.append(value)
            seen.add(value)
    return normalized


def preflight_batch_ids(
    queryset,
    ids: Sequence[int],
    *,
    resource_name: str,
    include_ids: Sequence[int] = (),
) -> None:
    """在单独事务中锁定并校验整批对象，失败时不产生任何删除。"""
    requested_ids = set(ids)
    with transaction.atomic():
        scoped_queryset = queryset.filter(pk__in=requested_ids)
        # 清掉视图层可能附带的关联预取，避免锁定不必要的关联表。
        scoped_queryset = scoped_queryset.select_related(None).prefetch_related(None)
        locked_ids = set(
            scoped_queryset.select_for_update().values_list("pk", flat=True)
        )

    visible_ids = locked_ids | set(include_ids)
    if not requested_ids.issubset(visible_ids):
        raise NotFound(f"{resource_name}不存在")


def success_item(object_id: int, object_name: str = "") -> dict[str, str]:
    """构造一个成功项。"""
    return {"object_id": str(object_id), "object_name": object_name or ""}


def failure_item(
    object_id: int,
    *,
    error_code: str,
    message: str,
    object_name: str = "",
    retryable: bool = False,
) -> dict[str, Any]:
    """构造一个失败项。"""
    return {
        "object_id": str(object_id),
        "object_name": object_name or "",
        "error_code": error_code,
        "message": message,
        "retryable": retryable,
    }


def build_batch_delete_result(
    ids: Sequence[int],
    success_items: Sequence[Mapping[str, Any]],
    failures: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """根据逐条结果构造统一批量删除响应。"""
    total_count = len(ids)
    success_count = len(success_items)
    failed_count = len(failures)
    if failed_count == 0:
        result_status = "succeeded"
    elif success_count == 0:
        result_status = "failed"
    else:
        result_status = "partial_failed"
    return {
        "status": result_status,
        "total_count": total_count,
        "success_count": success_count,
        "failed_count": failed_count,
        "processed_count": success_count + failed_count,
        "success_items": [dict(item) for item in success_items],
        "failures": [dict(item) for item in failures],
    }


__all__ = [
    "build_batch_delete_result",
    "failure_item",
    "normalize_batch_ids",
    "preflight_batch_ids",
    "success_item",
]
