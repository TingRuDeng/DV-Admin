import json
import sys
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path
from typing import Any

# 添加路径以便脚本直接运行时仍能导入 app 包。
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent
sys.path.append(str(project_root / "fastapi"))

from tortoise import Tortoise, run_async

from app.core.config import settings
from app.db.models.base import BaseModel
from app.db.models.oauth import Users
from app.db.models.system import Departments, DictData, DictItems, Permissions, Roles


class DjangoDataImportError(RuntimeError):
    """Django fixture 导入失败，必须中断流程并暴露根因。"""


@dataclass
class ImportTasks:
    """导入过程中延后处理的关系任务。"""

    m2m: list[tuple[BaseModel, str, list[int]]] = dataclass_field(default_factory=list)
    fk: list[tuple[type[BaseModel], int, str, int]] = dataclass_field(default_factory=list)


@dataclass(frozen=True)
class ModelImportContext:
    """单个 Django 模型导入所需的上下文。"""

    model_name: str
    model_class: type[BaseModel]
    tasks: ImportTasks


@dataclass
class ModelWriteBuffers:
    """单条数据转换后的写入参数。"""

    create: dict[str, Any]
    update: dict[str, Any] = dataclass_field(default_factory=dict)
    m2m: dict[str, list[int]] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class FieldAssignContext:
    """字段转换时需要共享的模型和主键信息。"""

    model_name: str
    model_class: type[BaseModel]
    pk: int
    buffers: ModelWriteBuffers
    tasks: ImportTasks


# 映射模型名称到类
MODEL_MAPPING: dict[str, type[BaseModel]] = {
    "system.departments": Departments,
    "system.permissions": Permissions,
    "system.roles": Roles,
    "system.users": Users,
    "system.dicts": DictData,
    "system.dictitems": DictItems,
}

# 字段名映射
FIELD_MAPPING = {
    "create_time": "created_at",
    "update_time": "updated_at",
    "dict": "dict_data",  # DictItems 的外键: Django(dict) -> FastAPI(dict_data)
    "dict_code": "code",  # DictData: Django(dict_code) -> FastAPI(code)
    "keepAlive": "keep_alive",  # Permissions: Django camel 字段 -> FastAPI snake 字段
    "alwaysShow": "always_show",  # Permissions: Django camel 字段 -> FastAPI snake 字段
}

IMPORT_ORDER = (
    "system.departments",
    "system.permissions",
    "system.dicts",
    "system.dictitems",  # 依赖 dicts
    "system.roles",  # 依赖 permissions (M2M)
    "system.users",  # 依赖 departments, roles (M2M)
)
SELF_REFERENCING_MODELS = {"system.departments", "system.permissions"}


async def init():
    """初始化数据库连接"""
    await Tortoise.init(config=settings.tortoise_orm_config)
    print("Database connection initialized.")


async def import_data():
    """导入 Django fixture；任何关键失败都必须中断。"""
    data = load_fixture_rows(fixture_file_path())
    tasks = ImportTasks()
    grouped_data = group_fixture_rows(data)

    for model_name in IMPORT_ORDER:
        context = ModelImportContext(model_name, MODEL_MAPPING[model_name], tasks)
        await import_model_items(context, grouped_data[model_name])

    await update_self_references(tasks.fk)
    await process_m2m_tasks(tasks.m2m)
    print("Import completed successfully!")


def fixture_file_path() -> Path:
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


async def import_model_items(
    context: ModelImportContext,
    items: list[dict[str, Any]],
) -> None:
    """导入同一模型的数据，单条失败时携带模型名和主键抛出。"""
    if not items:
        return

    print(f"Importing {len(items)} items for {context.model_name}...")
    for item in items:
        try:
            obj, m2m_fields = await import_model_item(context, item)
        except Exception as exc:
            if isinstance(exc, DjangoDataImportError):
                raise
            pk = item.get("pk")
            raise DjangoDataImportError(
                f"Error importing {context.model_name} id={pk}: {exc}"
            ) from exc
        context.tasks.m2m.extend((obj, field, ids) for field, ids in m2m_fields.items() if ids)


