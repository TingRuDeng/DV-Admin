import importlib
import sys
from pathlib import Path

from drf_admin.apps.system import models as system_models
from drf_admin.apps.system.models_notice import Notices

ROOT = Path(__file__).resolve().parents[3]
DJANGO_MODEL_MAPPING = {
    "system.departments": system_models.Departments,
    "system.permissions": system_models.Permissions,
    "system.roles": system_models.Roles,
    "system.users": system_models.Users,
    "system.dicts": system_models.Dicts,
    "system.dictitems": system_models.DictItems,
    "system.notices": Notices,
}


def test_django_model_tables_match_shared_contracts():
    """Django 模型 db_table 必须与共享模型契约保持一致。"""
    model_contracts = load_model_contracts()
    assert hasattr(model_contracts, "iter_django_model_table_contracts")
    for contract in model_contracts.iter_django_model_table_contracts():
        model = DJANGO_MODEL_MAPPING[contract.django_model]
        assert model._meta.db_table == contract.django_table


def test_django_field_metadata_matches_shared_contracts():
    """Django 关键字段元数据必须与共享模型契约保持一致。"""
    model_contracts = load_model_contracts()
    assert hasattr(model_contracts, "iter_django_field_metadata_contracts")
    for contract in model_contracts.iter_django_field_metadata_contracts():
        model = DJANGO_MODEL_MAPPING[contract.django_model]
        field = model._meta.get_field(contract.field_name)
        assert field.__class__.__name__ == contract.field_type
        assert field.null == contract.null
        if contract.default is not model_contracts.NO_DEFAULT:
            assert field.default == contract.default


def test_django_field_constraints_match_shared_contracts():
    """Django 关键字段约束必须与共享模型契约保持一致。"""
    model_contracts = load_model_contracts()
    assert hasattr(model_contracts, "iter_django_field_constraint_contracts")
    for contract in model_contracts.iter_django_field_constraint_contracts():
        model = DJANGO_MODEL_MAPPING[contract.django_model]
        field = model._meta.get_field(contract.field_name)
        if contract.max_length is not model_contracts.NO_DEFAULT:
            assert field.max_length == contract.max_length
        if contract.unique is not model_contracts.NO_DEFAULT:
            assert field.unique == contract.unique
        if contract.index is not model_contracts.NO_DEFAULT:
            assert field.db_index == contract.index


def load_model_contracts():
    """加载仓库根目录的共享模型契约模块。"""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return importlib.import_module("scripts.model_contracts")
