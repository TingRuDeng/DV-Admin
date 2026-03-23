"""
数据库初始化模块

提供数据库连接初始化和关闭功能。
"""

from tortoise import Tortoise

from app.core.config import settings
from app.core.exceptions import APIException


async def init_db() -> None:
    """
    初始化数据库连接

    初始化 Tortoise ORM 并生成数据库表。
    """
    try:
        # 初始化 Tortoise ORM
        await Tortoise.init(config=settings.tortoise_orm_config)

        # 生成数据库表（开发环境使用，生产环境建议使用迁移工具）
        if settings.is_development:
            await Tortoise.generate_schemas()

    except Exception as e:
        raise APIException(
            code=500,
            message=f"数据库初始化失败: {str(e)}",
        )


async def close_db() -> None:
    """
    关闭数据库连接

    优雅地关闭所有数据库连接。
    """
    await Tortoise.close_connections()


async def check_db_connection() -> bool:
    """
    检查数据库连接状态

    Returns:
        连接是否正常
    """
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        return True
    except Exception:
        return False
