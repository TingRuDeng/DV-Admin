"""用户写操作 API 路由。"""

from fastapi import APIRouter, Request

from app.api.deps import require_permissions
from app.api.v1.system.user_routes.mutation_docs import (
    BATCH_DELETE_USERS_DESCRIPTION,
    BATCH_DELETE_USERS_RESPONSES,
    CREATE_USER_DESCRIPTION,
    CREATE_USER_RESPONSES,
    DELETE_USER_DESCRIPTION,
    DELETE_USER_RESPONSES,
    PARTIAL_UPDATE_USER_DESCRIPTION,
    PARTIAL_UPDATE_USER_RESPONSES,
)
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import (
    BatchDeleteRequest,
    BatchDeleteResult,
    UserCreate,
    UserOut,
    UserPartialUpdate,
    UserUpdate,
)
from app.services.system.batch_delete import normalize_batch_ids
from app.services.system.user_service import user_service
from app.utils.audit import set_audit_context, set_audit_object

router = APIRouter()

@router.post(
    "/",
    response_model=ResponseModel[UserOut],
    summary="创建用户",
    description=CREATE_USER_DESCRIPTION,
    responses=CREATE_USER_RESPONSES,
)
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: Users = require_permissions("system:users:add"),
) -> ResponseModel[UserOut]:
    set_audit_object(
        request,
        "system.users",
        "",
        changed_fields=list(user_data.model_dump(exclude_unset=True)),
    )
    user = await user_service.create(user_data, current_user=current_user)
    set_audit_object(
        request,
        "system.users",
        user.id,
        changed_fields=list(user_data.model_dump(exclude_unset=True)),
    )
    return ResponseModel.success(data=user, message="创建成功")
@router.put("/{user_id}/", response_model=ResponseModel[UserOut])
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    current_user: Users = require_permissions("system:users:edit"),
) -> ResponseModel[UserOut]:
    """
    更新用户
    """
    set_audit_object(
        request,
        "system.users",
        user_id,
        changed_fields=list(user_data.model_dump(exclude_unset=True)),
    )
    user = await user_service.update(user_id, user_data, current_user=current_user)
    return ResponseModel.success(data=user, message="更新成功")
@router.patch(
    "/{user_id}/",
    response_model=ResponseModel[UserOut],
    summary="局部更新用户",
    description=PARTIAL_UPDATE_USER_DESCRIPTION,
    responses=PARTIAL_UPDATE_USER_RESPONSES,
)
async def partial_update_user(
    request: Request,
    user_id: int,
    user_data: UserPartialUpdate,
    current_user: Users = require_permissions("system:users:edit"),
) -> ResponseModel[UserOut]:
    set_audit_object(
        request,
        "system.users",
        user_id,
        changed_fields=list(user_data.model_dump(exclude_unset=True)),
    )
    user = await user_service.partial_update(
        user_id,
        user_data,
        current_user=current_user,
    )
    return ResponseModel.success(data=user, message="更新成功")
@router.post(
    "/batch-delete/retry/",
    response_model=ResponseModel[BatchDeleteResult],
    summary="重试失败用户删除",
)
async def retry_batch_delete_users(
    request: Request,
    delete_req: BatchDeleteRequest,
    current_user: Users = require_permissions("system:users:delete"),
) -> ResponseModel[BatchDeleteResult]:
    ids = normalize_batch_ids(delete_req.ids, resource_name="用户")
    set_audit_object(request, "system.users", "", changed_fields=["ids", "retry"])
    set_audit_context(request, batch_count=len(ids), batch_ids=[str(item) for item in ids[:100]])
    result = await user_service.retry_batch_delete(ids, current_user=current_user)
    set_audit_context(
        request,
        success_count=result.success_count,
        failed_count=result.failed_count,
        failure_codes=sorted({item.error_code for item in result.failures}),
    )
    return ResponseModel.success(data=result, message="批量删除重试完成")


@router.delete(
    "/{user_id}/",
    response_model=ResponseModel[None],
    summary="删除用户",
    description=DELETE_USER_DESCRIPTION,
    responses=DELETE_USER_RESPONSES,
)
async def delete_user(
    request: Request,
    user_id: int,
    current_user: Users = require_permissions("system:users:delete"),
) -> ResponseModel[None]:
    set_audit_object(request, "system.users", user_id)
    await user_service.delete(user_id, current_user=current_user)
    return ResponseModel.success(message="删除成功")
@router.delete(
    "/",
    response_model=ResponseModel[BatchDeleteResult],
    summary="批量删除用户",
    description=BATCH_DELETE_USERS_DESCRIPTION,
    responses=BATCH_DELETE_USERS_RESPONSES,
)
async def batch_delete_users(
    request: Request,
    delete_req: BatchDeleteRequest,
    current_user: Users = require_permissions("system:users:delete"),
) -> ResponseModel[BatchDeleteResult]:
    ids = normalize_batch_ids(delete_req.ids, resource_name="用户")
    set_audit_object(request, "system.users", "", changed_fields=["ids"])
    set_audit_context(
        request,
        batch_count=len(ids),
        batch_ids=[str(item) for item in ids[:100]],
    )
    result = await user_service.batch_delete(ids, current_user=current_user)
    set_audit_context(
        request,
        success_count=result.success_count,
        failed_count=result.failed_count,
        failure_codes=sorted({item.error_code for item in result.failures}),
    )
    return ResponseModel.success(data=result, message="批量删除完成")
