# -*- coding: utf-8 -*-
"""
角色管理 API 路由
"""

from typing import List, Optional

from fastapi import APIRouter, Query, Request

from app.api.deps import require_permissions
from app.schemas.base import PageResult, ResponseModel
from app.schemas.system import BulkDelete, RoleCreate, RoleOut, RoleUpdate, RoleWithPermissions
from app.services.system.role_service import role_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[PageResult[RoleOut]])
async def get_roles(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user=require_permissions("system:roles:query"),
):
    """获取角色分页列表"""
    result = await role_service.get_page(
        page=page,
        page_size=page_size,
        search=search,
    )
    return ResponseModel.success(data=result)


@router.get("/options/", response_model=ResponseModel[List[dict]])
async def get_role_options(
    request: Request,
    current_user=require_permissions("system:roles:query"),
):
    """获取角色下拉选项"""
    options = await role_service.get_options()
    return ResponseModel.success(data=options)


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
    role = await role_service.create(role_data)
    return ResponseModel.success(data=role, message="创建成功")


@router.put("/{role_id}/", response_model=ResponseModel[RoleOut])
async def update_role(
    request: Request,
    role_id: int,
    role_data: RoleUpdate,
    current_user=require_permissions("system:roles:edit"),
):
    """更新角色"""
    role = await role_service.update(role_id, role_data)
    return ResponseModel.success(data=role, message="更新成功")


@router.delete("/{role_id}/", response_model=ResponseModel[None])
async def delete_role(
    request: Request,
    role_id: int,
    current_user=require_permissions("system:roles:delete"),
):
    """删除角色"""
    await role_service.delete(role_id)
    return ResponseModel.success(message="删除成功")


@router.delete("/", response_model=ResponseModel[None])
async def batch_delete_roles(
    request: Request,
    delete_req: BulkDelete,
    current_user=require_permissions("system:roles:delete"),
):
    """批量删除角色"""
    await role_service.batch_delete(delete_req.ids)
    return ResponseModel.success(message="批量删除成功")


@router.get("/{role_id}/menu-ids/", response_model=ResponseModel[List[int]])
async def get_role_menu_ids(
    request: Request,
    role_id: int,
    current_user=require_permissions("system:roles:query"),
):
    """获取角色的菜单ID列表"""
    menu_ids = await role_service.get_menu_ids(role_id)
    return ResponseModel.success(data=menu_ids)


@router.get("/{role_id}/menus/", response_model=ResponseModel[List[dict]])
async def get_role_menus(
    request: Request,
    role_id: int,
    current_user=require_permissions("system:roles:query"),
):
    """获取角色的菜单列表"""
    menus = await role_service.get_menus(role_id)
    return ResponseModel.success(data=menus)
