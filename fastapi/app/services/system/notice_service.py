"""
通知公告 Service
"""

from typing import cast

from tortoise.transactions import in_transaction

from app.core.exceptions import NotFound, ValidationError
from app.db.models.oauth import Users
from app.db.models.system import NoticeReads, Notices
from app.schemas.system import (
    BatchDeleteFailure,
    BatchDeleteResult,
    BatchDeleteSuccessItem,
    NoticeAdminPageResult,
    NoticeCreate,
    NoticeDetailOut,
    NoticeFormOut,
    NoticeMyPageResult,
    NoticePageOut,
    NoticeUpdate,
)
from app.services.system.batch_delete import build_batch_delete_result, normalize_batch_ids
from app.services.system.data_scope import apply_notice_admin_data_scope
from app.services.system.field_permission import (
    can_view_notice_content_fields,
    can_view_notice_target_fields,
    can_write_notice_target_fields,
    has_notice_target_write,
)
from app.services.system.notice_read_helpers import (
    find_unread_notice_ids,
    is_notice_visible_to_user,
)
from app.services.system.notice_serializers import (
    notice_to_detail_out,
    notice_to_form_out,
    notice_to_my_page_out,
    notice_to_page_out,
)
from app.services.system.notice_time import local_now

NOTICE_SCAN_BATCH_SIZE = 200


class _PublishedNoticeError(Exception):
    """内部控制流异常：通知当前处于已发布状态。"""


