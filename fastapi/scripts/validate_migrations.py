#!/usr/bin/env python3
"""验证 Tortoise ORM 迁移基线、既有库接管和模型漂移。"""

from __future__ import annotations

import argparse
import asyncio
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = PROJECT_ROOT / "app" / "db" / "migrations"
MIGRATION_CONFIG = "app.db.migration_config.TORTOISE_ORM"
TEST_SECRET_KEY = "migration-validation-key-at-least-sixty-four-characters-long-123456"
BASELINE_MIGRATION = "0001_initial"
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


def assert_baseline_history(database_url: str) -> None:
    history = run_tortoise(database_url, "history", "models")
    if BASELINE_MIGRATION not in history:
        raise RuntimeError("迁移历史缺少 models.0001_initial")


def validate_fresh_database(database_url: str, sqlite_path: Path | None = None) -> None:
    run_tortoise(database_url, "migrate")
    assert_baseline_history(database_url)
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
        assert_baseline_history(database_url)

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
    validate_existing_sqlite_baseline()
    validate_model_drift()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("all-sqlite", "fresh"),
        help="all-sqlite 验证空库、既有库和漂移；fresh 验证指定空库",
    )
    parser.add_argument("--database-url", help="fresh 模式使用的空数据库 URL")
    args = parser.parse_args()
    if args.mode == "fresh" and not args.database_url:
        parser.error("fresh 模式必须提供 --database-url")
    return args


def main() -> int:
    args = parse_args()
    if args.mode == "all-sqlite":
        validate_all_sqlite()
    else:
        validate_fresh_database(args.database_url)
    print("FastAPI migrations validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
