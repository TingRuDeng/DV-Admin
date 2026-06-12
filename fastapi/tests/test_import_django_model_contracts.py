from scripts.model_contracts import iter_django_fastapi_model_contracts

from app.db.import_django_data import MODEL_MAPPING, map_field_name
from app.db.models.base import BaseModel
from scripts import model_contracts

FIELD_MODEL_MAPPING = {
    model.__name__: model for model in MODEL_MAPPING.values()
} | {
    "BaseModel": BaseModel,
}


def test_import_mapping_matches_shared_model_contracts():
    """导入脚本必须覆盖共享模型契约声明的模型和字段映射。"""
    contracts = iter_django_fastapi_model_contracts()
    for contract in contracts:
        assert contract.django_model in MODEL_MAPPING
        assert MODEL_MAPPING[contract.django_model].__name__ == contract.fastapi_model
        for django_field, fastapi_field in contract.field_aliases.items():
            assert map_field_name(contract.django_model, django_field) == fastapi_field


def test_fastapi_model_tables_match_shared_contracts():
    """FastAPI 模型表名必须与共享模型契约保持一致。"""
    contracts = iter_django_fastapi_model_contracts()
    for contract in contracts:
        model = MODEL_MAPPING[contract.django_model]
        assert model.Meta.table == contract.fastapi_table


def test_fastapi_model_alias_targets_match_shared_contracts():
    """FastAPI 字段别名目标必须真实存在于契约声明的模型。"""
    assert hasattr(model_contracts, "iter_fastapi_alias_targets")
    for contract, target_fields in model_contracts.iter_fastapi_alias_targets():
        model = MODEL_MAPPING[contract.django_model]
        for field_name in target_fields:
            assert field_name in model._meta.fields_map


def test_fastapi_relation_through_tables_match_shared_contracts():
    """FastAPI 多对多 through 表必须与共享关联契约保持一致。"""
    assert hasattr(model_contracts, "iter_django_fastapi_relation_contracts")
    for contract in model_contracts.iter_django_fastapi_relation_contracts():
        model = MODEL_MAPPING[contract.django_model]
        relation_field = model._meta.fields_map[contract.fastapi_field]
        assert relation_field.through == contract.fastapi_through_table


def test_fastapi_field_metadata_matches_shared_contracts():
    """FastAPI 字段类型、null 和 default 必须与共享字段元数据契约一致。"""
    assert hasattr(model_contracts, "iter_fastapi_field_metadata_contracts")
    for contract in model_contracts.iter_fastapi_field_metadata_contracts():
        model = FIELD_MODEL_MAPPING[contract.fastapi_model]
        field = model._meta.fields_map[contract.field_name]
        assert type(field).__name__ == contract.field_type
        assert field.null == contract.null
        if contract.default is not model_contracts.NO_DEFAULT:
            assert field.default == contract.default


def test_fastapi_field_constraints_match_shared_contracts():
    """FastAPI 字段长度、唯一性和索引必须与共享字段约束契约一致。"""
    assert hasattr(model_contracts, "iter_fastapi_field_constraint_contracts")
    for contract in model_contracts.iter_fastapi_field_constraint_contracts():
        model = FIELD_MODEL_MAPPING[contract.fastapi_model]
        field = model._meta.fields_map[contract.field_name]
        if contract.max_length is not model_contracts.NO_DEFAULT:
            assert field.max_length == contract.max_length
        if contract.unique is not model_contracts.NO_DEFAULT:
            assert field.unique == contract.unique
        if contract.index is not model_contracts.NO_DEFAULT:
            assert field.index == contract.index
