"""
通知已读状态 helper
"""

from tortoise.expressions import Q


def find_unread_notice_ids(
    published_ids: list[int],
    existing_ids: list[int],
) -> list[int]:
    """计算用户尚未标记已读的通知 ID。"""
    existing_id_set = set(existing_ids)
    return [notice_id for notice_id in published_ids if notice_id not in existing_id_set]


def apply_read_filter(query, read_notice_ids: list[int], is_read: int):
    """按已读状态过滤我的通知查询。"""
    if is_read == 1:
        return query.filter(id__in=read_notice_ids)
    if read_notice_ids:
        return query.filter(~Q(id__in=read_notice_ids))
    return query
