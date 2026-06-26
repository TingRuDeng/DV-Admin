from app.db.django_import_errors import DjangoDataImportError
from app.db.models.base import BaseModel


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
        await process_m2m_task(obj, field, ids)


async def process_m2m_task(obj: BaseModel, field: str, ids: list[int]) -> None:
    """处理单个 M2M 字段，失败时保留对象和字段信息。"""
    try:
        relation = getattr(obj, field)
        related_objs = await relation.remote_model.filter(id__in=ids).all()
        assert_related_ids_exist(ids, related_objs, obj, field)
        await relation.clear()
        await relation.add(*related_objs)
    except Exception as exc:
        if isinstance(exc, DjangoDataImportError):
            raise
        message = f"Error processing M2M for {obj} field={field}: {exc}"
        raise DjangoDataImportError(message) from exc


def assert_related_ids_exist(
    ids: list[int],
    related_objs: list[BaseModel],
    obj: BaseModel,
    field: str,
) -> None:
    """确认 M2M 目标全部存在，禁止静默丢关系。"""
    found_ids = {related.id for related in related_objs}
    missing_ids = sorted(set(ids) - found_ids)
    if missing_ids:
        raise DjangoDataImportError(
            f"Error processing M2M for {obj} field={field}: missing related ids {missing_ids}"
        )
