from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_model_contract_test_validation_is_split_from_cli_entrypoint():
    """模型契约主入口只负责编排，测试片段校验必须独立维护。"""
    entrypoint = read_text("scripts/validate_model_contracts.py")
    assert "from model_test_validation import validate_tests" in entrypoint
    assert "fastapi_required =" not in entrypoint
    assert "django_required =" not in entrypoint
    assert (ROOT / "scripts/model_test_validation.py").exists()


def read_text(relative_path: str) -> str:
    """读取仓库内文本文件。"""
    return (ROOT / relative_path).read_text(encoding="utf-8")
