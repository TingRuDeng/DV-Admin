"""
菜单/权限管理 API 路由
"""


from fastapi import APIRouter, Request

from app.api.deps import require_permissions
from app.schemas.base import ResponseModel
from app.schemas.system import MenuCreate, MenuOut, MenuTree, MenuUpdate
from app.services.system.menu_service import menu_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[list[MenuTree]])
async def get_menus(
    request: Request,
    current_user=require_permissions("system:menus:query"),
):
    """获取菜单树形列表"""
    menu_tree = await menu_service.get_tree()
    return ResponseModel.success(data=menu_tree)


@router.get("/options/", response_model=ResponseModel[list[dict]])
async def get_menu_options(
    request: Request,
    current_user=require_permissions("system:menus:query"),
):
    """获取菜单下拉选项"""
    options = await menu_service.get_options()
    return ResponseModel.success(data=options)


@router.get("/perms", response_model=ResponseModel[list[str]])
async def get_permissions(
    request: Request,
    current_user=require_permissions("system:menus:query"),
):
    """获取所有权限标识"""
    perms = await menu_service.get_permissions()
    return ResponseModel.success(data=perms)


@router.get("/{menu_id}/", response_model=ResponseModel[MenuOut])
async def get_menu(
    request: Request,
    menu_id: int,
    current_user=require_permissions("system:menus:query"),
):
    """获取菜单详情"""
    menu = await menu_service.get(menu_id)
    return ResponseModel.success(data=menu)


@router.post("/", response_model=ResponseModel[MenuOut])
async def create_menu(
    request: Request,
    menu_data: MenuCreate,
    current_user=require_permissions("system:menus:add"),
):
    """创建菜单"""
    menu = await menu_service.create(menu_data)
    return ResponseModel.success(data=menu, message="创建成功")


@router.put("/{menu_id}/", response_model=ResponseModel[MenuOut])
async def update_menu(
    request: Request,
    menu_id: int,
    menu_data: MenuUpdate,
    current_user=require_permissions("system:menus:edit"),
):
    """更新菜单"""
    menu = await menu_service.update(menu_id, menu_data)
    return ResponseModel.success(data=menu, message="更新成功")


@router.delete("/{menu_id}/", response_model=ResponseModel[None])
async def delete_menu(
    request: Request,
    menu_id: int,
    current_user=require_permissions("system:menus:delete"),
):
    """删除菜单"""
    await menu_service.delete(menu_id)
    return ResponseModel.success(message="删除成功")
