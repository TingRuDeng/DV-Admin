"""
角色管理 API 路由
"""


from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import require_permissions
from app.api.pagination import PaginationParams, page_params
from app.schemas.base import PageResult, ResponseModel
from app.schemas.system import (
    BatchDeleteRequest,
    BatchDeleteResult,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleWithPermissions,
)
from app.schemas.system_roles import RoleMenuAssign
from app.services.system.batch_delete import normalize_batch_ids
from app.services.system.role_service import role_service
from app.utils.audit import set_audit_context, set_audit_object

router = APIRouter()


@router.get("/", response_model=ResponseModel[PageResult[RoleOut]])
async def get_roles(
    request: Request,
    pagination: PaginationParams = Depends(page_params),
    search: str | None = Query(None, description="搜索关键词"),
    current_user=require_permissions("system:roles:query"),
):
    """获取角色分页列表"""
    result = await role_service.get_page(
        page=pagination.page,
        page_size=pagination.page_size,
        search=search,
    )
    return ResponseModel.success(data=result)


@router.get("/options/", response_model=ResponseModel[list[dict]])
async def get_role_options(
    request: Request,
    current_user=require_permissions("system:roles:query"),
):
    """获取角色下拉选项"""
    options = await role_service.get_options()
    return ResponseModel.success(data=options)


@router.post(
    "/batch-delete/retry/",
    response_model=ResponseModel[BatchDeleteResult],
    summary="重试失败角色删除",
)
async def retry_batch_delete_roles(
    request: Request,
    delete_req: BatchDeleteRequest,
    current_user=require_permissions("system:roles:delete"),
):
    """逐条重试角色删除。"""
    ids = normalize_batch_ids(delete_req.ids, resource_name="角色")
    set_audit_object(request, "system.roles", "", changed_fields=["ids", "retry"])
    set_audit_context(request, batch_count=len(ids), batch_ids=[str(item) for item in ids[:100]])
    result = await role_service.retry_batch_delete(ids, current_user=current_user)
    set_audit_context(
        request,
        success_count=result.success_count,
        failed_count=result.failed_count,
        failure_codes=sorted({item.error_code for item in result.failures}),
    )
    return ResponseModel.success(data=result, message="批量删除重试完成")


@router.get("/{role_id}/", response_model=ResponseModel[RoleWithPermissions])
async def get_role(
    request: Request,
    role_id: int,
    current_user=require_permissions("system:roles:query"),
):
    """获取角色详情"""
    role = await role_service.get(role_id)
    return ResponseModel.success(data=role)


@router.post("/", response_model=ResponseModel[RoleOut])
async def create_role(
    request: Request,
    role_data: RoleCreate,
    current_user=require_permissions("system:roles:add"),
):
    """创建角色"""
    set_audit_object(
        request,
        "system.roles",
        "",
        changed_fields=list(role_data.model_dump(exclude_unset=True)),
    )
    role = await role_service.create(role_data)
    set_audit_object(
        request,
        "system.roles",
        role.id,
        changed_fields=list(role_data.model_dump(exclude_unset=True)),
    )
    return ResponseModel.success(data=role, message="创建成功")


@router.put("/{role_id}/", response_model=ResponseModel[RoleOut])
async def update_role(
    request: Request,
    role_id: int,
    role_data: RoleUpdate,
    current_user=require_permissions("system:roles:edit"),
):
    """更新角色"""
    set_audit_object(
        request,
        "system.roles",
        role_id,
        changed_fields=list(role_data.model_dump(exclude_unset=True)),
    )
    role = await role_service.update(role_id, role_data)
    return ResponseModel.success(data=role, message="更新成功")


@router.delete("/{role_id}/", response_model=ResponseModel[None])
async def delete_role(
    request: Request,
    role_id: int,
    current_user=require_permissions("system:roles:delete"),
):
    """删除角色"""
    set_audit_object(request, "system.roles", role_id)
    await role_service.delete(role_id)
    return ResponseModel.success(message="删除成功")


@router.delete("/", response_model=ResponseModel[BatchDeleteResult])
async def batch_delete_roles(
    request: Request,
    delete_req: BatchDeleteRequest,
    current_user=require_permissions("system:roles:delete"),
):
    """批量删除角色"""
    set_audit_object(request, "system.roles", "", changed_fields=["ids"])
    ids = normalize_batch_ids(delete_req.ids, resource_name="角色")
    set_audit_context(
        request,
        batch_count=len(ids),
        batch_ids=[str(item) for item in ids[:100]],
    )
    result = await role_service.batch_delete(ids, current_user=current_user)
    set_audit_context(
        request,
        success_count=result.success_count,
        failed_count=result.failed_count,
        failure_codes=sorted({item.error_code for item in result.failures}),
    )
    return ResponseModel.success(data=result, message="批量删除完成")


@router.put("/{role_id}/menus/", response_model=ResponseModel[list[int]])
async def assign_role_menus(
    request: Request,
    role_id: int,
    menu_data: RoleMenuAssign,
    current_user=require_permissions("system:roles:edit"),
):
    """分配角色菜单权限"""
    set_audit_object(
        request,
        "system.roles",
        role_id,
        changed_fields=["menuIds"],
        assigned_menu_ids=menu_data.menu_ids[:100],
    )
    menu_ids = await role_service.assign_menus(role_id, menu_data.menu_ids)
    return ResponseModel.success(data=menu_ids, message="分配权限成功")


@router.get("/{role_id}/menu-ids/", response_model=ResponseModel[list[int]])
async def get_role_menu_ids(
    request: Request,
    role_id: int,
    current_user=require_permissions("system:roles:query"),
):
    """获取角色的菜单ID列表"""
    menu_ids = await role_service.get_menu_ids(role_id)
    return ResponseModel.success(data=menu_ids)


@router.get("/{role_id}/menus/", response_model=ResponseModel[list[dict]])
async def get_role_menus(
    request: Request,
    role_id: int,
    current_user=require_permissions("system:roles:query"),
):
    """获取角色的菜单列表"""
    menus = await role_service.get_menus(role_id)
    return ResponseModel.success(data=menus)
