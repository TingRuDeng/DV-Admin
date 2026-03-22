# -*- coding: utf-8 -*-
"""
数据库模型模块

包含所有 Tortoise ORM 模型定义。
"""

from app.db.models.oauth import Users
from app.db.models.system import (
    Departments,
    DictData,
    DictItems,
    Permissions,
    Roles,
)

__all__ = [
    "Users",
    "Roles",
    "Permissions",
    "Departments",
    "DictData",
    "DictItems",
]
