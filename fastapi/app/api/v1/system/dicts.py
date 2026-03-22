# -*- coding: utf-8 -*-
"""
字典管理 API 路由
"""

from typing import List, Optional

from fastapi import APIRouter, Query, Request

from app.api.deps import require_permissions
from app.schemas.base import PageResult, ResponseModel
from app.schemas.system import (
    BulkDelete,
    DictDataCreate,
    DictDataOut,
    DictDataUpdate,
    DictItemCreate,
    DictItemOut,
    DictItemUpdate,
    DictWithItems,
)
from app.services.system.dict_service import dict_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[PageResult[DictDataOut]])
async def get_dicts(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user=require_permissions("system:dicts:query"),
):
    """获取字典类型分页列表"""
    result = await dict_service.get_dict_page(
        page=page,
        page_size=page_size,
        search=search,
    )
    return ResponseModel.success(data=result)


@router.get("/{dict_id}/", response_model=ResponseModel[DictWithItems])
async def get_dict(
    request: Request,
    dict_id: int,
    current_user=require_permissions("system:dicts:query"),
):
    """获取字典类型详情（包含字典项）"""
    dict_data = await dict_service.get_dict(dict_id)
    return ResponseModel.success(data=dict_data)


@router.post("/", response_model=ResponseModel[DictDataOut])
async def create_dict(
    request: Request,
    dict_data: DictDataCreate,
    current_user=require_permissions("system:dicts:add"),
):
    """创建字典类型"""
    d = await dict_service.create_dict(dict_data)
    return ResponseModel.success(data=d, message="创建成功")


@router.put("/{dict_id}/", response_model=ResponseModel[DictDataOut])
async def update_dict(
    request: Request,
    dict_id: int,
    dict_data: DictDataUpdate,
    current_user=require_permissions("system:dicts:edit"),
):
    """更新字典类型"""
    d = await dict_service.update_dict(dict_id, dict_data)
    return ResponseModel.success(data=d, message="更新成功")


@router.delete("/{dict_id}/", response_model=ResponseModel[None])
async def delete_dict(
    dict_id: int,
    current_user=require_permissions("system:dicts:delete"),
):
    """删除字典类型"""
    await dict_service.delete_dict(dict_id)
    return ResponseModel.success(message="删除成功")


@router.delete("/", response_model=ResponseModel[None])
async def batch_delete_dicts(
    request: Request,
    delete_req: BulkDelete,
    current_user=require_permissions("system:dicts:delete"),
):
    """批量删除字典类型"""
    await dict_service.batch_delete_dicts(delete_req.ids)
    return ResponseModel.success(message="删除成功")


# 字典项管理
@router.get("/{dict_id}/items", response_model=ResponseModel[List[DictItemOut]])
async def get_dict_items(
    request: Request,
    dict_id: int,
    current_user=require_permissions("system:dicts:view"),
):
    """获取字典项列表"""
    items = await dict_service.get_items(dict_id)
    return ResponseModel.success(data=items)


@router.post("/{dict_id}/items", response_model=ResponseModel[DictItemOut])
async def create_dict_item(
    request: Request,
    dict_id: int,
    item_data: DictItemCreate,
    current_user=require_permissions("system:dicts:add"),
):
    """创建字典项"""
    item = await dict_service.create_item(dict_id, item_data)
    return ResponseModel.success(data=item, message="创建成功")


@router.put("/{dict_id}/items/{item_id}", response_model=ResponseModel[DictItemOut])
async def update_dict_item(
    dict_id: int,
    item_id: int,
    item_data: DictItemUpdate,
    current_user=require_permissions("system:dicts:edit"),
):
    """更新字典项"""
    item = await dict_service.update_item(dict_id, item_id, item_data)
    return ResponseModel.success(data=item, message="更新成功")


@router.delete("/{dict_id}/items/{item_id}", response_model=ResponseModel[None])
async def delete_dict_item(
    request: Request,
    dict_id: int,
    item_id: int,
    current_user=require_permissions("system:dicts:delete"),
):
    """删除字典项"""
    await dict_service.delete_item(dict_id, item_id)
    return ResponseModel.success(message="删除成功")


@router.get("/code/{code}", response_model=ResponseModel[List[DictItemOut]])
async def get_dict_by_code(
    request: Request,
    code: str,
):
    """根据编码获取字典项（公开接口，用于前端获取字典）"""
    items = await dict_service.get_items_by_code(code)
    return ResponseModel.success(data=items)
