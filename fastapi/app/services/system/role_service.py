"""
角色管理 Service
"""
from typing import Any

from app.core.cache import CacheKeys, cache_service
from app.core.exceptions import NotFound, ValidationError
from app.db.models.system import Permissions, Roles
from app.schemas.base import PageResult
from app.schemas.system import RoleCreate, RoleOut, RoleUpdate, RoleWithPermissions


class RoleService:
    """角色管理服务"""

    # 缓存 TTL（秒）
    CACHE_TTL = 600  # 10分钟

    async def _clear_role_cache(self, role_id: int | None = None) -> None:
        """
        清除角色缓存

        Args:
            role_id: 角色ID，为 None 时清除所有角色缓存
        """
        if role_id:
            # 清除特定角色缓存
            cache_key = CacheKeys.format_key(CacheKeys.ROLE_DETAIL, role_id=role_id)
            await cache_service.delete(cache_key)
            cache_key = CacheKeys.format_key(CacheKeys.ROLE_PERMISSIONS, role_id=role_id)
            await cache_service.delete(cache_key)
        # 清除角色选项缓存
        await cache_service.delete(CacheKeys.ROLE_OPTIONS)

    async def get_page(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> PageResult[RoleOut]:
        """
        获取角色分页列表
        """
        query = Roles.all()

        if search:
            query = query.filter(name__icontains=search)

        total = await query.count()
        roles = await query.offset((page - 1) * page_size).limit(page_size).all()

        role_list = [
            RoleOut(
                id=role.id,
                name=role.name,
                code=role.code,
                status=role.status,
                sort=role.sort,
                is_default=role.is_default,
                desc=role.desc,
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
            for role in roles
        ]

        return PageResult.create(
            total=total, page=page, page_size=page_size, results=role_list
        )

    async def get(self, role_id: int) -> RoleWithPermissions:
        """
        获取角色详情
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        await role.fetch_related("permissions")
        permission_ids = [perm.id for perm in role.permissions]

        return RoleWithPermissions(
            id=role.id,
            name=role.name,
            code=role.code,
            status=role.status,
            sort=role.sort,
            is_default=role.is_default,
            desc=role.desc,
            permissions=permission_ids,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

    async def create(self, role_data: RoleCreate) -> RoleOut:
        """
        创建角色
        """
        # 检查角色名是否已存在
        existing = await Roles.get_or_none(name=role_data.name)
        if existing:
            raise ValidationError("角色名称已存在")

        # 创建角色
        role = await Roles.create(
            name=role_data.name,
            code=role_data.code,
            status=role_data.status,
            sort=role_data.sort,
            is_default=role_data.is_default,
            desc=role_data.desc or "",
        )

        # 关联权限
        if role_data.permission_ids:
            perms = await Permissions.filter(id__in=role_data.permission_ids).all()
            await role.permissions.add(*perms)

        # 清除角色选项缓存
        await self._clear_role_cache()

        return RoleOut(
            id=role.id,
            name=role.name,
            code=role.code,
            status=role.status,
            sort=role.sort,
            is_default=role.is_default,
            desc=role.desc,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

    async def update(self, role_id: int, role_data: RoleUpdate) -> RoleOut:
        """
        更新角色
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        # 更新字段
        update_fields = {}
        if role_data.name is not None:
            update_fields["name"] = role_data.name
        if role_data.code is not None:
            update_fields["code"] = role_data.code
        if role_data.status is not None:
            update_fields["status"] = role_data.status
        if role_data.sort is not None:
            update_fields["sort"] = role_data.sort
        if role_data.is_default is not None:
            update_fields["is_default"] = role_data.is_default
        if role_data.desc is not None:
            update_fields["desc"] = role_data.desc

        if update_fields:
            await Roles.filter(id=role_id).update(**update_fields)
            await role.refresh_from_db()

        # 更新权限
        if role_data.permission_ids is not None:
            await role.permissions.clear()
            if role_data.permission_ids:
                perms = await Permissions.filter(id__in=role_data.permission_ids).all()
                await role.permissions.add(*perms)

        # 清除缓存
        await self._clear_role_cache(role_id)

        return RoleOut(
            id=role.id,
            name=role.name,
            code=role.code,
            status=role.status,
            sort=role.sort,
            is_default=role.is_default,
            desc=role.desc,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

    async def delete(self, role_id: int) -> None:
        """
        删除角色
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        await role.delete()

        # 清除缓存
        await self._clear_role_cache(role_id)

    async def batch_delete(self, ids: list[int]) -> None:
        """
        批量删除角色
        """
        await Roles.filter(id__in=ids).delete()

        # 清除所有角色缓存
        for role_id in ids:
            await self._clear_role_cache(role_id)

    async def get_options(self) -> list[dict[str, Any]]:
        """
        获取角色下拉选项（带缓存）
        """
        async def _fetch_options():
            roles = await Roles.filter(status=1).all()
            return [{"id": role.id, "label": role.name} for role in roles]

        return await cache_service.get_or_set(
            CacheKeys.ROLE_OPTIONS, _fetch_options, ttl=self.CACHE_TTL
        )

    async def get_menu_ids(self, role_id: int) -> list[int]:
        """
        获取角色的菜单ID列表
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        await role.fetch_related("permissions")
        permission_ids = [perm.id for perm in role.permissions]
        return permission_ids

    async def get_menus(self, role_id: int) -> list[dict[str, Any]]:
        """
        获取角色的菜单列表
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        await role.fetch_related("permissions")
        menus = []
        for perm in role.permissions:
            if perm.type in ["CATALOG", "MENU"]:
                menus.append({
                    "id": perm.id,
                    "name": perm.name,
                    "type": perm.type,
                })
        return menus


# 导出服务实例
role_service = RoleService()
