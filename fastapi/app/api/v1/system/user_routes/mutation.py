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
from app.schemas.system import BulkDelete, UserCreate, UserOut, UserPartialUpdate, UserUpdate
from app.services.system.user_service import user_service

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
    user = await user_service.create(user_data)
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
    user = await user_service.update(user_id, user_data)
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
    user = await user_service.partial_update(user_id, user_data)
    return ResponseModel.success(data=user, message="更新成功")
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
    await user_service.delete(user_id, current_user.id)
    return ResponseModel.success(message="删除成功")
@router.delete(
    "/",
    response_model=ResponseModel[None],
    summary="批量删除用户",
    description=BATCH_DELETE_USERS_DESCRIPTION,
    responses=BATCH_DELETE_USERS_RESPONSES,
)
async def batch_delete_users(
    request: Request,
    delete_req: BulkDelete,
    current_user: Users = require_permissions("system:users:delete"),
) -> ResponseModel[None]:
    await user_service.batch_delete(delete_req.ids, current_user.id)
    return ResponseModel.success(message="批量删除成功")
