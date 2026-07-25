"""Tortoise ORM 迁移元数据契约。"""

from importlib import import_module
from importlib.metadata import version

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
