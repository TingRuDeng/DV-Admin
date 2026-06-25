"""用户服务序列化 helper。"""

from app.db.models.oauth import Users
from app.db.models.system import Departments
from app.schemas.system import UserFormOut, UserOut


class UserSerializerMixin:
    """集中处理用户输出模型转换，避免查询和写操作重复拼字段。"""

    async def _serialize_user(self, user: Users) -> UserOut:
        """
        序列化用户对象（处理关联字段）
        """
        # 获取部门名称
        dept_name = None
        if user.dept_id:
            department = await Departments.get_or_none(id=user.dept_id)
            if department:
                dept_name = department.name

        # 获取角色名称
        await user.fetch_related("roles")
        role_names = ",".join([role.name for role in user.roles])

        return UserOut(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            avatar=user.avatar,
            gender=user.gender,
            is_active=user.is_active,
            dept_id=user.dept_id,
            dept_name=dept_name,
            role_names=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


    async def _serialize_user_optimized(self, user: Users, depts: dict[int, str]) -> UserOut:
        """
        序列化用户对象（优化版本，避免 N+1 查询）

        Args:
            user: 用户对象
            depts: 预加载的部门字典 {dept_id: dept_name}
        """
        # 从预加载的部门字典获取部门名称
        dept_name = depts.get(user.dept_id) if user.dept_id else None

        # 角色已通过 prefetch_related 加载，直接访问
        role_names = ",".join([role.name for role in user.roles])

        return UserOut(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            avatar=user.avatar,
            gender=user.gender,
            is_active=user.is_active,
            dept_id=user.dept_id,
            dept_name=dept_name,
            role_names=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


    async def _serialize_user_form(self, user: Users) -> UserFormOut:
        """
        序列化用户对象（表单回填用）
        """
        base = await self._serialize_user(user)

        await user.fetch_related("roles")
        role_ids = [role.id for role in user.roles]

        return UserFormOut(**base.model_dump(), roles=role_ids)

