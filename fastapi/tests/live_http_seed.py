"""为 FastAPI 真实 HTTP smoke 创建隔离数据库样本。"""

from __future__ import annotations

import asyncio
import json

from tortoise import Tortoise

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.oauth import Users
from app.db.models.system import Notices, Permissions, Roles


async def seed() -> dict[str, int | str]:
    await Tortoise.init(config=settings.tortoise_orm_config)
    query_permission = await Permissions.create(
        name="system:notices:query",
        type="BUTTON",
        perm="system:notices:query",
    )
    role = await Roles.create(
        name="HTTP Smoke 角色",
        code="http-smoke",
        status=1,
        data_scope=1,
    )
    await role.permissions.add(query_permission)
    user = await Users.create(
        username="http-smoke",
        password=get_password_hash("httpPass123"),
        name="HTTP Smoke 用户",
        is_active=1,
    )
    await user.roles.add(role)
    notice = await Notices.create(
        title="FastAPI 真实 HTTP 通知",
        content="FastAPI 真实 HTTP 正文",
        target_type=1,
        publish_status=1,
        publisher_id=user.id,
        publisher_name=user.username,
    )
    result = {"username": user.username, "user_id": user.id, "notice_id": notice.id}
    await Tortoise.close_connections()
    return result


if __name__ == "__main__":
    print(json.dumps(asyncio.run(seed())))
