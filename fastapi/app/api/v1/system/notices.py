"""
通知公告 API
"""


from fastapi import APIRouter, Query, Request

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import (
    BatchDeleteRequest,
    BatchDeleteResult,
    NoticeAdminPageResult,
    NoticeCreate,
    NoticeDetailOut,
    NoticeFormOut,
    NoticeMyPageResult,
    NoticePageOut,
    NoticeUpdate,
)
from app.services.system.batch_delete import normalize_batch_ids
from app.services.system.notice_service import notice_service
from app.utils.audit import set_audit_context, set_audit_object

router = APIRouter()


@router.get("/page", response_model=ResponseModel[NoticeAdminPageResult])
async def get_notice_page(
    request: Request,
    page_num: int = Query(1, alias="pageNum", ge=1, description="页码"),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页数量"),
    title: str | None = Query(None, description="标题"),
    publish_status: int | None = Query(None, alias="publishStatus", description="发布状态"),
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_page(
        page_num=page_num,
        page_size=page_size,
        title=title,
        publish_status=publish_status,
        current_user=current_user,
    )
    return ResponseModel.success(data=data)


@router.get("/{notice_id}/form", response_model=ResponseModel[NoticeFormOut])
async def get_notice_form(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_form(notice_id, current_user=current_user)
    return ResponseModel.success(data=data)


@router.post("", response_model=ResponseModel[NoticePageOut])
async def create_notice(
    request: Request,
    notice_data: NoticeCreate,
    current_user: Users = require_permissions("system:notices:add"),
):
    set_audit_object(
        request,
        "system.notices",
        "",
        changed_fields=list(notice_data.model_dump(exclude_unset=True)),
    )
    data = await notice_service.create(
        notice_data,
        publisher_id=current_user.id,
        publisher_name=current_user.name or current_user.username,
        current_user=current_user,
    )
    set_audit_object(
        request,
        "system.notices",
        data.id,
        changed_fields=list(notice_data.model_dump(exclude_unset=True)),
    )
    return ResponseModel.success(data=data, message="创建成功")


@router.put("/read-all", response_model=ResponseModel[None])
async def read_all_notices(
    request: Request,
    current_user: Users = require_permissions("system:notices:query"),
):
    set_audit_object(request, "system.notices", "", changed_fields=["readAll"])
    await notice_service.read_all(user_id=current_user.id)
    return ResponseModel.success(message="操作成功")


@router.put("/{notice_id}", response_model=ResponseModel[NoticePageOut])
async def update_notice(
    request: Request,
    notice_id: int,
    notice_data: NoticeUpdate,
    current_user: Users = require_permissions("system:notices:edit"),
):
    set_audit_object(
        request,
        "system.notices",
        notice_id,
        changed_fields=list(notice_data.model_dump(exclude_unset=True)),
    )
    data = await notice_service.update(notice_id, notice_data, current_user=current_user)
    return ResponseModel.success(data=data, message="更新成功")


@router.post(
    "/batch-delete/retry/",
    response_model=ResponseModel[BatchDeleteResult],
    summary="重试失败通知删除",
)
async def retry_batch_delete_notices(
    request: Request,
    delete_req: BatchDeleteRequest,
    current_user: Users = require_permissions("system:notices:delete"),
):
    """逐条重试通知删除。"""
    ids = normalize_batch_ids(delete_req.ids, resource_name="通知")
    set_audit_object(request, "system.notices", "", changed_fields=["ids", "retry"])
    set_audit_context(request, batch_count=len(ids), batch_ids=[str(item) for item in ids[:100]])
    result = await notice_service.retry_batch_delete(ids, current_user=current_user)
    set_audit_context(
        request,
        success_count=result.success_count,
        failed_count=result.failed_count,
        failure_codes=sorted({item.error_code for item in result.failures}),
    )
    return ResponseModel.success(data=result, message="批量删除重试完成")


@router.delete("", response_model=ResponseModel[BatchDeleteResult])
@router.delete("/", response_model=ResponseModel[BatchDeleteResult])
async def batch_delete_notices(
    request: Request,
    delete_req: BatchDeleteRequest,
    current_user: Users = require_permissions("system:notices:delete"),
):
    """使用 JSON body 批量删除通知。"""
    ids = normalize_batch_ids(delete_req.ids, resource_name="通知")
    set_audit_object(request, "system.notices", "", changed_fields=["ids"])
    set_audit_context(request, batch_count=len(ids), batch_ids=[str(item) for item in ids[:100]])
    result = await notice_service.batch_delete(ids, current_user=current_user)
    set_audit_context(
        request,
        success_count=result.success_count,
        failed_count=result.failed_count,
        failure_codes=sorted({item.error_code for item in result.failures}),
    )
    return ResponseModel.success(data=result, message="批量删除完成")


@router.delete("/{ids}", response_model=ResponseModel[BatchDeleteResult])
async def delete_notices(
    request: Request,
    ids: str,
    current_user: Users = require_permissions("system:notices:delete"),
):
    try:
        parsed_ids = [int(x) for x in ids.split(",") if x.strip()]
    except ValueError as exc:
        from app.core.exceptions import ValidationError

        raise ValidationError("通知 ID 必须为正整数") from exc
    parsed_ids = normalize_batch_ids(parsed_ids, resource_name="通知")
    set_audit_object(request, "system.notices", "", changed_fields=["ids"])
    set_audit_context(
        request,
        batch_count=len(parsed_ids),
        batch_ids=[str(item) for item in parsed_ids[:100]],
    )
    result = await notice_service.batch_delete(parsed_ids, current_user=current_user)
    set_audit_context(
        request,
        success_count=result.success_count,
        failed_count=result.failed_count,
        failure_codes=sorted({item.error_code for item in result.failures}),
    )
    return ResponseModel.success(data=result, message="批量删除完成")


@router.put("/{notice_id}/publish", response_model=ResponseModel[None])
async def publish_notice(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:publish"),
):
    set_audit_object(request, "system.notices", notice_id, changed_fields=["publishStatus"])
    await notice_service.publish(notice_id, current_user=current_user)
    return ResponseModel.success(message="发布成功")


@router.put("/{notice_id}/revoke", response_model=ResponseModel[None])
async def revoke_notice(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:revoke"),
):
    set_audit_object(request, "system.notices", notice_id, changed_fields=["publishStatus"])
    await notice_service.revoke(notice_id, current_user=current_user)
    return ResponseModel.success(message="撤回成功")


@router.get("/{notice_id}/detail", response_model=ResponseModel[NoticeDetailOut])
async def get_notice_detail(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_detail(notice_id, user_id=current_user.id)
    return ResponseModel.success(data=data)


@router.get("/my-page/", response_model=ResponseModel[NoticeMyPageResult])
async def get_my_notice_page(
    request: Request,
    page_num: int = Query(1, alias="pageNum", ge=1, description="页码"),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页数量"),
    title: str | None = Query(None, description="标题"),
    is_read: int | None = Query(
        None,
        alias="isRead",
        ge=0,
        le=1,
        description="是否已读(1:是;0:否)",
    ),
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_my_page(
        user_id=current_user.id,
        page_num=page_num,
        page_size=page_size,
        title=title,
        is_read=is_read,
        current_user=current_user,
    )
    return ResponseModel.success(data=data)
