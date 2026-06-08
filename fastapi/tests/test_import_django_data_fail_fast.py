import json

import pytest

from app.db import import_django_data


def write_fixture(tmp_path, rows: list[dict]) -> None:
    """写入最小 Django fixture，模拟真实导入输入。"""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir()
    (backend_dir / "init_data.json").write_text(json.dumps(rows), encoding="utf-8")


@pytest.mark.asyncio
async def test_import_data_raises_when_fixture_missing(tmp_path, monkeypatch):
    """缺少 fixture 时必须失败，避免误报导入成功。"""
    monkeypatch.setattr(import_django_data, "project_root", str(tmp_path))

    with pytest.raises(import_django_data.DjangoDataImportError, match="File not found"):
        await import_django_data.import_data()


@pytest.mark.asyncio
async def test_import_data_raises_on_invalid_model_item(db, tmp_path, monkeypatch):
    """单条数据导入失败时必须暴露模型和主键。"""
    monkeypatch.setattr(import_django_data, "project_root", str(tmp_path))
    write_fixture(
        tmp_path,
        [
            {
                "model": "system.departments",
                "pk": 1001,
                "fields": {
                    "sort": 1,
                    "status": 1,
                },
            }
        ],
    )

    with pytest.raises(import_django_data.DjangoDataImportError, match="system.departments id=1001"):
        await import_django_data.import_data()


@pytest.mark.asyncio
async def test_import_data_raises_when_m2m_target_missing(db, tmp_path, monkeypatch):
    """M2M 目标缺失时必须失败，避免静默生成残缺关系。"""
    monkeypatch.setattr(import_django_data, "project_root", str(tmp_path))
    write_fixture(
        tmp_path,
        [
            {
                "model": "system.roles",
                "pk": 1002,
                "fields": {
                    "name": "测试角色",
                    "code": "test_role",
                    "status": 1,
                    "permissions": [9999],
                },
            }
        ],
    )

    with pytest.raises(import_django_data.DjangoDataImportError, match="missing related ids"):
        await import_django_data.import_data()
