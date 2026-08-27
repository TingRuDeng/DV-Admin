"""用户写操作服务。"""

from typing import Any

from tortoise.transactions import in_transaction

from app.core.config import settings
from app.core.exceptions import BusinessError, NotFound, ValidationError
from app.core.security import get_password_hash
from app.db.models.oauth import Users
from app.db.models.system import Roles
from app.schemas.system import UserCreate, UserOut, UserPartialUpdate, UserUpdate
from app.services.system.data_scope import (
    apply_user_data_scope,
    can_manage_user_department,
)
from app.services.system.field_permission import (
    can_write_sensitive_user_fields,
    has_sensitive_user_write,
)
from app.services.system.user_services.cache import UserCacheMixin
from app.services.system.user_services.serializers import UserSerializerMixin


class UserMutationMixin(UserCacheMixin, UserSerializerMixin):
    """承载用户创建、更新、删除和密码重置。"""

    async def create(
        self,
        user_in: UserCreate,
        current_user: Users | None = None,
    ) -> UserOut:
        """
        创建用户
        """
        # 检查用户名是否已存在
        existing = await Users.get_or_none(username=user_in.username)
        if existing:
            raise ValidationError("用户名已存在")

        await self._validate_sensitive_user_write(
            email=user_in.email,
            mobile=user_in.mobile,
            current_user=current_user,
        )
        await self._validate_department_write(current_user, user_in.dept_id)
        roles = await self._resolve_roles(user_in.role_ids)

        # 检查手机号是否已存在
        if user_in.mobile:
            existing = await Users.get_or_none(mobile=user_in.mobile)
            if existing:
                raise ValidationError("手机号已存在")

        # 创建用户
        password = user_in.password or settings.default_password
        user = await Users.create(
            username=user_in.username,
            password=get_password_hash(password),
            name=user_in.name,
            email=user_in.email,
            mobile=user_in.mobile,
            avatar=user_in.avatar,
            gender=user_in.gender,
            is_active=user_in.is_active,
            dept_id=user_in.dept_id,
        )

        # 关联角色
        if roles:
            await user.roles.add(*roles)

        return await self._serialize_user(user, current_user)


    async def update(
        self,
        user_id: int,
        user_in: UserUpdate,
        current_user: Users | None = None,
    ) -> UserOut:
        """
        更新用户
        """
        user = await self._get_scoped_user(user_id, current_user)

        await self._validate_sensitive_user_write(
            email=user_in.email,
            mobile=user_in.mobile,
            current_user=current_user,
        )
        if user_in.dept_id is not None:
            await self._validate_department_write(current_user, user_in.dept_id)
        roles = (
            await self._resolve_roles(user_in.role_ids)
            if user_in.role_ids is not None
            else None
        )

        # 检查手机号是否已被其他用户使用
        if user_in.mobile:
            existing = await Users.get_or_none(mobile=user_in.mobile)
            if existing and existing.id != user_id:
                raise ValidationError("手机号已存在")

        # 更新用户字段
        update_fields: dict[str, Any] = {}
        if user_in.name is not None:
            update_fields["name"] = user_in.name
        if user_in.email is not None:
            update_fields["email"] = user_in.email
        if user_in.mobile is not None:
            update_fields["mobile"] = user_in.mobile
        if user_in.gender is not None:
            update_fields["gender"] = user_in.gender
        if user_in.is_active is not None:
            update_fields["is_active"] = user_in.is_active
        if user_in.dept_id is not None:
            update_fields["dept_id"] = user_in.dept_id
        if user_in.avatar is not None:
            update_fields["avatar"] = user_in.avatar

        if update_fields:
            await Users.filter(id=user_id).update(**update_fields)
            await user.refresh_from_db()

        # 更新角色关联
        if roles is not None:
            # 清除现有角色
            await user.roles.clear()
            # 添加新角色
            if roles:
                await user.roles.add(*roles)

        # 清除用户缓存（角色变更会影响权限和菜单）
        await self._clear_user_cache(user_id)

        return await self._serialize_user(user, current_user)

    async def _validate_sensitive_user_write(
        self,
        email: str | None,
        mobile: str | None,
        current_user: Users | None,
    ) -> None:
        """校验当前操作者是否可写入用户手机号和邮箱。"""
        if not has_sensitive_user_write(email=email, mobile=mobile):
            return
        if await can_write_sensitive_user_fields(current_user):
            return
        raise ValidationError("缺少字段写入权限，不能写入手机号或邮箱")


    async def partial_update(
        self,
        user_id: int,
        user_in: UserPartialUpdate,
        current_user: Users | None = None,
    ) -> UserOut:
        """
        局部更新用户（状态）
        """
        user = await self._get_scoped_user(user_id, current_user)

        # 更新状态
        user.is_active = user_in.is_active
        await user.save()

        # 清除用户缓存
        await self._clear_user_cache(user_id)

        return await self._serialize_user(user, current_user)


    async def delete(
        self,
        user_id: int,
        current_user: Users | None = None,
    ) -> None:
        """
        删除用户
        """
        # 不能删除自己
        if current_user is not None and user_id == current_user.id:
            raise BusinessError("不能删除当前登录用户")

        user = await self._get_scoped_user(user_id, current_user)

        # 删除用户（级联删除角色关联）
        await user.delete()

        # 清除用户缓存
        await self._clear_user_cache(user_id)


    async def batch_delete(
        self,
        ids: list[int],
        current_user: Users | None = None,
    ) -> None:
        """
        批量删除用户
        """
        unique_ids = list(dict.fromkeys(ids))
        if not unique_ids:
            raise ValidationError("用户 ID 列表不能为空")
        if current_user is not None and current_user.id in unique_ids:
            raise BusinessError("不能删除当前登录用户")

        async with in_transaction() as connection:
            query = await apply_user_data_scope(
                Users.all().using_db(connection),
                current_user,
            )
            users = await query.filter(id__in=unique_ids).select_for_update().all()
            if len(users) != len(unique_ids):
                raise NotFound("用户不存在")

            await query.filter(id__in=unique_ids).delete()

        # 清除所有被删除用户的缓存
        for user_id in unique_ids:
            await self._clear_user_cache(user_id)


    async def reset_password(
        self,
        user_id: int,
        current_user: Users | None = None,
    ) -> None:
        """
        重置用户密码
        """
        user = await self._get_scoped_user(user_id, current_user)

        default_password = settings.default_password
        user.password = get_password_hash(default_password)
        await user.save()

    async def _get_scoped_user(
        self,
        user_id: int,
        current_user: Users | None,
    ) -> Users:
        """按操作者数据范围读取目标用户，不泄露越权对象是否存在。"""
        query = await apply_user_data_scope(Users.all(), current_user)
        user = await query.filter(id=user_id).first()
        if user is None:
            raise NotFound("用户不存在")
        return user

    async def _validate_department_write(
        self,
        current_user: Users | None,
        dept_id: int | None,
    ) -> None:
        if await can_manage_user_department(current_user, dept_id):
            return
        raise ValidationError("目标部门超出当前用户数据范围")

    async def _resolve_roles(
        self,
        role_ids: list[int] | None,
    ) -> list[Roles]:
        """完整解析角色 ID，禁止静默忽略不存在的角色。"""
        unique_role_ids = list(dict.fromkeys(role_ids or []))
        if not unique_role_ids:
            return []
        roles = await Roles.filter(id__in=unique_role_ids).all()
        if len(roles) != len(unique_role_ids):
            raise ValidationError("角色不存在")
        return roles
