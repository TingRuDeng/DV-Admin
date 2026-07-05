"""
通知公告 Service
"""

from typing import cast

from app.core.exceptions import NotFound, ValidationError
from app.db.models.oauth import Users
from app.db.models.system import NoticeReads, Notices
from app.schemas.system import (
    NoticeAdminPageResult,
    NoticeCreate,
    NoticeDetailOut,
    NoticeFormOut,
    NoticeMyPageResult,
    NoticePageOut,
    NoticeUpdate,
)
from app.services.system.field_permission import (
    can_write_notice_target_fields,
    has_notice_target_write,
)
from app.services.system.notice_read_helpers import (
    apply_read_filter,
    find_unread_notice_ids,
)
from app.services.system.notice_serializers import (
    notice_to_detail_out,
    notice_to_form_out,
    notice_to_my_page_out,
    notice_to_page_out,
)
from app.services.system.notice_time import local_now


class NoticeService:
    """通知公告服务"""

    async def get_page(
        self,
        page_num: int,
        page_size: int,
        title: str | None = None,
        publish_status: int | None = None,
    ) -> NoticeAdminPageResult:
        query = Notices.all()

        if title:
            query = query.filter(title__icontains=title)

        if publish_status is not None:
            query = query.filter(publish_status=publish_status)

        total = await query.count()
        notices = (
            await query.order_by("-created_at")
            .offset((page_num - 1) * page_size)
            .limit(page_size)
            .all()
        )

        results = [notice_to_page_out(notice) for notice in notices]

        return NoticeAdminPageResult(list=results, total=total)

    async def get_form(self, notice_id: int) -> NoticeFormOut:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        return notice_to_form_out(notice)

    async def get_detail(self, notice_id: int, user_id: int | None = None) -> NoticeDetailOut:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if user_id is not None:
            await self._mark_read(notice_id=notice.id, user_id=user_id)

        return notice_to_detail_out(notice)

    async def create(
        self,
        notice_in: NoticeCreate,
        publisher_id: int,
        publisher_name: str,
        current_user: Users | None = None,
    ) -> NoticePageOut:
        if notice_in.target_type == 2 and not notice_in.target_user_ids:
            raise ValidationError("目标类型为指定时，必须选择目标用户")

        await self._validate_notice_target_write(notice_in.target_user_ids, current_user)

        notice = await Notices.create(
            title=notice_in.title,
            content=notice_in.content,
            type=notice_in.type,
            level=notice_in.level,
            target_type=notice_in.target_type,
            target_user_ids=notice_in.target_user_ids if notice_in.target_type == 2 else [],
            publisher_id=publisher_id,
            publisher_name=publisher_name,
            publish_status=0,
        )

        return notice_to_page_out(notice)

    async def update(
        self,
        notice_id: int,
        notice_in: NoticeUpdate,
        current_user: Users | None = None,
    ) -> NoticePageOut:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if notice.publish_status == 1:
            raise ValidationError("已发布通知不允许编辑")

        await self._validate_notice_target_write(notice_in.target_user_ids, current_user)

        update_fields = {}
        for field, value in notice_in.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields[field] = value

        if "target_user_ids" in update_fields and notice_in.target_type != 2:
            update_fields["target_user_ids"] = []

        if "target_type" in update_fields and update_fields["target_type"] != 2:
            update_fields["target_user_ids"] = []

        if update_fields:
            await Notices.filter(id=notice_id).update(**update_fields)
            await notice.refresh_from_db()

        return notice_to_page_out(notice)

    async def _validate_notice_target_write(
        self,
        target_user_ids: list[int] | None,
        current_user: Users | None,
    ) -> None:
        """校验当前操作者是否可写入通知指定用户范围。"""
        if not has_notice_target_write(target_user_ids):
            return
        if await can_write_notice_target_fields(current_user):
            return
        raise ValidationError("缺少通知目标字段写入权限，不能写入指定用户范围")

    async def delete_by_ids(self, ids: list[int]) -> None:
        published = await Notices.filter(id__in=ids, publish_status=1).exists()
        if published:
            raise ValidationError("已发布通知不允许删除")

        await Notices.filter(id__in=ids).delete()

    async def publish(self, notice_id: int) -> None:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if notice.publish_status == 1:
            return

        notice.publish_status = 1
        notice.publish_time = local_now()
        notice.revoke_time = None
        await notice.save()

    async def revoke(self, notice_id: int) -> None:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if notice.publish_status != 1:
            return

        notice.publish_status = -1
        notice.revoke_time = local_now()
        await notice.save()

    async def read_all(self, user_id: int) -> None:
        published_ids = cast(
            list[int],
            await Notices.filter(publish_status=1).values_list("id", flat=True),
        )
        if not published_ids:
            return

        existing_ids = cast(
            list[int],
            await NoticeReads.filter(user_id=user_id, notice_id__in=published_ids).values_list(
                "notice_id", flat=True
            ),
        )

        missing = find_unread_notice_ids(published_ids, existing_ids)
        if not missing:
            return

        await NoticeReads.bulk_create(
            [NoticeReads(notice_id=nid, user_id=user_id) for nid in missing]
        )

    async def get_my_page(
        self,
        user_id: int,
        page_num: int,
        page_size: int,
        title: str | None = None,
        is_read: int | None = None,
    ) -> NoticeMyPageResult:
        query = Notices.filter(publish_status=1)

        if title:
            query = query.filter(title__icontains=title)

        read_notice_ids = cast(
            list[int],
            await NoticeReads.filter(user_id=user_id).values_list("notice_id", flat=True),
        )

        if is_read is not None:
            query = apply_read_filter(query, read_notice_ids, is_read)

        total = await query.count()
        notices = (
            await query.order_by("-publish_time", "-created_at")
            .offset((page_num - 1) * page_size)
            .limit(page_size)
            .all()
        )

        notice_ids = [n.id for n in notices]
        read_ids = set(
            cast(
                list[int],
                await NoticeReads.filter(user_id=user_id, notice_id__in=notice_ids).values_list(
                    "notice_id", flat=True
                ),
            )
        )

        items = [notice_to_my_page_out(notice, read_ids) for notice in notices]

        return NoticeMyPageResult(list=items, total=total)

    async def _mark_read(self, notice_id: int, user_id: int) -> None:
        await NoticeReads.get_or_create(notice_id=notice_id, user_id=user_id)


notice_service = NoticeService()