async def import_model_item(
    context: ModelImportContext,
    item: dict[str, Any],
) -> tuple[BaseModel, dict[str, list[int]]]:
    """创建或更新单条 fixture 数据，并返回待处理的 M2M 关系。"""
    pk = item["pk"]
    buffers = build_model_kwargs(
        FieldAssignContext(
            context.model_name,
            context.model_class,
            pk,
            ModelWriteBuffers(create={"id": pk}),
            context.tasks,
        ),
        item["fields"],
    )

    if await context.model_class.filter(id=pk).exists():
        if buffers.update:
            await context.model_class.filter(id=pk).update(**buffers.update)
        return await context.model_class.get(id=pk), buffers.m2m
    return await context.model_class.create(**buffers.create), buffers.m2m


def build_model_kwargs(
    context: FieldAssignContext,
    fields_data: dict[str, Any],
) -> ModelWriteBuffers:
    """把 Django 字段转换为 FastAPI 模型可写参数。"""
    for field, value in fields_data.items():
        mapped_field = map_field_name(context.model_name, field)
        if mapped_field in context.model_class._meta.m2m_fields:
            context.buffers.m2m[mapped_field] = normalize_relation_ids(value)
            continue
        if mapped_field in context.model_class._meta.fields_map:
            assign_model_field(context, mapped_field, value)
    return context.buffers


def assign_model_field(
    context: FieldAssignContext,
    field: str,
    value: Any,
) -> None:
    """根据字段类型写入 create/update 参数。"""
    if field in context.model_class._meta.fk_fields:
        assign_fk_field(context, field, value)
        return
    if context.model_name == "system.users" and field == "is_active":
        value = 1 if value else 0
    context.buffers.create[field] = value
    context.buffers.update[field] = value


def assign_fk_field(
    context: FieldAssignContext,
    field: str,
    value: Any,
) -> None:
    """处理普通外键和自关联外键。"""
    if context.model_name in SELF_REFERENCING_MODELS and field == "parent" and value is not None:
        context.tasks.fk.append((context.model_class, context.pk, field, value))
        value = None
    key = f"{field}_id"
    context.buffers.create[key] = value
    context.buffers.update[key] = value


def map_field_name(model_name: str, field: str) -> str:
    """把 Django 字段名映射到 FastAPI 模型字段名。"""
    if model_name == "system.dicts" and field == "remark":
        return "desc"
    return FIELD_MAPPING.get(field, field)


def normalize_relation_ids(value: Any) -> list[int]:
    """规范化 M2M 主键列表。"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return list(value)


async def update_self_references(fk_updates: list[tuple[type[BaseModel], int, str, int]]) -> None:
    """导入完成后补自关联外键，任何失败都中断。"""
    print(f"Updating {len(fk_updates)} self-referencing foreign keys...")
    for ModelClass, pk, field, fk_id in fk_updates:
        try:
            await ModelClass.filter(id=pk).update(**{f"{field}_id": fk_id})
        except Exception as exc:
            raise DjangoDataImportError(
                f"Error updating FK for {ModelClass.__name__} id={pk}: {exc}"
            ) from exc


async def process_m2m_tasks(m2m_tasks: list[tuple[BaseModel, str, list[int]]]) -> None:
    """处理 M2M 关系，目标缺失时中断，避免生成残缺关系。"""
    print(f"Processing {len(m2m_tasks)} M2M relationships...")
    for obj, field, ids in m2m_tasks:
        try:
            relation = getattr(obj, field)
            related_objs = await relation.remote_model.filter(id__in=ids).all()
            assert_related_ids_exist(ids, related_objs, obj, field)
            await relation.clear()
            await relation.add(*related_objs)
        except Exception as exc:
            if isinstance(exc, DjangoDataImportError):
                raise
            raise DjangoDataImportError(f"Error processing M2M for {obj} field={field}: {exc}") from exc


def assert_related_ids_exist(ids: list[int], related_objs: list[BaseModel], obj: BaseModel, field: str) -> None:
    """确认 M2M 目标全部存在，禁止静默丢关系。"""
    found_ids = {related.id for related in related_objs}
    missing_ids = sorted(set(ids) - found_ids)
    if missing_ids:
        raise DjangoDataImportError(
            f"Error processing M2M for {obj} field={field}: missing related ids {missing_ids}"
        )


async def main():
    await init()
    await import_data()
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(main())
