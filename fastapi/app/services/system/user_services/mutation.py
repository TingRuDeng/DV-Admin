"""用户写操作服务。"""

from typing import Any

from app.core.config import settings
from app.core.exceptions import BusinessError, NotFound, ValidationError
from app.core.security import get_password_hash
from app.db.models.oauth import Users
from app.db.models.system import Roles
from app.schemas.system import UserCreate, UserOut, UserPartialUpdate, UserUpdate
from app.services.system.user_services.cache import UserCacheMixin
from app.services.system.user_services.serializers import UserSerializerMixin


class UserMutationMixin(UserCacheMixin, UserSerializerMixin):
    """承载用户创建、更新、删除和密码重置。"""

    async def create(self, user_in: UserCreate) -> UserOut:
        """
        创建用户
        """
        # 检查用户名是否已存在
        existing = await Users.get_or_none(username=user_in.username)
        if existing:
            raise ValidationError("用户名已存在")

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
        if user_in.role_ids:
            roles = await Roles.filter(id__in=user_in.role_ids).all()
            await user.roles.add(*roles)

        return await self._serialize_user(user)


    async def update(self, user_id: int, user_in: UserUpdate) -> UserOut:
        """
        更新用户
        """
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise NotFound("用户不存在")

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
        if user_in.role_ids is not None:
            # 清除现有角色
            await user.roles.clear()
            # 添加新角色
            if user_in.role_ids:
                roles = await Roles.filter(id__in=user_in.role_ids).all()
                await user.roles.add(*roles)

        # 清除用户缓存（角色变更会影响权限和菜单）
        await self._clear_user_cache(user_id)

        return await self._serialize_user(user)


    async def partial_update(self, user_id: int, user_in: UserPartialUpdate) -> UserOut:
        """
        局部更新用户（状态）
        """
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise NotFound("用户不存在")

        # 更新状态
        user.is_active = user_in.is_active
        await user.save()

        # 清除用户缓存
        await self._clear_user_cache(user_id)

        return await self._serialize_user(user)


    async def delete(self, user_id: int, current_user_id: int) -> None:
        """
        删除用户
        """
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise NotFound("用户不存在")

        # 不能删除自己
        if user.id == current_user_id:
            raise BusinessError("不能删除当前登录用户")

        # 删除用户（级联删除角色关联）
        await user.delete()

        # 清除用户缓存
        await self._clear_user_cache(user_id)


    async def batch_delete(self, ids: list[int], current_user_id: int) -> None:
        """
        批量删除用户
        """
        if current_user_id in ids:
            raise BusinessError("不能删除当前登录用户")

        # 批量删除
        await Users.filter(id__in=ids).delete()

        # 清除所有被删除用户的缓存
        for user_id in ids:
            await self._clear_user_cache(user_id)


    async def reset_password(self, user_id: int) -> None:
        """
        重置用户密码
        """
        user = await Users.get_or_none(id=user_id)
        if not user:
            raise NotFound("用户不存在")

        default_password = settings.default_password
        user.password = get_password_hash(default_password)
        await user.save()

