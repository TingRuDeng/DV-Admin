from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_model_contract_test_validation_is_split_from_cli_entrypoint():
    """模型契约主入口只负责编排，测试片段校验必须独立维护。"""
    entrypoint = read_text("scripts/validate_model_contracts.py")
    assert "from model_test_validation import validate_tests" in entrypoint
    assert "fastapi_required =" not in entrypoint
    assert "django_required =" not in entrypoint
    assert (ROOT / "scripts/model_test_validation.py").exists()


def test_model_field_constraints_are_split_from_metadata_contracts():
    """字段约束契约必须独立维护，避免字段契约入口继续膨胀。"""
    field_contracts = read_text("scripts/model_field_contracts.py")
    assert "from scripts.model_field_constraint_contracts import" in field_contracts
    assert "FASTAPI_FIELD_CONSTRAINT_CONTRACTS =" not in field_contracts
    assert "DJANGO_FIELD_CONSTRAINT_CONTRACTS =" not in field_contracts
    assert (ROOT / "scripts/model_field_constraint_contracts.py").exists()


def test_fastapi_model_validation_is_split_from_cli_entrypoint():
    """FastAPI 模型校验必须独立维护，避免模型契约 CLI 继续膨胀。"""
    entrypoint = read_text("scripts/validate_model_contracts.py")
    assert "from model_fastapi_validation import" in entrypoint
    assert "def validate_fastapi_model_tables(" not in entrypoint
    assert "def validate_fastapi_field_metadata(" not in entrypoint
    assert "def load_field_metadata_contracts(" not in entrypoint
    assert (ROOT / "scripts/model_fastapi_validation.py").exists()


def read_text(relative_path: str) -> str:
    """读取仓库内文本文件。"""
    return (ROOT / relative_path).read_text(encoding="utf-8")
