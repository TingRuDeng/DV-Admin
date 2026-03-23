"""
部门管理 API 路由
"""


from app.api.deps import require_permissions
from app.schemas.base import ResponseModel
from app.schemas.system import BulkDelete, DeptCreate, DeptOut, DeptTree, DeptUpdate
from app.services.system.dept_service import dept_service
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/", response_model=ResponseModel[list[DeptTree]])
async def get_depts(
    request: Request,
    current_user=require_permissions("system:departments:query"),
):
    """获取部门树形列表"""
    dept_tree = await dept_service.get_tree()
    return ResponseModel.success(data=dept_tree)


@router.get("/options", response_model=ResponseModel[list[dict]])
async def get_dept_options(
    request: Request,
    current_user=require_permissions("system:departments:query"),
):
    """获取部门下拉选项"""
    options = await dept_service.get_options()
    return ResponseModel.success(data=options)


@router.get("/{dept_id}/", response_model=ResponseModel[DeptOut])
async def get_dept(
    request: Request,
    dept_id: int,
    current_user=require_permissions("system:departments:query"),
):
    """获取部门详情"""
    dept = await dept_service.get(dept_id)
    return ResponseModel.success(data=dept)


@router.post("/", response_model=ResponseModel[DeptOut])
async def create_dept(
    request: Request,
    dept_data: DeptCreate,
    current_user=require_permissions("system:departments:add"),
):
    """创建部门"""
    dept = await dept_service.create(dept_data)
    return ResponseModel.success(data=dept, message="创建成功")


@router.put("/{dept_id}/", response_model=ResponseModel[DeptOut])
async def update_dept(
    request: Request,
    dept_id: int,
    dept_data: DeptUpdate,
    current_user=require_permissions("system:departments:edit"),
):
    """更新部门"""
    dept = await dept_service.update(dept_id, dept_data)
    return ResponseModel.success(data=dept, message="更新成功")


@router.delete("/{dept_id}/", response_model=ResponseModel[None])
async def delete_dept(
    request: Request,
    dept_id: int,
    current_user=require_permissions("system:departments:delete"),
):
    """删除部门"""
    await dept_service.delete(dept_id)
    return ResponseModel.success(message="删除成功")


@router.delete("/", response_model=ResponseModel[None])
async def bulk_delete_depts(
    request: Request,
    delete_req: BulkDelete,
    current_user=require_permissions("system:departments:delete"),
):
    """批量删除部门"""
    await dept_service.bulk_delete(delete_req.ids)
    return ResponseModel.success(message="删除成功")
