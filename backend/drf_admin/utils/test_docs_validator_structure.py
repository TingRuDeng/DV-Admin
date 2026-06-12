from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_contract_entrypoint_validation_is_split_from_docs_cli():
    """文档契约入口校验必须独立维护，避免 validate_docs.py 继续膨胀。"""
    entrypoint = read_text("scripts/validate_docs.py")
    assert "from docs_contract_validation import validate_contract_entrypoints" in entrypoint
    assert "CONTRACT_REQUIRED_FILES =" not in entrypoint
    assert "PNPM_ACTION_SETUP_REQUIRED =" not in entrypoint
    assert "def validate_contract_entrypoints(" not in entrypoint
    assert (ROOT / "scripts/docs_contract_validation.py").exists()


def read_text(relative_path: str) -> str:
    """读取仓库内文本文件。"""
    return (ROOT / relative_path).read_text(encoding="utf-8")
