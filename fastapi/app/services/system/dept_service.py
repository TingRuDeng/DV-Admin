"""
部门管理 Service
"""
from typing import Any

from app.core.exceptions import BusinessError, NotFound, ValidationError
from app.db.models.system import Departments
from app.schemas.system import DeptCreate, DeptOut, DeptTree, DeptUpdate


class DeptService:
    """部门管理服务"""

    async def get_tree(self) -> list[DeptTree]:
        """
        获取部门树形列表
        """
        depts = await Departments.all()
        return self._build_dept_tree(depts)

    async def get(self, dept_id: int) -> DeptOut:
        """
        获取部门详情
        """
        dept = await Departments.get_or_none(id=dept_id)
        if not dept:
            raise NotFound("部门不存在")

        return DeptOut(
            id=dept.id,
            name=dept.name,
            status=dept.status,
            sort=dept.sort,
            parent_id=dept.parent_id,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
        )

    async def create(self, dept_data: DeptCreate) -> DeptOut:
        """
        创建部门
        """
        # 检查父部门是否存在
        if dept_data.parent_id:
            parent = await Departments.get_or_none(id=dept_data.parent_id)
            if not parent:
                raise ValidationError("父部门不存在")

        dept = await Departments.create(
            name=dept_data.name,
            status=dept_data.status,
            sort=dept_data.sort,
            parent_id=dept_data.parent_id,
        )

        return DeptOut(
            id=dept.id,
            name=dept.name,
            status=dept.status,
            sort=dept.sort,
            parent_id=dept.parent_id,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
        )

    async def update(self, dept_id: int, dept_data: DeptUpdate) -> DeptOut:
        """
        更新部门
        """
        dept = await Departments.get_or_none(id=dept_id)
        if not dept:
            raise NotFound("部门不存在")

        # 检查不能将自己设为父部门
        if dept_data.parent_id == dept_id:
            raise ValidationError("不能将自己设为父部门")

        update_fields = {}
        if dept_data.name is not None:
            update_fields["name"] = dept_data.name
        if dept_data.status is not None:
            update_fields["status"] = dept_data.status
        if dept_data.sort is not None:
            update_fields["sort"] = dept_data.sort
        if dept_data.parent_id is not None:
            update_fields["parent_id"] = dept_data.parent_id

        if update_fields:
            await Departments.filter(id=dept_id).update(**update_fields)
            await dept.refresh_from_db()

        return DeptOut(
            id=dept.id,
            name=dept.name,
            status=dept.status,
            sort=dept.sort,
            parent_id=dept.parent_id,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
        )

    async def delete(self, dept_id: int) -> None:
        """
        删除部门
        """
        dept = await Departments.get_or_none(id=dept_id)
        if not dept:
            raise NotFound("部门不存在")

        # 检查是否有子部门
        children = await Departments.filter(parent_id=dept_id).count()
        if children > 0:
            raise BusinessError("该部门下存在子部门，无法删除")

        await dept.delete()

    async def bulk_delete(self, ids: list[int]) -> None:
        """
        批量删除部门
        """
        for dept_id in ids:
            await self.delete(dept_id)

    async def get_options(self) -> list[dict[str, Any]]:
        """
        获取部门下拉选项
        """
        depts = await Departments.filter(status=1).all()
        return self._build_options(depts)

    def _build_dept_tree(self, depts: list[Departments], parent_id: int | None = None) -> list[DeptTree]:
        """构建部门树"""
        tree = []
        for dept in depts:
            if dept.parent_id == parent_id:
                children = self._build_dept_tree(depts, dept.id)
                dept_data = {
                    "id": dept.id,
                    "name": dept.name,
                    "label": dept.name,
                    "status": dept.status,
                    "sort": dept.sort,
                    "parent_id": dept.parent_id,
                    "created_at": dept.created_at,
                    "updated_at": dept.updated_at,
                    "children": children if children else [],
                }
                tree.append(dept_data)
        return sorted(tree, key=lambda x: x["sort"])

    def _build_options(self, depts: list[Departments], parent_id: int | None = None, level: int = 0) -> list[dict[str, Any]]:
        """构建部门选项"""
        options = []
        for dept in depts:
            if dept.parent_id == parent_id:
                prefix = "  " * level
                options.append({
                    "value": dept.id,
                    "label": f"{prefix}{dept.name}",
                })
                options.extend(self._build_options(depts, dept.id, level + 1))
        return options


# 导出服务实例
dept_service = DeptService()
