"""
通知公告 Service
"""
from datetime import datetime

from tortoise.expressions import Q

from app.core.exceptions import NotFound, ValidationError
from app.db.models.system import NoticeReads, Notices
from app.schemas.system import (
    NoticeAdminPageResult,
    NoticeCreate,
    NoticeDetailOut,
    NoticeFormOut,
    NoticeMyPageOut,
    NoticeMyPageResult,
    NoticePageOut,
    NoticeUpdate,
)


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

        results = [
            NoticePageOut(
                id=n.id,
                title=n.title,
                content=n.content,
                type=n.type,
                level=n.level,
                target_type=n.target_type,
                publisher_id=n.publisher_id,
                publisher_name=n.publisher_name,
                publish_status=n.publish_status,
                create_time=n.created_at,
                publish_time=n.publish_time,
                revoke_time=n.revoke_time,
            )
            for n in notices
        ]

        return NoticeAdminPageResult(list=results, total=total)

    async def get_form(self, notice_id: int) -> NoticeFormOut:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        return NoticeFormOut(
            id=notice.id,
            title=notice.title,
            content=notice.content,
            type=notice.type,
            level=notice.level,
            target_type=notice.target_type,
            target_user_ids=list(notice.target_user_ids or []),
        )

    async def get_detail(self, notice_id: int, user_id: int | None = None) -> NoticeDetailOut:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if user_id is not None:
            await self._mark_read(notice_id=notice.id, user_id=user_id)

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

    async def create(self, notice_in: NoticeCreate, publisher_id: int, publisher_name: str) -> NoticePageOut:
        if notice_in.target_type == 2 and not notice_in.target_user_ids:
            raise ValidationError("目标类型为指定时，必须选择目标用户")

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

    async def update(self, notice_id: int, notice_in: NoticeUpdate) -> NoticePageOut:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if notice.publish_status == 1:
            raise ValidationError("已发布通知不允许编辑")

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
        notice.publish_time = datetime.now()
        notice.revoke_time = None
        await notice.save()

    async def revoke(self, notice_id: int) -> None:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if notice.publish_status != 1:
            return

        notice.publish_status = -1
        notice.revoke_time = datetime.now()
        await notice.save()

    async def read_all(self, user_id: int) -> None:
        published_ids = await Notices.filter(publish_status=1).values_list("id", flat=True)
        if not published_ids:
            return

        existing_ids = await NoticeReads.filter(
            user_id=user_id, notice_id__in=published_ids
        ).values_list("notice_id", flat=True)

        missing = [nid for nid in published_ids if nid not in set(existing_ids)]
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

        read_notice_ids = await NoticeReads.filter(user_id=user_id).values_list(
            "notice_id", flat=True
        )

        if is_read is not None:
            if is_read == 1:
                query = query.filter(id__in=read_notice_ids)
            else:
                if read_notice_ids:
                    query = query.filter(~Q(id__in=read_notice_ids))

        total = await query.count()
        notices = (
            await query.order_by("-publish_time", "-created_at")
            .offset((page_num - 1) * page_size)
            .limit(page_size)
            .all()
        )

        notice_ids = [n.id for n in notices]
        read_ids = set(
            await NoticeReads.filter(user_id=user_id, notice_id__in=notice_ids).values_list(
                "notice_id", flat=True
            )
        )

        items = [
            NoticeMyPageOut(
                id=n.id,
                title=n.title,
                content=n.content,
                type=n.type,
                level=n.level,
                target_type=n.target_type,
                publisher_id=n.publisher_id,
                publisher_name=n.publisher_name,
                publish_status=n.publish_status,
                create_time=n.created_at,
                publish_time=n.publish_time,
                revoke_time=n.revoke_time,
                is_read=1 if n.id in read_ids else 0,
            )
            for n in notices
        ]

        return NoticeMyPageResult(list=items, total=total)

    async def _mark_read(self, notice_id: int, user_id: int) -> None:
        await NoticeReads.get_or_create(notice_id=notice_id, user_id=user_id)


notice_service = NoticeService()
