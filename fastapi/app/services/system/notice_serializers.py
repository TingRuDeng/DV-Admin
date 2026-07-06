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
from app.services.system.field_permission import (
    filter_notice_content,
    filter_notice_target_user_ids,
)


def notice_to_page_out(
    notice: Notices,
    can_view_target_users: bool = True,
    can_view_content: bool = True,
) -> NoticePageOut:
    """将通知 ORM 对象转换为后台分页输出。"""
    return NoticePageOut(
        id=notice.id,
        title=notice.title,
        content=filter_notice_content(notice.content, can_view_content),
        type=notice.type,
        level=notice.level,
        target_type=notice.target_type,
        target_user_ids=filter_notice_target_user_ids(
            notice.target_user_ids,
            can_view_target_users,
        ),
        publisher_id=notice.publisher_id,
        publisher_name=notice.publisher_name,
        publish_status=notice.publish_status,
        create_time=notice.created_at,
        update_time=notice.updated_at,
        publish_time=notice.publish_time,
        revoke_time=notice.revoke_time,
    )


def notice_to_form_out(
    notice: Notices,
    can_view_target_users: bool = True,
    can_view_content: bool = True,
) -> NoticeFormOut:
    """将通知 ORM 对象转换为表单输出。"""
    return NoticeFormOut(
        id=notice.id,
        title=notice.title,
        content=filter_notice_content(notice.content, can_view_content),
        type=notice.type,
        level=notice.level,
        target_type=notice.target_type,
        target_user_ids=filter_notice_target_user_ids(
            notice.target_user_ids,
            can_view_target_users,
        ),
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


def notice_to_my_page_out(
    notice: Notices,
    read_ids: set[int],
    can_view_target_users: bool = True,
) -> NoticeMyPageOut:
    """将通知 ORM 对象转换为我的通知分页输出。"""
    page_out = notice_to_page_out(notice, can_view_target_users, can_view_content=True)
    return NoticeMyPageOut(**page_out.model_dump(), is_read=1 if notice.id in read_ids else 0)
