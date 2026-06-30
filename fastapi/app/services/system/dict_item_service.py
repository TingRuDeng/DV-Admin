"""
嵌套字典项服务
"""

from app.core.exceptions import NotFound
from app.db.models.system import DictData, DictItems
from app.schemas.base import PageResult
from app.schemas.system import DictItemCreate, DictItemOut, DictItemUpdate
from app.services.system.dict_cache import DictCacheMixin
from app.services.system.dict_item_helpers import extract_item_update_fields
from app.services.system.dict_item_serializers import serialize_dict_item


class DictItemService(DictCacheMixin):
    """基于字典类型路径访问的字典项服务"""

    async def get_item_page(
        self,
        page: int,
        page_size: int,
        dict_id: int | None = None,
        label: str | None = None,
        code: str | None = None,
    ) -> PageResult[DictItemOut]:
        """获取字典项分页列表。"""
        query = DictItems.all()
        query = _apply_item_filters(query, dict_id, label, code)

        total = await query.count()
        items = (
            await query.prefetch_related("dict_data")
            .order_by("dict_data_id", "value")
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return PageResult.create(
            total=total,
            page=page,
            page_size=page_size,
            results=[serialize_dict_item(item, item.dict_data.name) for item in items],
        )

    async def get_items(self, dict_id: int) -> list[DictItemOut]:
        """获取字典项列表。"""
        dict_data = await _require_dict_data(dict_id)
        items = await DictItems.filter(dict_data_id=dict_id).order_by("value").all()
        return [serialize_dict_item(item, dict_data.name) for item in items]

    async def create_item(
        self,
        dict_id: int,
        item_data: DictItemCreate,
    ) -> DictItemOut:
        """创建字典项。"""
        dict_data = await _require_dict_data(dict_id)

        item = await DictItems.create(
            label=item_data.label,
            value=item_data.value,
            status=item_data.status,
            tag_type=item_data.tag_type,
            dict_data_id=dict_id,
        )

        await self._clear_dict_cache(dict_data.dict_code)
        return serialize_dict_item(item, dict_data.name)

    async def update_item(
        self,
        dict_id: int,
        item_id: int,
        item_data: DictItemUpdate,
    ) -> DictItemOut:
        """更新字典项。"""
        item = await DictItems.get_or_none(id=item_id, dict_data_id=dict_id)
        if not item:
            raise NotFound("字典项不存在")

        update_fields = extract_item_update_fields(item_data)
        if update_fields:
            await DictItems.filter(id=item_id).update(**update_fields)
            await item.refresh_from_db()

        dict_data = await DictData.get_or_none(id=dict_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.dict_code)

        return serialize_dict_item(item, dict_data.name if dict_data else None)

    async def delete_item(self, dict_id: int, item_id: int) -> None:
        """删除字典项。"""
        item = await DictItems.get_or_none(id=item_id, dict_data_id=dict_id)
        if not item:
            raise NotFound("字典项不存在")

        await item.delete()

        dict_data = await DictData.get_or_none(id=dict_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.dict_code)


def _apply_item_filters(query, dict_id: int | None, label: str | None, code: str | None):
    """应用字典项分页过滤条件。"""
    if dict_id:
        query = query.filter(dict_data_id=dict_id)
    if label:
        query = query.filter(label__icontains=label)
    if code:
        query = query.filter(dict_data__dict_code=code)
    return query


async def _require_dict_data(dict_id: int) -> DictData:
    """读取字典类型，不存在时抛出统一业务错误。"""
    dict_data = await DictData.get_or_none(id=dict_id)
    if not dict_data:
        raise NotFound("字典类型不存在")
    return dict_data
