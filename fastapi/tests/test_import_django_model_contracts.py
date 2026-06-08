from scripts.model_contracts import iter_django_fastapi_model_contracts

from app.db.import_django_data import MODEL_MAPPING, map_field_name


def test_import_mapping_matches_shared_model_contracts():
    """导入脚本必须覆盖共享模型契约声明的模型和字段映射。"""
    contracts = iter_django_fastapi_model_contracts()
    for contract in contracts:
        assert contract.django_model in MODEL_MAPPING
        assert MODEL_MAPPING[contract.django_model].__name__ == contract.fastapi_model
        for django_field, fastapi_field in contract.field_aliases.items():
            assert map_field_name(contract.django_model, django_field) == fastapi_field
