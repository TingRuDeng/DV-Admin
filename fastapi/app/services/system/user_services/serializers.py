"""用户服务序列化 helper。"""

from app.db.models.oauth import Users
from app.db.models.system import Departments
from app.schemas.system import UserFormOut, UserOut
from app.services.system.field_permission import (
    USER_FIELD_PLAIN_PERMISSION,
    can_view_plain_fields,
    mask_email,
    mask_mobile,
)


class UserSerializerMixin:
    """集中处理用户输出模型转换，避免查询和写操作重复拼字段。"""

    async def _serialize_user(
        self,
        user: Users,
        current_user: Users | None = None,
    ) -> UserOut:
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
        role_ids = [role.id for role in user.roles]
        role_names = ",".join([role.name for role in user.roles])

        email, mobile = await self._visible_contact_fields(
            email=user.email,
            mobile=user.mobile,
            current_user=current_user,
        )

        return UserOut(
            id=user.id,
            username=user.username,
            name=user.name,
            email=email,
            mobile=mobile,
            avatar=user.avatar,
            gender=user.gender,
            is_active=user.is_active,
            dept_id=user.dept_id,
            dept_name=dept_name,
            roles=role_ids,
            role_names=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


    async def _serialize_user_optimized(
        self,
        user: Users,
        depts: dict[int, str],
        current_user: Users | None = None,
    ) -> UserOut:
        """
        序列化用户对象（优化版本，避免 N+1 查询）

        Args:
            user: 用户对象
            depts: 预加载的部门字典 {dept_id: dept_name}
        """
        # 从预加载的部门字典获取部门名称
        dept_name = depts.get(user.dept_id) if user.dept_id else None

        # 角色已通过 prefetch_related 加载，直接访问
        role_ids = [role.id for role in user.roles]
        role_names = ",".join([role.name for role in user.roles])

        email, mobile = await self._visible_contact_fields(
            email=user.email,
            mobile=user.mobile,
            current_user=current_user,
        )

        return UserOut(
            id=user.id,
            username=user.username,
            name=user.name,
            email=email,
            mobile=mobile,
            avatar=user.avatar,
            gender=user.gender,
            is_active=user.is_active,
            dept_id=user.dept_id,
            dept_name=dept_name,
            roles=role_ids,
            role_names=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


    async def _serialize_user_form(
        self,
        user: Users,
        current_user: Users | None = None,
    ) -> UserFormOut:
        """
        序列化用户对象（表单回填用）
        """
        base = await self._serialize_user(user, current_user)

        await user.fetch_related("roles")
        role_ids = [role.id for role in user.roles]

        base_data = base.model_dump()
        base_data["roles"] = role_ids
        return UserFormOut(**base_data)

    async def _visible_contact_fields(
        self,
        email: str | None,
        mobile: str | None,
        current_user: Users | None,
    ) -> tuple[str | None, str | None]:
        """根据当前读取者权限返回用户联系方式。"""
        can_view_plain = await can_view_plain_fields(
            current_user,
            USER_FIELD_PLAIN_PERMISSION,
        )
        if can_view_plain:
            return email, mobile
        return mask_email(email), mask_mobile(mobile)
