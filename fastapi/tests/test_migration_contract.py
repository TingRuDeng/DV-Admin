"""Tortoise ORM 迁移元数据契约。"""

from importlib import import_module
from importlib.metadata import version
from pathlib import Path

from tortoise.indexes import Index

from app.core.config import Settings
from app.db.migration_config import TORTOISE_ORM
from app.db.models.oauth import Users
from app.db.models.system import (
    Departments,
    DictData,
    DictItems,
    NoticeReads,
    Notices,
    OperationLog,
    Permissions,
    Roles,
)

Migration = import_module("app.db.migrations.0001_initial").Migration
RequestIdMigration = import_module(
    "app.db.migrations.0002_auto_20260725_2230"
).Migration

MODELS = (
    Departments,
    DictData,
    DictItems,
    NoticeReads,
    Notices,
    OperationLog,
    Permissions,
    Roles,
    Users,
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_tortoise_version_is_pinned_for_migration_compatibility():
    assert version("tortoise-orm") == "1.1.7"


def test_migration_config_uses_committed_package():
    assert TORTOISE_ORM["apps"]["models"]["migrations"] == "app.db.migrations"


def test_mysql_url_is_expanded_for_tortoise_client(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "mysql://migration-user:migration-password@127.0.0.1:3306/migration-db",
    )
    settings = Settings()
    credentials = settings.tortoise_orm_config["connections"]["default"]["credentials"]

    assert credentials["user"] == "migration-user"
    assert credentials["password"] == "migration-password"
    assert credentials["host"] == "127.0.0.1"
    assert credentials["port"] == 3306
    assert credentials["database"] == "migration-db"


def test_initial_migration_is_declared_as_baseline():
    assert Migration.initial is True
    assert Migration.dependencies == []


def test_request_id_migration_keeps_database_default_for_existing_rows():
    add_field = RequestIdMigration.operations[0]

    assert RequestIdMigration.dependencies == [("models", "0001_initial")]
    assert add_field.field.default == ""
    assert add_field.field.db_default == ""


def test_compose_waits_for_single_migration_service_before_fastapi_start():
    root_compose = (REPOSITORY_ROOT / "compose.yaml").read_text()
    docker_compose = (
        REPOSITORY_ROOT / "fastapi" / "docker" / "docker-compose.yml"
    ).read_text()

    assert "fastapi-migrate:" in root_compose
    assert "condition: service_completed_successfully" in root_compose
    assert "migrate:" in docker_compose
    assert "condition: service_completed_successfully" in docker_compose


def test_production_compose_requires_secrets_and_uses_immutable_image():
    docker_compose = (
        REPOSITORY_ROOT / "fastapi" / "docker" / "docker-compose.yml"
    ).read_text()

    assert "${DATABASE_URL:?" in docker_compose
    assert "${SECRET_KEY:?" in docker_compose
    assert "${DEFAULT_PASSWORD:?" in docker_compose
    assert "${MYSQL_ROOT_PASSWORD:?" in docker_compose
    assert "your-secret-key-here" not in docker_compose
    assert "--reload" not in docker_compose
    assert "../app:/app/app" not in docker_compose


def test_model_indexes_are_serializable_by_migration_writer():
    for model in MODELS:
        assert all(isinstance(index, Index) for index in model.Meta.indexes)


def test_field_descriptions_do_not_break_sqlite_atomic_migrations():
    for model in MODELS:
        descriptions = (
            field.description or ""
            for field in model._meta.fields_map.values()
            if hasattr(field, "description")
        )
        assert all(";" not in description for description in descriptions)
