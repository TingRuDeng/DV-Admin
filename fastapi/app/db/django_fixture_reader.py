import json
from pathlib import Path
from typing import Any

from app.db.django_import_config import MODEL_MAPPING
from app.db.django_import_errors import DjangoDataImportError


def fixture_file_path(project_root: str | Path) -> Path:
    """返回当前项目约定的 Django fixture 路径。"""
    return Path(project_root) / "backend" / "init_data.json"


def load_fixture_rows(json_path: Path) -> list[dict[str, Any]]:
    """读取 Django fixture，文件缺失或格式错误时立即失败。"""
    if not json_path.exists():
        raise DjangoDataImportError(f"File not found: {json_path}")

    print(f"Reading data from {json_path}...")
    with json_path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise DjangoDataImportError("Fixture root must be a list")
    return data


def group_fixture_rows(data: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """按 Django model 名称分组，未知模型保持跳过兼容。"""
    grouped_data: dict[str, list[dict[str, Any]]] = {key: [] for key in MODEL_MAPPING}
    for item in data:
        model_name = item.get("model")
        if model_name in grouped_data:
            grouped_data[model_name].append(item)
    return grouped_data
