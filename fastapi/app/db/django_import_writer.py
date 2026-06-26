from typing import Any

from app.db.django_import_config import SELF_REFERENCING_MODELS, map_field_name
from app.db.django_import_errors import DjangoDataImportError
from app.db.django_import_state import FieldAssignContext, ModelImportContext, ModelWriteBuffers
from app.db.models.base import BaseModel


async def import_model_items(
    context: ModelImportContext,
    items: list[dict[str, Any]],
) -> None:
    """导入同一模型的数据，单条失败时携带模型名和主键抛出。"""
    if not items:
        return

    print(f"Importing {len(items)} items for {context.model_name}...")
    for item in items:
        obj, m2m_fields = await import_model_item_with_context(context, item)
        context.tasks.m2m.extend(
            (obj, field, ids) for field, ids in m2m_fields.items() if ids
        )


async def import_model_item_with_context(
    context: ModelImportContext,
    item: dict[str, Any],
) -> tuple[BaseModel, dict[str, list[int]]]:
    """包装单条导入错误，保证错误消息携带模型名和主键。"""
    try:
        return await import_model_item(context, item)
    except Exception as exc:
        if isinstance(exc, DjangoDataImportError):
            raise
        pk = item.get("pk")
        message = f"Error importing {context.model_name} id={pk}: {exc}"
        raise DjangoDataImportError(message) from exc


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
    if should_delay_self_reference(context.model_name, field, value):
        context.tasks.fk.append((context.model_class, context.pk, field, value))
        value = None
    key = f"{field}_id"
    context.buffers.create[key] = value
    context.buffers.update[key] = value


def should_delay_self_reference(model_name: str, field: str, value: Any) -> bool:
    """判断自引用外键是否需要等全部主记录导入后再回填。"""
    return model_name in SELF_REFERENCING_MODELS and field == "parent" and value is not None


def normalize_relation_ids(value: Any) -> list[int]:
    """规范化 M2M 主键列表。"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return list(value)
