#!/usr/bin/env python3
"""验证 Tortoise ORM 迁移基线、既有库接管和模型漂移。"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = PROJECT_ROOT / "app" / "db" / "migrations"
MIGRATION_CONFIG = "app.db.migration_config.TORTOISE_ORM"
TEST_SECRET_KEY = "migration-validation-key-at-least-sixty-four-characters-long-123456"
BASELINE_MIGRATION = "0001_initial"
LATEST_MIGRATION = "0003_operationlog_audit_context"
OPERATION_LOG_TABLE = "system_operation_log"
MIGRATION_ROW_USERNAME = "__migration_validation_0001__"
MIGRATION_REQUEST_ID = "migration-validation-request-id"
REQUIRED_TABLES = {
    "system_departments",
    "system_dict_items",
    "system_dicts",
    "system_notice_reads",
    "system_notices",
    "system_operation_log",
    "system_permissions",
    "system_roles",
    "system_roles_to_system_departments",
    "system_roles_to_system_permissions",
    "system_users",
    "system_users_to_system_roles",
}


def build_env(database_url: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "test",
            "DATABASE_URL": database_url,
            "SECRET_KEY": TEST_SECRET_KEY,
        }
    )
    return env


def run_tortoise(database_url: str, *args: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tortoise",
            "-c",
            MIGRATION_CONFIG,
            *args,
        ],
        cwd=PROJECT_ROOT,
        env=build_env(database_url),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        raise RuntimeError(
            f"Tortoise 迁移命令失败（exit {result.returncode}）: {' '.join(args)}"
        )
    return result.stdout


def sqlite_tables(database_path: Path) -> set[str]:
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            """
        ).fetchall()
    return {row[0] for row in rows}


def migration_history(database_url: str) -> str:
    return run_tortoise(database_url, "history", "models")


def assert_migration_history(database_url: str, *required_migrations: str) -> None:
    history = run_tortoise(database_url, "history", "models")
    missing = [migration for migration in required_migrations if migration not in history]
    if missing:
        raise RuntimeError(f"迁移历史缺少: {missing}")


def validate_fresh_database(database_url: str, sqlite_path: Path | None = None) -> None:
    run_tortoise(database_url, "migrate")
    assert_migration_history(database_url, BASELINE_MIGRATION, LATEST_MIGRATION)
    if sqlite_path is not None:
        actual_tables = sqlite_tables(sqlite_path)
        expected_tables = REQUIRED_TABLES | {"tortoise_migrations"}
        if actual_tables != expected_tables:
            raise RuntimeError(
                f"空库迁移表集合不匹配: expected={sorted(expected_tables)}, "
                f"actual={sorted(actual_tables)}"
            )


async def create_runtime_schema(database_url: str) -> None:
    os.environ.update(build_env(database_url))

    from tortoise import Tortoise

    from app.core.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    await Tortoise.init(config=settings.tortoise_orm_config)
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()
    get_settings.cache_clear()


def database_backend(database_url: str) -> str:
    scheme = urlsplit(database_url).scheme
    if scheme == "sqlite":
        return "sqlite"
    if scheme in {"mysql", "mysql+asyncmy"}:
        return "mysql"
    raise RuntimeError(f"增量迁移校验暂不支持数据库协议: {scheme}")


async def open_database_connection(database_url: str) -> Any:
    os.environ.update(build_env(database_url))

    from tortoise import Tortoise, connections

    from app.core.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()
    await Tortoise.init(config=settings.tortoise_orm_config)
    return connections.get("default")


async def close_database_connection() -> None:
    from tortoise import Tortoise

    from app.core.config import get_settings

    await Tortoise.close_connections()
    get_settings.cache_clear()


async def operation_log_columns(connection: Any, backend: str) -> set[str]:
    if backend == "sqlite":
        _, rows = await connection.execute_query(
            f'PRAGMA table_info("{OPERATION_LOG_TABLE}")'
        )
        return {str(row["name"]) for row in rows}

    _, rows = await connection.execute_query(
        """
        SELECT COLUMN_NAME AS column_name
        FROM information_schema.columns
        WHERE table_schema = DATABASE() AND table_name = %s
        """,
        [OPERATION_LOG_TABLE],
    )
    return {str(row["column_name"]) for row in rows}


