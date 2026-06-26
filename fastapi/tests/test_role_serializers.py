"""角色服务输出转换 helper 测试。"""

import uuid

import pytest

from app.db.models.system import Permissions, Roles
from app.schemas.system import RoleUpdate
from app.services.system.role_serializers import (
    build_role_menu_items,
    build_role_out,
    build_role_update_fields,
    build_role_with_permissions,
)


class TestRoleSerializers:
    """测试角色服务纯 helper。"""

    @pytest.mark.asyncio
    async def test_build_role_out_maps_role_fields(self, db):
        """角色列表输出应完整映射角色基础字段。"""
        role = await Roles.create(
            name=f"输出角色_{uuid.uuid4().hex[:6]}",
            code=f"role_out_{uuid.uuid4().hex[:6]}",
            status=1,
            sort=7,
            is_default=1,
            desc="输出描述",
        )

        result = build_role_out(role)

        assert result.id == role.id
        assert result.name == role.name
        assert result.code == role.code
        assert result.status == 1
        assert result.sort == 7
        assert result.is_default == 1
        assert result.desc == "输出描述"

    @pytest.mark.asyncio
    async def test_build_role_with_permissions_keeps_permission_ids(self, db):
        """角色详情输出应保留调用方传入的权限 ID。"""
        role = await Roles.create(
            name=f"详情角色_{uuid.uuid4().hex[:6]}",
            code=f"role_detail_{uuid.uuid4().hex[:6]}",
            status=1,
        )

        result = build_role_with_permissions(role, [3, 1, 2])

        assert result.id == role.id
        assert result.permissions == [3, 1, 2]

    def test_build_role_update_fields_ignores_unset_fields(self):
        """角色更新字段只包含显式传入的字段。"""
        update = RoleUpdate(name="新角色名", status=0)

        assert build_role_update_fields(update) == {
            "name": "新角色名",
            "status": 0,
        }

    @pytest.mark.asyncio
    async def test_build_role_menu_items_keeps_only_catalog_and_menu(self, db):
        """角色菜单输出只保留目录和菜单权限。"""
        catalog = await Permissions.create(
            name=f"目录_{uuid.uuid4().hex[:6]}",
            type="CATALOG",
        )
        menu = await Permissions.create(
            name=f"菜单_{uuid.uuid4().hex[:6]}",
            type="MENU",
        )
        button = await Permissions.create(
            name=f"按钮_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm=f"role:test:{uuid.uuid4().hex[:6]}",
        )

        result = build_role_menu_items([catalog, menu, button])

        assert [item["id"] for item in result] == [catalog.id, menu.id]
        assert {item["type"] for item in result} == {"CATALOG", "MENU"}
