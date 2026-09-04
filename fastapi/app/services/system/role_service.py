"""
角色管理 Service
"""
from typing import Any

from loguru import logger
from tortoise.transactions import in_transaction

from app.core.cache import CacheKeys, cache_service
from app.core.exceptions import NotFound, ValidationError
from app.db.models.system import Departments, Permissions, Roles
from app.schemas.base import PageResult
from app.schemas.system import (
    BatchDeleteFailure,
    BatchDeleteResult,
    BatchDeleteSuccessItem,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleWithPermissions,
)
from app.services.system.access_cache import clear_user_access_cache, get_role_user_ids
from app.services.system.batch_delete import build_batch_delete_result, normalize_batch_ids
from app.services.system.role_serializers import (
    build_role_menu_items,
    build_role_out,
    build_role_update_fields,
    build_role_with_permissions,
)

PROTECTED_ROLE_IDENTIFIERS = frozenset(
    {
        "admin",
        "superadmin",
        "administrator",
        "超级管理员",
        "系统管理员",
    }
)


class _ProtectedRoleError(Exception):
    """内部控制流异常：锁定后发现角色已变为受保护角色。"""


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

    async def _clear_assigned_user_access_cache(self, role_id: int) -> None:
        """角色权限变化后清除所有关联用户的权限和菜单缓存。"""
        await clear_user_access_cache(await get_role_user_ids(role_id))

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
        roles = (
            await query.prefetch_related("permissions", "data_depts")
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        role_list = [
            build_role_out(
                role,
                [perm.id for perm in role.permissions],
                [dept.id for dept in role.data_depts],
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

        await role.fetch_related("permissions", "data_depts")
        permission_ids = [perm.id for perm in role.permissions]
        dept_ids = [dept.id for dept in role.data_depts]

        return build_role_with_permissions(role, permission_ids, dept_ids)

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
            data_scope=role_data.data_scope,
            desc=role_data.desc or "",
        )

        # 关联权限
        if role_data.permission_ids:
            perms = await Permissions.filter(id__in=role_data.permission_ids).all()
            await role.permissions.add(*perms)
        if role_data.dept_ids:
            depts = await Departments.filter(id__in=role_data.dept_ids).all()
            await role.data_depts.add(*depts)

        # 清除角色选项缓存
        await self._clear_role_cache()

        await role.fetch_related("permissions", "data_depts")
        return build_role_out(
            role,
            [perm.id for perm in role.permissions],
            [dept.id for dept in role.data_depts],
        )

    async def update(self, role_id: int, role_data: RoleUpdate) -> RoleOut:
        """
        更新角色
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        # 更新字段
        update_fields = build_role_update_fields(role_data)

        if update_fields:
            await Roles.filter(id=role_id).update(**update_fields)
            await role.refresh_from_db()

        # 更新权限
        if role_data.permission_ids is not None:
            await role.permissions.clear()
            if role_data.permission_ids:
                perms = await Permissions.filter(id__in=role_data.permission_ids).all()
                await role.permissions.add(*perms)
            await self._clear_assigned_user_access_cache(role_id)
        if role_data.dept_ids is not None:
            await role.data_depts.clear()
            if role_data.dept_ids:
                depts = await Departments.filter(id__in=role_data.dept_ids).all()
                await role.data_depts.add(*depts)

        # 清除缓存
        await self._clear_role_cache(role_id)

        await role.fetch_related("permissions", "data_depts")
        return build_role_out(
            role,
            [perm.id for perm in role.permissions],
            [dept.id for dept in role.data_depts],
        )

    async def assign_menus(self, role_id: int, menu_ids: list[int]) -> list[int]:
        """
        分配角色菜单权限
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        unique_ids = list(dict.fromkeys(menu_ids))
        permissions = await Permissions.filter(id__in=unique_ids).all()
        if len(permissions) != len(unique_ids):
            raise ValidationError("权限不存在")

        await role.permissions.clear()
        if permissions:
            await role.permissions.add(*permissions)
        await self._clear_assigned_user_access_cache(role_id)
        await self._clear_role_cache(role_id)
        return unique_ids

    async def delete(self, role_id: int) -> None:
        """
        删除角色
        """
        role = await Roles.get_or_none(id=role_id)
        if not role:
            raise NotFound("角色不存在")

        if self._is_protected_role(role):
            raise ValidationError("系统角色不可删除")

        await role.delete()

        # 清除缓存
        await self._clear_role_cache(role_id)

    async def batch_delete(
        self,
        ids: list[int],
        current_user=None,
    ) -> BatchDeleteResult:
        """批量删除角色并返回逐条结果。"""
        unique_ids = normalize_batch_ids(ids, resource_name="角色")
        roles = await Roles.filter(id__in=unique_ids).all()
        if len(roles) != len(unique_ids):
            raise NotFound("角色不存在")

        roles_by_id = {role.id: role for role in roles}
        success_items: list[BatchDeleteSuccessItem] = []
        failures: list[BatchDeleteFailure] = []
        for role_id in unique_ids:
            role = roles_by_id[role_id]
            object_name = role.name
            if self._is_protected_role(role):
                failures.append(self._protected_failure(role_id, object_name))
                continue

            outcome = await self._delete_one_for_batch(role_id, object_name)
            if isinstance(outcome, BatchDeleteFailure):
                failures.append(outcome)
            else:
                success_items.append(outcome)

        return build_batch_delete_result(unique_ids, success_items, failures)

    async def retry_batch_delete(
        self,
        ids: list[int],
        current_user=None,
    ) -> BatchDeleteResult:
        """逐条重新校验并重试角色删除。"""
        unique_ids = normalize_batch_ids(ids, resource_name="角色")
        success_items: list[BatchDeleteSuccessItem] = []
        failures: list[BatchDeleteFailure] = []
        for role_id in unique_ids:
            role = await Roles.get_or_none(id=role_id)
            if role is None:
                failures.append(
                    BatchDeleteFailure(
                        object_id=str(role_id),
                        error_code="ALREADY_DELETED",
                        message="角色已不存在",
                        retryable=False,
                    )
                )
                continue

            object_name = role.name
            if self._is_protected_role(role):
                failures.append(self._protected_failure(role_id, object_name))
                continue

            outcome = await self._delete_one_for_batch(
                role_id,
                object_name,
                missing_code="ALREADY_DELETED",
                missing_message="角色已不存在",
            )
            if isinstance(outcome, BatchDeleteFailure):
                failures.append(outcome)
            else:
                success_items.append(outcome)

        return build_batch_delete_result(unique_ids, success_items, failures)

    @staticmethod
    def _is_protected_role(role: Roles) -> bool:
        """按名称和编码识别内置系统角色。"""
        return any(
            isinstance(value, str)
            and value.strip().casefold() in PROTECTED_ROLE_IDENTIFIERS
            for value in (role.name, role.code)
        )

    @staticmethod
    def _protected_failure(role_id: int, object_name: str) -> BatchDeleteFailure:
        return BatchDeleteFailure(
            object_id=str(role_id),
            object_name=object_name,
            error_code="PROTECTED_OBJECT",
            message="系统角色不可删除",
            retryable=False,
        )

    async def _delete_one_for_batch(
        self,
        role_id: int,
        object_name: str,
        *,
        missing_code: str = "NOT_FOUND",
        missing_message: str = "角色不存在",
    ) -> BatchDeleteSuccessItem | BatchDeleteFailure:
        """在独立事务中删除单个角色并清理关联用户缓存。"""
        try:
            async with in_transaction() as connection:
                locked_role = await (
                    Roles.filter(id=role_id).using_db(connection).select_for_update().first()
                )
                if locked_role is None:
                    raise NotFound(missing_message)
                if self._is_protected_role(locked_role):
                    raise _ProtectedRoleError
                # 角色行锁定后再读取关联用户，确保缓存清理集合与本次删除事务一致。
                affected_user_ids = await get_role_user_ids(
                    role_id,
                    using_db=connection,
                )
                await locked_role.delete(using_db=connection)
        except _ProtectedRoleError:
            return self._protected_failure(role_id, object_name)
        except NotFound:
            return BatchDeleteFailure(
                object_id=str(role_id),
                object_name=object_name,
                error_code=missing_code,
                message=missing_message,
                retryable=False,
            )
        except Exception:  # noqa: BLE001 - 单条失败不能阻塞其余项目
            return BatchDeleteFailure(
                object_id=str(role_id),
                object_name=object_name,
                error_code="DELETE_FAILED",
                message="删除角色失败",
                retryable=True,
            )

        # 数据库提交后，缓存只是后处理；其故障不能把已删除对象报告成失败。
        try:
            await self._clear_role_cache(role_id)
        except Exception as exc:  # noqa: BLE001 - 记录后继续处理用户缓存
            logger.warning("角色 {} 删除后清理角色缓存失败: {}", role_id, exc)
        try:
            await clear_user_access_cache(affected_user_ids)
        except Exception as exc:  # noqa: BLE001 - 记录后保留删除结果
            logger.warning("角色 {} 删除后清理用户权限缓存失败: {}", role_id, exc)
        return BatchDeleteSuccessItem(
            object_id=str(role_id),
            object_name=object_name,
        )

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
        return build_role_menu_items(list(role.permissions))


# 导出服务实例
role_service = RoleService()
