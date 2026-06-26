"""
通知服务输出转换 helper
"""

from app.db.models.system import Notices
from app.schemas.system import (
    NoticeDetailOut,
    NoticeFormOut,
    NoticeMyPageOut,
    NoticePageOut,
)


def notice_to_page_out(notice: Notices) -> NoticePageOut:
    """将通知 ORM 对象转换为后台分页输出。"""
    return NoticePageOut(
        id=notice.id,
        title=notice.title,
        content=notice.content,
        type=notice.type,
        level=notice.level,
        target_type=notice.target_type,
        publisher_id=notice.publisher_id,
        publisher_name=notice.publisher_name,
        publish_status=notice.publish_status,
        create_time=notice.created_at,
        publish_time=notice.publish_time,
        revoke_time=notice.revoke_time,
    )


def notice_to_form_out(notice: Notices) -> NoticeFormOut:
    """将通知 ORM 对象转换为表单输出。"""
    return NoticeFormOut(
        id=notice.id,
        title=notice.title,
        content=notice.content,
        type=notice.type,
        level=notice.level,
        target_type=notice.target_type,
        target_user_ids=list(notice.target_user_ids or []),
    )


def notice_to_detail_out(notice: Notices) -> NoticeDetailOut:
    """将通知 ORM 对象转换为详情输出。"""
    return NoticeDetailOut(
        id=notice.id,
        title=notice.title,
        content=notice.content,
        type=notice.type,
        level=notice.level,
        publisher_name=notice.publisher_name,
        publish_time=notice.publish_time,
        publish_status=notice.publish_status,
    )


def notice_to_my_page_out(notice: Notices, read_ids: set[int]) -> NoticeMyPageOut:
    """将通知 ORM 对象转换为我的通知分页输出。"""
    page_out = notice_to_page_out(notice)
    return NoticeMyPageOut(**page_out.model_dump(), is_read=1 if notice.id in read_ids else 0)
