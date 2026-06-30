"""
扁平字典项服务
"""

from app.core.cache import CacheKeys, cache_service
from app.core.exceptions import NotFound
from app.db.models.system import DictData, DictItems
from app.schemas.system import DictItemCreate, DictItemOut, DictItemUpdate
from app.services.system.dict_cache import DictCacheMixin
from app.services.system.dict_item_helpers import extract_item_update_fields
from app.services.system.dict_item_serializers import serialize_dict_item


class DictItemFlatService(DictCacheMixin):
    """直接通过字典项 ID 访问的服务"""

    async def create_item_flat(self, item_data: DictItemCreate) -> DictItemOut:
        """创建字典项。"""
        dict_data = await _require_dict_data(item_data.dict_data_id)
        item = await DictItems.create(
            label=item_data.label,
            value=item_data.value,
            status=item_data.status,
            tag_type=item_data.tag_type,
            dict_data_id=item_data.dict_data_id,
        )

        await self._clear_dict_cache(dict_data.dict_code)
        return serialize_dict_item(item, dict_data.name)

    async def update_item_flat(
        self,
        item_id: int,
        item_data: DictItemUpdate,
    ) -> DictItemOut:
        """更新字典项。"""
        item = await DictItems.get_or_none(id=item_id)
        if not item:
            raise NotFound("字典项不存在")

        update_fields = extract_item_update_fields(item_data)
        if update_fields:
            await DictItems.filter(id=item_id).update(**update_fields)
            await item.refresh_from_db()

        dict_data = await DictData.get_or_none(id=item.dict_data_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.dict_code)

        return serialize_dict_item(item, dict_data.name if dict_data else None)

    async def delete_item_flat(self, item_id: int) -> None:
        """删除字典项。"""
        item = await DictItems.get_or_none(id=item_id)
        if not item:
            raise NotFound("字典项不存在")

        dict_data_id = item.dict_data_id
        await item.delete()

        dict_data = await DictData.get_or_none(id=dict_data_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.dict_code)

    async def batch_delete_items_flat(self, ids: list[int]) -> None:
        """批量删除字典项。"""
        items = await DictItems.filter(id__in=ids).all()
        dict_data_ids = list({item.dict_data_id for item in items})

        await DictItems.filter(id__in=ids).delete()

        dict_datas = await DictData.filter(id__in=dict_data_ids).all()
        for dict_data in dict_datas:
            await self._clear_dict_cache(dict_data.dict_code)

    async def get_items_by_code(self, code: str) -> list[DictItemOut]:
        """根据编码获取字典项，保留原有缓存语义。"""
        cache_key = CacheKeys.format_key(CacheKeys.DICT_BY_CODE, code=code)

        async def _fetch_items():
            return await _fetch_active_items_by_code(code)

        cached_items = await cache_service.get_or_set(
            cache_key,
            _fetch_items,
            ttl=self.CACHE_TTL,
        )

        return [DictItemOut(**item) for item in cached_items]


async def _require_dict_data(dict_data_id: int) -> DictData:
    """读取字典类型，不存在时抛出统一业务错误。"""
    dict_data = await DictData.get_or_none(id=dict_data_id)
    if not dict_data:
        raise NotFound("字典类型不存在")
    return dict_data


async def _fetch_active_items_by_code(code: str) -> list[dict[str, object]]:
    """读取启用字典类型下的启用字典项并转为缓存安全结构。"""
    dict_data = await DictData.get_or_none(dict_code=code, status=1)
    if not dict_data:
        return []

    items = (
        await DictItems.filter(dict_data_id=dict_data.id, status=1)
        .order_by("value")
        .all()
    )

    return [_to_cache_item(item, dict_data) for item in items]


def _to_cache_item(item: DictItems, dict_data: DictData) -> dict[str, object]:
    """将字典项转换为可缓存的基础结构。"""
    return {
        "id": item.id,
        "label": item.label,
        "value": item.value,
        "status": item.status,
        "tag_type": item.tag_type,
        "dict_data_id": item.dict_data_id,
        "dict_name": dict_data.name,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }
