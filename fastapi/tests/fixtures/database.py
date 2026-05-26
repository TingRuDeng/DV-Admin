"""测试数据库生命周期夹具。"""

import asyncio
import uuid
from pathlib import Path
from tempfile import gettempdir

import pytest_asyncio
from tortoise import Tortoise
from tortoise.exceptions import ConfigurationError

TEST_DB_PATH = Path(gettempdir()) / f"dv_admin_fastapi_test_{uuid.uuid4().hex}.sqlite3"


async def ensure_test_db_initialized() -> None:
    """确保测试数据库上下文可用。"""
    try:
        Tortoise.get_connection("default")
        return
    except (ConfigurationError, RuntimeError):
        pass

    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {"file_path": str(TEST_DB_PATH)},
                }
            },
            "apps": {
                "models": {
                    "models": [
                        "app.db.models.oauth",
                        "app.db.models.system",
                    ],
                    "default_connection": "default",
                }
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai",
        },
        _enable_global_fallback=True,
    )

    if not TEST_DB_PATH.exists():
        await Tortoise.generate_schemas()

    from app.core.cache import cache_service

    await cache_service.init()


async def reset_test_db_state() -> None:
    """清空测试库中的业务表，并重置缓存。"""
    connection = Tortoise.get_connection("default")
    tables = await connection.execute_query_dict(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        """
    )
    table_names = [row["name"] for row in tables]

    statements = ["PRAGMA foreign_keys=OFF;"]
    statements.extend(f'DELETE FROM "{table_name}";' for table_name in table_names)

    sqlite_sequence = await connection.execute_query_dict(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'sqlite_sequence'"
    )
    if sqlite_sequence:
        statements.append("DELETE FROM sqlite_sequence;")

    statements.append("PRAGMA foreign_keys=ON;")
    await connection.execute_script("\n".join(statements))

    from app.core.cache import cache_service
    from app.core.redis import redis_manager

    await cache_service._memory_cache.clear()
    cache_service._redis_cache._redis = None
    cache_service._backend = cache_service._memory_cache
    cache_service._use_redis = False
    redis_manager._client = None
    redis_manager._pool = None


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """初始化测试数据库，并在会话结束后清理临时库。"""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    await ensure_test_db_initialized()

    yield

    await Tortoise.close_connections()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture(scope="session")
async def session_loop():
    """复用当前 pytest-asyncio 会话事件循环。"""
    return asyncio.get_running_loop()


@pytest_asyncio.fixture(scope="function")
async def db():
    """确保函数级测试始终能拿到干净的数据库上下文。"""
    await ensure_test_db_initialized()
    await reset_test_db_state()
    yield
