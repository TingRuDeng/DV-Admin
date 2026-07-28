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


def is_notice_visible_to_user(notice, user_id: int) -> bool:
    """全体通知对所有用户可见，定向通知只对目标用户可见。"""
    if notice.target_type == 1:
        return True
    return user_id in (notice.target_user_ids or [])


def apply_read_filter(query, read_notice_ids: list[int], is_read: int):
    """按已读状态过滤我的通知查询。"""
    if is_read == 1:
        return query.filter(id__in=read_notice_ids)
    if read_notice_ids:
        return query.filter(~Q(id__in=read_notice_ids))
    return query
