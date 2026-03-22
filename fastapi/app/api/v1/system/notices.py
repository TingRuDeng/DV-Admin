# -*- coding: utf-8 -*-
"""
通知公告 API
"""

from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import (
    NoticeAdminPageResult,
    NoticeCreate,
    NoticeDetailOut,
    NoticeFormOut,
    NoticeMyPageResult,
    NoticePageOut,
    NoticeUpdate,
)
from app.services.system.notice_service import notice_service

router = APIRouter()


@router.get("/page", response_model=ResponseModel[NoticeAdminPageResult])
async def get_notice_page(
    request: Request,
    page_num: int = Query(1, alias="pageNum", ge=1, description="页码"),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页数量"),
    title: Optional[str] = Query(None, description="标题"),
    publish_status: Optional[int] = Query(None, alias="publishStatus", description="发布状态"),
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_page(
        page_num=page_num,
        page_size=page_size,
        title=title,
        publish_status=publish_status,
    )
    return ResponseModel.success(data=data)


@router.get("/{notice_id}/form", response_model=ResponseModel[NoticeFormOut])
async def get_notice_form(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_form(notice_id)
    return ResponseModel.success(data=data)


@router.post("", response_model=ResponseModel[NoticePageOut])
async def create_notice(
    request: Request,
    notice_data: NoticeCreate,
    current_user: Users = require_permissions("system:notices:add"),
):
    data = await notice_service.create(
        notice_data, publisher_id=current_user.id, publisher_name=current_user.name or current_user.username
    )
    return ResponseModel.success(data=data, message="创建成功")


@router.put("/{notice_id}", response_model=ResponseModel[NoticePageOut])
async def update_notice(
    request: Request,
    notice_id: int,
    notice_data: NoticeUpdate,
    current_user: Users = require_permissions("system:notices:edit"),
):
    data = await notice_service.update(notice_id, notice_data)
    return ResponseModel.success(data=data, message="更新成功")


@router.delete("/{ids}", response_model=ResponseModel[None])
async def delete_notices(
    request: Request,
    ids: str,
    current_user: Users = require_permissions("system:notices:delete"),
):
    id_list = [int(x) for x in ids.split(",") if x.strip()]
    await notice_service.delete_by_ids(id_list)
    return ResponseModel.success(message="删除成功")


@router.put("/{notice_id}/publish", response_model=ResponseModel[None])
async def publish_notice(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:publish"),
):
    await notice_service.publish(notice_id)
    return ResponseModel.success(message="发布成功")


@router.put("/{notice_id}/revoke", response_model=ResponseModel[None])
async def revoke_notice(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:revoke"),
):
    await notice_service.revoke(notice_id)
    return ResponseModel.success(message="撤回成功")


@router.get("/{notice_id}/detail", response_model=ResponseModel[NoticeDetailOut])
async def get_notice_detail(
    request: Request,
    notice_id: int,
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_detail(notice_id, user_id=current_user.id)
    return ResponseModel.success(data=data)


@router.put("/read-all", response_model=ResponseModel[None])
async def read_all_notices(
    request: Request,
    current_user: Users = require_permissions("system:notices:query"),
):
    await notice_service.read_all(user_id=current_user.id)
    return ResponseModel.success(message="操作成功")


@router.get("/my-page/", response_model=ResponseModel[NoticeMyPageResult])
async def get_my_notice_page(
    request: Request,
    page_num: int = Query(1, alias="pageNum", ge=1, description="页码"),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页数量"),
    title: Optional[str] = Query(None, description="标题"),
    is_read: Optional[int] = Query(None, alias="isRead", description="是否已读(1:是;0:否)"),
    current_user: Users = require_permissions("system:notices:query"),
):
    data = await notice_service.get_my_page(
        user_id=current_user.id,
        page_num=page_num,
        page_size=page_size,
        title=title,
        is_read=is_read,
    )
    return ResponseModel.success(data=data)
