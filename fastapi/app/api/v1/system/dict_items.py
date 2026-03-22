# -*- coding: utf-8 -*-
"""
字典项管理 API 路由 (扁平化接口)
"""

from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api.deps import require_permissions
from app.schemas.base import PageResult, ResponseModel
from app.schemas.system import (
    BulkDelete,
    DictItemCreate,
    DictItemOut,
    DictItemUpdate,
)
from app.services.system.dict_service import dict_service

router = APIRouter()


@router.get("/", response_model=ResponseModel[PageResult[DictItemOut]])
async def get_dict_item_page(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    dict_id: Optional[int] = Query(None, alias="dict", description="字典ID"),
    label: Optional[str] = Query(None, description="标签"),
    code: Optional[str] = Query(None, alias="dictCode", description="字典编码"),
    current_user=require_permissions("system:dicts:query"),
):
    """获取字典项分页列表"""
    result = await dict_service.get_item_page(
        page=page,
        page_size=page_size,
        dict_id=dict_id,
        label=label,
        code=code,
    )
    return ResponseModel.success(data=result)


@router.post("/", response_model=ResponseModel[DictItemOut])
async def create_dict_item(
    request: Request,
    item_data: DictItemCreate,
    current_user=require_permissions("system:dicts:add"),
):
    """创建字典项"""
    item = await dict_service.create_item_flat(item_data)
    return ResponseModel.success(data=item, message="创建成功")


@router.put("/{item_id}/", response_model=ResponseModel[DictItemOut])
async def update_dict_item(
    request: Request,
    item_id: int,
    item_data: DictItemUpdate,
    current_user=require_permissions("system:dicts:edit"),
):
    """更新字典项"""
    item = await dict_service.update_item_flat(item_id, item_data)
    return ResponseModel.success(data=item, message="更新成功")


@router.delete("/{item_id}/", response_model=ResponseModel[None])
async def delete_dict_item(
    request: Request,
    item_id: int,
    current_user=require_permissions("system:dicts:delete"),
):
    """删除字典项"""
    await dict_service.delete_item_flat(item_id)
    return ResponseModel.success(message="删除成功")


@router.delete("/", response_model=ResponseModel[None])
async def batch_delete_dict_items(
    request: Request,
    delete_req: BulkDelete,
    current_user=require_permissions("system:dicts:delete"),
):
    """批量删除字典项"""
    await dict_service.batch_delete_items_flat(delete_req.ids)
    return ResponseModel.success(message="删除成功")
