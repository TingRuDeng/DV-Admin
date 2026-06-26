import sys
from pathlib import Path

# 添加路径以便脚本直接运行时仍能导入 app 包。
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent
sys.path.append(str(project_root / "fastapi"))

from tortoise import Tortoise, run_async

from app.core.config import settings
from app.db.django_fixture_reader import fixture_file_path, group_fixture_rows, load_fixture_rows
from app.db.django_import_config import FIELD_MAPPING, IMPORT_ORDER, MODEL_MAPPING, map_field_name
from app.db.django_import_errors import DjangoDataImportError
from app.db.django_import_relations import process_m2m_tasks, update_self_references
from app.db.django_import_state import ImportTasks, ModelImportContext
from app.db.django_import_writer import import_model_items

__all__ = [
    "DjangoDataImportError",
    "FIELD_MAPPING",
    "MODEL_MAPPING",
    "import_data",
    "init",
    "main",
    "map_field_name",
]


async def init():
    """初始化数据库连接"""
    await Tortoise.init(config=settings.tortoise_orm_config)
    print("Database connection initialized.")


async def import_data():
    """导入 Django fixture；任何关键失败都必须中断。"""
    data = load_fixture_rows(fixture_file_path(project_root))
    tasks = ImportTasks()
    grouped_data = group_fixture_rows(data)

    for model_name in IMPORT_ORDER:
        context = ModelImportContext(model_name, MODEL_MAPPING[model_name], tasks)
        await import_model_items(context, grouped_data[model_name])

    await update_self_references(tasks.fk)
    await process_m2m_tasks(tasks.m2m)
    print("Import completed successfully!")


async def main():
    await init()
    await import_data()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(main())
