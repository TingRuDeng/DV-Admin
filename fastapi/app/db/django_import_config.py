from app.db.models.base import BaseModel
from app.db.models.oauth import Users
from app.db.models.system import (
    Departments,
    DictData,
    DictItems,
    Notices,
    Permissions,
    Roles,
)

# 映射模型名称到类，导入入口和契约测试都依赖该公开目录。
MODEL_MAPPING: dict[str, type[BaseModel]] = {
    "system.departments": Departments,
    "system.permissions": Permissions,
    "system.roles": Roles,
    "system.users": Users,
    "system.dicts": DictData,
    "system.dictitems": DictItems,
    "system.notices": Notices,
}

# 字段名映射只登记真实跨实现差异，业务同名字段不做额外别名。
FIELD_MAPPING = {
    "create_time": "created_at",
    "update_time": "updated_at",
    "dict": "dict_data",
    "keepAlive": "keep_alive",
    "alwaysShow": "always_show",
}

IMPORT_ORDER = (
    "system.departments",
    "system.permissions",
    "system.dicts",
    "system.dictitems",
    "system.notices",
    "system.roles",
    "system.users",
)

SELF_REFERENCING_MODELS = {"system.departments", "system.permissions"}


def map_field_name(model_name: str, field: str) -> str:
    """把 Django 字段名映射到 FastAPI 模型字段名。"""
    return FIELD_MAPPING.get(field, field)
