from scripts.model_contracts import iter_django_fastapi_model_contracts

from app.db.import_django_data import MODEL_MAPPING, map_field_name
from app.db.models.base import BaseModel
from app.db.models.system import NoticeReads
from scripts import model_contracts

FIELD_MODEL_MAPPING = {
    model.__name__: model for model in MODEL_MAPPING.values()
} | {
    "BaseModel": BaseModel,
    "NoticeReads": NoticeReads,
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


def test_dict_data_table_name_matches_django_contract():
    """字典主表应使用 Django 表名，避免双后端继续登记表名差异。"""
    contract = find_model_contract("system.dicts")

    assert contract.fastapi_table == contract.django_table


def test_fastapi_model_alias_targets_match_shared_contracts():
    """FastAPI 字段别名目标必须真实存在于契约声明的模型。"""
    assert hasattr(model_contracts, "iter_fastapi_alias_targets")
    for contract, target_fields in model_contracts.iter_fastapi_alias_targets():
        model = MODEL_MAPPING[contract.django_model]
        for field_name in target_fields:
            assert field_name in model._meta.fields_map


def test_fastapi_relation_through_tables_match_shared_contracts():
    """FastAPI 多对多 through 表和字段必须与共享关联契约保持一致。"""
    assert hasattr(model_contracts, "iter_django_fastapi_relation_contracts")
    for contract in model_contracts.iter_django_fastapi_relation_contracts():
        model = MODEL_MAPPING[contract.django_model]
        relation_field = model._meta.fields_map[contract.fastapi_field]
        assert relation_field.through == contract.fastapi_through_table
        assert relation_field.backward_key == contract.fastapi_backward_key
        assert relation_field.forward_key == contract.fastapi_forward_key


def test_relation_through_table_names_match_django_contracts():
    """多对多关联表应使用 Django 表名，避免双后端继续登记 through 表差异。"""
    contracts = model_contracts.iter_django_fastapi_relation_contracts()

    for contract in contracts:
        assert contract.fastapi_through_table == contract.django_through_table


def test_relation_through_column_names_match_django_contracts():
    """多对多关联表字段应使用 Django 字段名，避免双后端继续登记字段差异。"""
    contracts = model_contracts.iter_django_fastapi_relation_contracts()

    for contract in contracts:
        assert contract.fastapi_backward_key == contract.django_backward_key
        assert contract.fastapi_forward_key == contract.django_forward_key


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


def test_dict_code_length_matches_django_field_contract():
    """FastAPI 字典编码长度必须与 Django 字典编码约束一致。"""
    django_contract = find_constraint("system.dicts", "dict_code")
    fastapi_contract = find_constraint("DictData", "dict_code")

    assert fastapi_contract.max_length == django_contract.max_length


def test_dict_data_field_names_do_not_need_business_aliases():
    """字典主表字段名应与 Django 语义一致，不再登记业务字段别名。"""
    contract = find_model_contract("system.dicts")

    assert "dict_code" not in contract.field_aliases
    assert "remark" not in contract.field_aliases


def test_dict_item_model_does_not_keep_fastapi_only_fields():
    """字典项模型不应继续保留 Django 没有的 FastAPI-only 字段。"""
    contract = find_model_contract("system.dictitems")
    model = MODEL_MAPPING[contract.django_model]

    assert "is_default" not in model._meta.fields_map
    assert "remark" not in model._meta.fields_map


def test_fastapi_model_indexes_match_shared_contracts():
    """FastAPI 模型 Meta.indexes 必须与共享模型索引契约一致。"""
    assert hasattr(model_contracts, "iter_fastapi_model_index_contracts")
    for contract in model_contracts.iter_fastapi_model_index_contracts():
        model = FIELD_MODEL_MAPPING[contract.fastapi_model]
        actual_indexes = tuple(tuple(index) for index in model.Meta.indexes)
        assert actual_indexes == contract.indexes


def test_fastapi_model_unique_together_matches_shared_contracts():
    """FastAPI 模型 Meta.unique_together 必须与共享唯一组合契约一致。"""
    assert hasattr(model_contracts, "iter_fastapi_unique_together_contracts")
    for contract in model_contracts.iter_fastapi_unique_together_contracts():
        model = FIELD_MODEL_MAPPING[contract.fastapi_model]
        assert tuple(model.Meta.unique_together) == contract.fields


def find_constraint(model_name: str, field_name: str):
    """按模型和字段查找共享字段约束契约。"""
    all_contracts = (
        model_contracts.iter_django_field_constraint_contracts()
        + model_contracts.iter_fastapi_field_constraint_contracts()
    )
    for contract in all_contracts:
        contract_model = getattr(contract, "django_model", getattr(contract, "fastapi_model", ""))
        if contract_model == model_name and contract.field_name == field_name:
            return contract
    raise AssertionError(f"缺少字段约束契约：{model_name}.{field_name}")


def find_model_contract(django_model: str):
    """按 Django 模型名查找共享模型契约。"""
    for contract in iter_django_fastapi_model_contracts():
        if contract.django_model == django_model:
            return contract
    raise AssertionError(f"缺少模型契约：{django_model}")
