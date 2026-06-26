"""
Django 数据导入映射测试

覆盖模型映射、字段映射和导入顺序契约。
"""

import pytest

from app.db.models.oauth import Users
from app.db.models.system import Departments, DictData, DictItems, Permissions, Roles


@pytest.mark.asyncio
async def test_model_mapping_exists(db):
    """模型映射必须覆盖 Django 初始化数据中的核心模型。"""
    from app.db.import_django_data import MODEL_MAPPING

    assert "system.departments" in MODEL_MAPPING
    assert "system.permissions" in MODEL_MAPPING
    assert "system.roles" in MODEL_MAPPING
    assert "system.users" in MODEL_MAPPING
    assert "system.dicts" in MODEL_MAPPING
    assert "system.dictitems" in MODEL_MAPPING

    assert MODEL_MAPPING["system.departments"] == Departments
    assert MODEL_MAPPING["system.permissions"] == Permissions
    assert MODEL_MAPPING["system.roles"] == Roles
    assert MODEL_MAPPING["system.users"] == Users
    assert MODEL_MAPPING["system.dicts"] == DictData
    assert MODEL_MAPPING["system.dictitems"] == DictItems


@pytest.mark.asyncio
async def test_field_mapping_exists(db):
    """字段映射必须保持 Django 到 FastAPI 的字段名转换契约。"""
    from app.db.import_django_data import FIELD_MAPPING, map_field_name

    assert FIELD_MAPPING["create_time"] == "created_at"
    assert FIELD_MAPPING["update_time"] == "updated_at"
    assert FIELD_MAPPING["dict"] == "dict_data"
    assert "dict_code" not in FIELD_MAPPING
    assert map_field_name("system.dicts", "dict_code") == "dict_code"
    assert map_field_name("system.dicts", "remark") == "remark"


@pytest.mark.asyncio
async def test_import_order(db):
    """导入顺序中的每个模型都必须存在映射。"""
    from app.db.import_django_data import MODEL_MAPPING

    import_order = [
        "system.departments",
        "system.permissions",
        "system.dicts",
        "system.dictitems",
        "system.roles",
        "system.users",
    ]

    for model_name in import_order:
        assert model_name in MODEL_MAPPING