class NoticeService:
    """通知公告服务"""

    async def get_page(
        self,
        page_num: int,
        page_size: int,
        title: str | None = None,
        publish_status: int | None = None,
        current_user: Users | None = None,
    ) -> NoticeAdminPageResult:
        query = await apply_notice_admin_data_scope(Notices.all(), current_user)

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

        can_view_target_users = await can_view_notice_target_fields(current_user)
        can_view_content = await can_view_notice_content_fields(current_user)
        results = [
            notice_to_page_out(notice, can_view_target_users, can_view_content)
            for notice in notices
        ]

        return NoticeAdminPageResult(list=results, total=total)

    async def get_form(
        self,
        notice_id: int,
        current_user: Users | None = None,
    ) -> NoticeFormOut:
        notice = await self._get_admin_notice(notice_id, current_user)
        can_view_target_users = await can_view_notice_target_fields(current_user)
        can_view_content = await can_view_notice_content_fields(current_user)
        return notice_to_form_out(notice, can_view_target_users, can_view_content)

    async def get_detail(self, notice_id: int, user_id: int | None = None) -> NoticeDetailOut:
        notice = await Notices.get_or_none(id=notice_id)
        if not notice:
            raise NotFound("通知不存在")

        if user_id is not None:
            if notice.publish_status != 1 or not is_notice_visible_to_user(notice, user_id):
                raise NotFound("通知不存在")
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

    async def delete_by_ids(
        self,
        ids: list[int],
        current_user: Users | None = None,
    ) -> BatchDeleteResult:
        """兼容旧方法名的结果化批量删除入口。"""
        return await self.batch_delete(ids, current_user=current_user)

    async def batch_delete(
        self,
        ids: list[int],
        current_user: Users | None = None,
    ) -> BatchDeleteResult:
        """批量删除通知并返回逐条结果。"""
        unique_ids = normalize_batch_ids(ids, resource_name="通知")
        all_notices = await Notices.filter(id__in=unique_ids).all()
        if len(all_notices) != len(unique_ids):
            raise NotFound("通知不存在")

        scoped_query = await apply_notice_admin_data_scope(
            Notices.filter(id__in=unique_ids), current_user
        )
        visible_ids = set(await scoped_query.values_list("id", flat=True))
        if len(visible_ids) != len(unique_ids):
            raise NotFound("通知不存在")

        notices_by_id = {notice.id: notice for notice in all_notices}
        success_items: list[BatchDeleteSuccessItem] = []
        failures: list[BatchDeleteFailure] = []
        for notice_id in unique_ids:
            notice = notices_by_id[notice_id]
            outcome = await self._delete_one_for_batch(
                notice_id,
                notice.title,
                current_user=current_user,
            )
            if isinstance(outcome, BatchDeleteFailure):
                failures.append(outcome)
            else:
                success_items.append(outcome)

        return build_batch_delete_result(unique_ids, success_items, failures)

    async def retry_batch_delete(
        self,
        ids: list[int],
        current_user: Users | None = None,
    ) -> BatchDeleteResult:
        """逐条重新校验并重试通知删除。"""
        unique_ids = normalize_batch_ids(ids, resource_name="通知")
        success_items: list[BatchDeleteSuccessItem] = []
        failures: list[BatchDeleteFailure] = []
        for notice_id in unique_ids:
            notice = await Notices.get_or_none(id=notice_id)
            if notice is None:
                failures.append(
                    BatchDeleteFailure(
                        object_id=str(notice_id),
                        error_code="ALREADY_DELETED",
                        message="通知已不存在",
                        retryable=False,
                    )
                )
                continue

            scoped_query = await apply_notice_admin_data_scope(
                Notices.filter(id=notice_id), current_user
            )
            visible = await scoped_query.first()
            if visible is None:
                failures.append(
                    BatchDeleteFailure(
                        object_id=str(notice_id),
                        object_name=notice.title,
                        error_code="NOT_FOUND",
                        message="通知不存在",
                        retryable=False,
                    )
                )
                continue

            outcome = await self._delete_one_for_batch(
                notice_id,
                notice.title,
                missing_code="ALREADY_DELETED",
                missing_message="通知已不存在",
                current_user=current_user,
            )
            if isinstance(outcome, BatchDeleteFailure):
                failures.append(outcome)
            else:
                success_items.append(outcome)

        return build_batch_delete_result(unique_ids, success_items, failures)

    async def _delete_one_for_batch(
        self,
        notice_id: int,
        object_name: str,
        *,
        missing_code: str = "NOT_FOUND",
        missing_message: str = "通知不存在",
        current_user: Users | None = None,
    ) -> BatchDeleteSuccessItem | BatchDeleteFailure:
        """在独立事务中复核状态并删除单个通知。"""
        try:
            async with in_transaction() as connection:
                scoped_query = await apply_notice_admin_data_scope(
                    Notices.filter(id=notice_id).using_db(connection),
                    current_user,
                )
                notice = await scoped_query.select_for_update().first()
                if notice is None:
                    # 通过同一事务连接确认对象是否仍存在，区分越权和已删除。
                    unscoped_notice = await (
                        Notices.filter(id=notice_id)
                        .using_db(connection)
                        .select_for_update()
                        .first()
                    )
                    if unscoped_notice is not None:
                        return BatchDeleteFailure(
                            object_id=str(notice_id),
                            object_name=object_name,
                            error_code="NOT_FOUND",
                            message="通知不存在",
                            retryable=False,
                        )
                    raise NotFound(missing_message)
                if notice.publish_status == 1:
                    raise _PublishedNoticeError
                await notice.delete(using_db=connection)
            return BatchDeleteSuccessItem(
                object_id=str(notice_id),
                object_name=object_name,
            )
        except _PublishedNoticeError:
            return BatchDeleteFailure(
                object_id=str(notice_id),
                object_name=object_name,
                error_code="PUBLISHED_OBJECT",
                message="已发布通知不允许删除",
                retryable=True,
            )
        except NotFound:
            return BatchDeleteFailure(
                object_id=str(notice_id),
                object_name=object_name,
                error_code=missing_code,
                message=missing_message,
                retryable=False,
            )
        except Exception:  # noqa: BLE001 - 单条失败不能阻塞其余项目
            return BatchDeleteFailure(
                object_id=str(notice_id),
                object_name=object_name,
                error_code="DELETE_FAILED",
                message="删除通知失败",
                retryable=True,
            )


    async def publish(self, notice_id: int, current_user: Users | None = None) -> None:
        notice = await self._get_admin_notice(notice_id, current_user)
        if notice.publish_status == 1:
            return

        notice.publish_status = 1
        notice.publish_time = local_now()
        notice.revoke_time = None
        await notice.save()

    async def revoke(self, notice_id: int, current_user: Users | None = None) -> None:
        notice = await self._get_admin_notice(notice_id, current_user)
        if notice.publish_status != 1:
            return

        notice.publish_status = -1
        notice.revoke_time = local_now()
        await notice.save()

    async def _get_admin_notice(
        self,
        notice_id: int,
        current_user: Users | None,
    ) -> Notices:
        """按后台管理数据范围获取通知对象。"""
        query = await apply_notice_admin_data_scope(Notices.filter(id=notice_id), current_user)
        notice = await query.first()
        if not notice:
            raise NotFound("通知不存在")
        return notice

    async def read_all(self, user_id: int) -> None:
        scan_offset = 0
        query = Notices.filter(publish_status=1).order_by("id")
        while True:
            published_notices = (
                await query.offset(scan_offset).limit(NOTICE_SCAN_BATCH_SIZE).all()
            )
            if not published_notices:
                return
            scan_offset += len(published_notices)
            published_ids = [
                notice.id
                for notice in published_notices
                if is_notice_visible_to_user(notice, user_id)
            ]
            if not published_ids:
                continue
            existing_ids = cast(
                list[int],
                await NoticeReads.filter(
                    user_id=user_id,
                    notice_id__in=published_ids,
                ).values_list("notice_id", flat=True),
            )
            missing = find_unread_notice_ids(published_ids, existing_ids)
            if missing:
                await NoticeReads.bulk_create(
                    [NoticeReads(notice_id=nid, user_id=user_id) for nid in missing],
                    ignore_conflicts=True,
                )

    async def get_my_page(
        self,
        user_id: int,
        page_num: int,
        page_size: int,
        title: str | None = None,
        is_read: int | None = None,
        current_user: Users | None = None,
    ) -> NoticeMyPageResult:
        query = Notices.filter(publish_status=1)

        if title:
            query = query.filter(title__icontains=title)

        if is_read not in (None, 0, 1):
            raise ValidationError("isRead 只能为 0 或 1")

        offset = (page_num - 1) * page_size
        scan_offset = 0
        total = 0
        notices: list[Notices] = []
        read_ids: set[int] = set()
        ordered_query = query.order_by("-publish_time", "-created_at", "-id")
        while True:
            batch = (
                await ordered_query.offset(scan_offset)
                .limit(NOTICE_SCAN_BATCH_SIZE)
                .all()
            )
            if not batch:
                break
            scan_offset += len(batch)
            visible = [
                notice for notice in batch
                if is_notice_visible_to_user(notice, user_id)
            ]
            visible_ids = [notice.id for notice in visible]
            if not visible_ids:
                continue
            batch_read_ids = set(
                cast(
                    list[int],
                    await NoticeReads.filter(
                        user_id=user_id,
                        notice_id__in=visible_ids,
                    ).values_list("notice_id", flat=True),
                )
            )
            for notice in visible:
                notice_is_read = notice.id in batch_read_ids
                if is_read is not None and notice_is_read != bool(is_read):
                    continue
                if offset <= total < offset + page_size:
                    notices.append(notice)
                    if notice_is_read:
                        read_ids.add(notice.id)
                total += 1

        can_view_target_users = await can_view_notice_target_fields(current_user)
        items = [notice_to_my_page_out(notice, read_ids, can_view_target_users) for notice in notices]

        return NoticeMyPageResult(list=items, total=total)

    async def _mark_read(self, notice_id: int, user_id: int) -> None:
        await NoticeReads.get_or_create(notice_id=notice_id, user_id=user_id)


notice_service = NoticeService()