async def request_id_index_names(connection: Any, backend: str) -> set[str]:
    if backend == "sqlite":
        _, indexes = await connection.execute_query(
            f'PRAGMA index_list("{OPERATION_LOG_TABLE}")'
        )
        matched_indexes: set[str] = set()
        for index in indexes:
            index_name = str(index["name"])
            escaped_index_name = index_name.replace('"', '""')
            _, index_columns = await connection.execute_query(
                f'PRAGMA index_info("{escaped_index_name}")'
            )
            if [str(column["name"]) for column in index_columns] == ["request_id"]:
                matched_indexes.add(index_name)
        return matched_indexes

    _, rows = await connection.execute_query(
        """
        SELECT INDEX_NAME AS index_name, COLUMN_NAME AS column_name
        FROM information_schema.statistics
        WHERE table_schema = DATABASE() AND table_name = %s
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """,
        [OPERATION_LOG_TABLE],
    )
    index_columns: dict[str, list[str]] = {}
    for row in rows:
        index_columns.setdefault(str(row["index_name"]), []).append(
            str(row["column_name"])
        )
    return {
        index_name
        for index_name, columns in index_columns.items()
        if columns == ["request_id"]
    }


async def seed_legacy_operation_log(database_url: str) -> None:
    backend = database_backend(database_url)
    connection = await open_database_connection(database_url)
    placeholder = "?" if backend == "sqlite" else "%s"
    values = [
        "2026-07-25 12:00:00",
        "2026-07-25 12:00:00",
        1,
        MIGRATION_ROW_USERNAME,
        "迁移校验",
        "升级前日志",
        "POST",
        "/api/v1/migration-validation",
        "",
        "{}",
        500,
        '{"message":"legacy-row"}',
        "127.0.0.1",
        "validator",
        "test",
        10,
        0,
        "legacy-error",
    ]
    columns = (
        "created_at",
        "updated_at",
        "user_id",
        "username",
        "name",
        "operation",
        "method",
        "path",
        "query_params",
        "request_body",
        "response_status",
        "response_body",
        "ip",
        "browser",
        "os",
        "execution_time",
        "status",
        "error_msg",
    )
    try:
        actual_columns = await operation_log_columns(connection, backend)
        unexpected_columns = actual_columns & {
            "request_id",
            "object_type",
            "object_id",
            "request_context",
        }
        if unexpected_columns:
            raise RuntimeError(
                "0001_initial 阶段不应存在后续审计字段: "
                f"{sorted(unexpected_columns)}"
            )

        placeholders = ", ".join([placeholder] * len(values))
        await connection.execute_query(
            f"""
            INSERT INTO {OPERATION_LOG_TABLE} ({", ".join(columns)})
            VALUES ({placeholders})
            """,
            values,
        )
        _, rows = await connection.execute_query(
            f"""
            SELECT username, operation
            FROM {OPERATION_LOG_TABLE}
            WHERE username = {placeholder}
            """,
            [MIGRATION_ROW_USERNAME],
        )
        if len(rows) != 1 or rows[0]["operation"] != "升级前日志":
            raise RuntimeError("0001_initial 代表数据写入失败")
    finally:
        await close_database_connection()


async def assert_upgraded_operation_log(
    database_url: str,
    expected_request_id: str,
    update_request_id: bool = False,
) -> None:
    backend = database_backend(database_url)
    connection = await open_database_connection(database_url)
    placeholder = "?" if backend == "sqlite" else "%s"
    try:
        actual_columns = await operation_log_columns(connection, backend)
        required_columns = {
            "request_id",
            "object_type",
            "object_id",
            "request_context",
        }
        missing_columns = required_columns - actual_columns
        if missing_columns:
            raise RuntimeError(f"增量迁移后缺少审计列: {sorted(missing_columns)}")

        index_names = await request_id_index_names(connection, backend)
        if len(index_names) != 1:
            raise RuntimeError(
                f"request_id 单列索引数量异常: expected=1, actual={sorted(index_names)}"
            )

        _, rows = await connection.execute_query(
            f"""
            SELECT operation, request_id, object_type, object_id, request_context
            FROM {OPERATION_LOG_TABLE}
            WHERE username = {placeholder}
            """,
            [MIGRATION_ROW_USERNAME],
        )
        if len(rows) != 1:
            raise RuntimeError("增量迁移未保留 0001_initial 代表数据")
        if rows[0]["operation"] != "升级前日志":
            raise RuntimeError("增量迁移修改了既有操作日志内容")
        if rows[0]["request_id"] != expected_request_id:
            raise RuntimeError(
                "request_id 默认值或幂等校验失败: "
                f"expected={expected_request_id!r}, actual={rows[0]['request_id']!r}"
            )
        if rows[0]["object_type"] != "" or rows[0]["object_id"] != "":
            raise RuntimeError(
                "对象关联字段默认值异常: "
                f"object_type={rows[0]['object_type']!r}, "
                f"object_id={rows[0]['object_id']!r}"
            )

        request_context = rows[0]["request_context"]
        if isinstance(request_context, bytes):
            request_context = request_context.decode()
        if isinstance(request_context, str):
            try:
                request_context = json.loads(request_context)
            except json.JSONDecodeError as exc:
                raise RuntimeError("request_context 默认值不是有效 JSON") from exc
        if request_context != {}:
            raise RuntimeError(
                "request_context 默认值异常: " f"actual={request_context!r}"
            )

        if update_request_id:
            await connection.execute_query(
                f"""
                UPDATE {OPERATION_LOG_TABLE}
                SET request_id = {placeholder}
                WHERE username = {placeholder}
                """,
                [MIGRATION_REQUEST_ID, MIGRATION_ROW_USERNAME],
            )
    finally:
        await close_database_connection()


