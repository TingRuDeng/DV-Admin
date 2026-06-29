"""
字典类型服务
"""

from app.core.exceptions import NotFound, ValidationError
from app.db.models.system import DictData
from app.schemas.base import PageResult
from app.schemas.system import DictDataCreate, DictDataOut, DictDataUpdate, DictWithItems
from app.services.system.dict_cache import DictCacheMixin
from app.services.system.dict_item_serializers import serialize_dict_item


def serialize_dict_data(dict_data: DictData) -> DictDataOut:
    """将字典类型 ORM 对象转换为响应模型。"""
    return DictDataOut(
        id=dict_data.id,
        name=dict_data.name,
        dict_code=dict_data.dict_code,
        status=dict_data.status,
        remark=dict_data.remark,
        created_at=dict_data.created_at,
        updated_at=dict_data.updated_at,
    )


class DictTypeService(DictCacheMixin):
    """字典类型 CRUD 服务"""

    async def get_dict_page(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> PageResult[DictDataOut]:
        """获取字典类型分页列表。"""
        query = DictData.all()

        if search:
            query = query.filter(name__icontains=search)

        total = await query.count()
        dicts = await query.offset((page - 1) * page_size).limit(page_size).all()
        dict_list = [serialize_dict_data(dict_data) for dict_data in dicts]

        return PageResult.create(
            total=total,
            page=page,
            page_size=page_size,
            results=dict_list,
        )

    async def get_dict(self, dict_id: int) -> DictWithItems:
        """获取字典类型详情，包含字典项。"""
        dict_data = await DictData.get_or_none(id=dict_id)
        if not dict_data:
            raise NotFound("字典类型不存在")

        await dict_data.fetch_related("items")
        items = await dict_data.items.all()

        return DictWithItems(
            **serialize_dict_data(dict_data).model_dump(),
            items=[serialize_dict_item(item, dict_data.name) for item in items],
        )

    async def create_dict(self, dict_data: DictDataCreate) -> DictDataOut:
        """创建字典类型。"""
        existing = await DictData.get_or_none(dict_code=dict_data.dict_code)
        if existing:
            raise ValidationError("字典编码已存在")

        created = await DictData.create(
            name=dict_data.name,
            dict_code=dict_data.dict_code,
            status=dict_data.status,
            remark=dict_data.remark,
        )
        return serialize_dict_data(created)

    async def update_dict(
        self,
        dict_id: int,
        dict_data: DictDataUpdate,
    ) -> DictDataOut:
        """更新字典类型。"""
        existing = await DictData.get_or_none(id=dict_id)
        if not existing:
            raise NotFound("字典类型不存在")

        old_code = existing.dict_code
        update_fields = _extract_update_fields(dict_data)

        if update_fields:
            await DictData.filter(id=dict_id).update(**update_fields)
            await existing.refresh_from_db()

        await self._clear_dict_cache(old_code)
        new_code = update_fields.get("dict_code")
        if isinstance(new_code, str) and new_code != old_code:
            await self._clear_dict_cache(new_code)

        return serialize_dict_data(existing)

    async def delete_dict(self, dict_id: int) -> None:
        """删除字典类型。"""
        dict_data = await DictData.get_or_none(id=dict_id)
        if not dict_data:
            raise NotFound("字典类型不存在")

        code = dict_data.dict_code
        await dict_data.delete()
        await self._clear_dict_cache(code)

    async def batch_delete_dicts(self, ids: list[int]) -> None:
        """批量删除字典类型。"""
        dicts = await DictData.filter(id__in=ids).all()
        codes = [dict_data.dict_code for dict_data in dicts]

        await DictData.filter(id__in=ids).delete()

        for code in codes:
            await self._clear_dict_cache(code)


def _extract_update_fields(dict_data: DictDataUpdate) -> dict[str, object]:
    """提取非空更新字段，保持原服务忽略 None 的行为。"""
    return {
        field: value
        for field, value in dict_data.model_dump(exclude_unset=True).items()
        if value is not None
    }
