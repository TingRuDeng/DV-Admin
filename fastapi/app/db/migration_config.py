"""Tortoise ORM 内建迁移使用的独立配置。"""

from copy import deepcopy

from app.core.config import settings

TORTOISE_ORM = deepcopy(settings.tortoise_orm_config)
TORTOISE_ORM["apps"]["models"]["migrations"] = "app.db.migrations"