def validate_incremental_database(database_url: str) -> None:
    run_tortoise(database_url, "migrate", "models", BASELINE_MIGRATION)
    history = migration_history(database_url)
    if BASELINE_MIGRATION not in history or LATEST_MIGRATION in history:
        raise RuntimeError("无法将数据库精确迁移到 0001_initial")

    asyncio.run(seed_legacy_operation_log(database_url))
    run_tortoise(database_url, "migrate", "models", LATEST_MIGRATION)
    assert_migration_history(database_url, BASELINE_MIGRATION, LATEST_MIGRATION)
    asyncio.run(
        assert_upgraded_operation_log(
            database_url,
            expected_request_id="",
            update_request_id=True,
        )
    )

    run_tortoise(database_url, "migrate")
    assert_migration_history(database_url, BASELINE_MIGRATION, LATEST_MIGRATION)
    asyncio.run(
        assert_upgraded_operation_log(
            database_url,
            expected_request_id=MIGRATION_REQUEST_ID,
        )
    )


def validate_existing_sqlite_baseline() -> None:
    with tempfile.TemporaryDirectory(prefix="dv-admin-existing-") as temp_dir:
        database_path = Path(temp_dir) / "existing.sqlite3"
        database_url = f"sqlite://{database_path}"
        asyncio.run(create_runtime_schema(database_url))

        before_tables = sqlite_tables(database_path)
        if before_tables != REQUIRED_TABLES:
            raise RuntimeError(
                f"既有 schema 表集合不匹配: expected={sorted(REQUIRED_TABLES)}, "
                f"actual={sorted(before_tables)}"
            )

        run_tortoise(database_url, "migrate", "--fake")
        assert_migration_history(database_url, BASELINE_MIGRATION, LATEST_MIGRATION)

        after_tables = sqlite_tables(database_path)
        expected_tables = REQUIRED_TABLES | {"tortoise_migrations"}
        if after_tables != expected_tables:
            raise RuntimeError("fake baseline 修改了既有业务 schema")


def migration_snapshot() -> dict[Path, bytes]:
    return {
        path: path.read_bytes()
        for path in MIGRATIONS_DIR.glob("*.py")
        if path.name != "__init__.py"
    }


def validate_model_drift() -> None:
    before = migration_snapshot()
    with tempfile.TemporaryDirectory(prefix="dv-admin-drift-") as temp_dir:
        database_url = f"sqlite://{Path(temp_dir) / 'drift.sqlite3'}"
        output = run_tortoise(database_url, "makemigrations", "models")

    after = migration_snapshot()
    created_paths = set(after) - set(before)
    changed_paths = {path for path in before if after.get(path) != before[path]}

    for path in created_paths:
        path.unlink()
    for path in changed_paths:
        path.write_bytes(before[path])

    if created_paths or changed_paths or "No changes detected" not in output:
        changed = sorted(path.name for path in created_paths | changed_paths)
        raise RuntimeError(f"FastAPI 模型存在未提交迁移: {changed}")


def validate_all_sqlite() -> None:
    with tempfile.TemporaryDirectory(prefix="dv-admin-fresh-") as temp_dir:
        database_path = Path(temp_dir) / "fresh.sqlite3"
        validate_fresh_database(f"sqlite://{database_path}", database_path)
    with tempfile.TemporaryDirectory(prefix="dv-admin-incremental-") as temp_dir:
        database_path = Path(temp_dir) / "incremental.sqlite3"
        validate_incremental_database(f"sqlite://{database_path}")
    validate_existing_sqlite_baseline()
    validate_model_drift()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("all-sqlite", "fresh", "incremental"),
        help=(
            "all-sqlite 验证 SQLite 空库、增量、既有库和漂移；"
            "fresh 验证指定空库；incremental 验证 0001 到最新版本"
        ),
    )
    parser.add_argument("--database-url", help="fresh/incremental 模式使用的空数据库 URL")
    args = parser.parse_args()
    if args.mode in {"fresh", "incremental"} and not args.database_url:
        parser.error(f"{args.mode} 模式必须提供 --database-url")
    return args


def main() -> int:
    args = parse_args()
    if args.mode == "all-sqlite":
        validate_all_sqlite()
    elif args.mode == "fresh":
        validate_fresh_database(args.database_url)
    else:
        validate_incremental_database(args.database_url)
    print("FastAPI migrations validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
