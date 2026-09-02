"""为 FastAPI 真实 HTTP smoke 创建隔离数据库样本。"""

from __future__ import annotations

import asyncio
import json

from tortoise import Tortoise

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.oauth import Users
from app.db.models.system import Notices, Permissions, Roles


async def seed() -> dict[str, int | str | list[int]]:
    await Tortoise.init(config=settings.tortoise_orm_config)
    button_permissions = [
        await Permissions.create(
            name=permission_code,
            type="BUTTON",
            perm=permission_code,
        )
        for permission_code in (
            "system:departments:query",
            "system:roles:query",
            "system:roles:edit",
            "system:users:add",
            "system:users:edit",
            "system:users:delete",
            "system:users:password:reset",
            "system:users:import",
            "system:users:export",
            "system:dictitems:query",
            "system:notices:query",
            "system:notices:add",
            "system:notices:edit",
            "system:notices:delete",
            "system:notices:publish",
            "system:notices:revoke",
        )
    ]
    catalog = await Permissions.create(
        name="契约目录",
        type="CATALOG",
        route_name="RuntimeContract",
        route_path="/runtime-contract",
        component="Layout",
        sort=1,
    )
    user_menu = await Permissions.create(
        name="用户管理",
        type="MENU",
        route_name="RuntimeContractUser",
        route_path="user",
        component="system/user/index",
        sort=2,
        parent=catalog,
        perm="system:users:query",
    )
    notice_menu = await Permissions.create(
        name="通知公告",
        type="MENU",
        route_name="RuntimeContractNotice",
        route_path="notices",
        component="system/notice/index",
        sort=3,
        parent=catalog,
        perm="system:notices:query",
    )
    role = await Roles.create(
        name="HTTP Smoke 角色",
        code="http-smoke",
        status=1,
        data_scope=1,
    )
    await role.permissions.add(catalog, user_menu, notice_menu, *button_permissions)
    user = await Users.create(
        username="http-smoke",
        password=get_password_hash("httpPass123"),
        name="HTTP Smoke 用户",
        is_active=1,
    )
    await user.roles.add(role)
    rbac_role = await Roles.create(
        name="HTTP Smoke RBAC 角色",
        code="http-smoke-rbac",
        status=1,
        data_scope=1,
    )
    rbac_user = await Users.create(
        username="http-smoke-rbac",
        password=get_password_hash("rbacPass123"),
        name="HTTP Smoke RBAC 用户",
        is_active=1,
    )
    await rbac_user.roles.add(rbac_role)
    notice = await Notices.create(
        title="FastAPI 真实 HTTP 通知",
        content="FastAPI 真实 HTTP 正文",
        target_type=1,
        publish_status=1,
        publisher_id=user.id,
        publisher_name=user.username,
    )
    result = {
        "username": user.username,
        "user_id": user.id,
        "notice_id": notice.id,
        "rbac_username": rbac_user.username,
        "rbac_role_id": rbac_role.id,
        "rbac_base_permission_ids": [
            permission.id
            for permission in button_permissions
            if permission.perm
            in {
                "system:departments:query",
                "system:dictitems:query",
                "system:notices:query",
            }
        ],
    }
    result["rbac_granted_permission_ids"] = [
        *result["rbac_base_permission_ids"],
        catalog.id,
        user_menu.id,
    ]
    await Tortoise.close_connections()
    return result


if __name__ == "__main__":
    print(json.dumps(asyncio.run(seed())))
