"""
字典管理 Service
"""

from app.core.cache import CacheKeys, cache_service
from app.core.exceptions import NotFound, ValidationError
from app.db.models.system import DictData, DictItems
from app.schemas.base import PageResult
from app.schemas.system import (
    DictDataCreate,
    DictDataOut,
    DictDataUpdate,
    DictItemCreate,
    DictItemOut,
    DictItemUpdate,
    DictWithItems,
)


class DictService:
    """字典管理服务"""

    # 缓存 TTL（秒）
    CACHE_TTL = 600  # 10分钟

    async def _clear_dict_cache(self, code: str | None = None) -> None:
        """
        清除字典缓存

        Args:
            code: 字典编码，为 None 时清除所有字典缓存
        """
        if code:
            cache_key = CacheKeys.format_key(CacheKeys.DICT_BY_CODE, code=code)
            await cache_service.delete(cache_key)
        else:
            # 清除所有字典相关缓存
            await cache_service.clear("dict:*")

    # ==================== 字典类型 ====================

    async def get_dict_page(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> PageResult[DictDataOut]:
        """
        获取字典类型分页列表
        """
        query = DictData.all()

        if search:
            query = query.filter(name__icontains=search)

        total = await query.count()
        dicts = await query.offset((page - 1) * page_size).limit(page_size).all()

        dict_list = [
            DictDataOut(
                id=d.id,
                name=d.name,
                code=d.code,
                status=d.status,
                desc=d.desc,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in dicts
        ]

        return PageResult.create(
            total=total, page=page, page_size=page_size, results=dict_list
        )

    async def get_dict(self, dict_id: int) -> DictWithItems:
        """
        获取字典类型详情（包含字典项）
        """
        dict_data = await DictData.get_or_none(id=dict_id)
        if not dict_data:
            raise NotFound("字典类型不存在")

        await dict_data.fetch_related("items")

        return DictWithItems(
            id=dict_data.id,
            name=dict_data.name,
            code=dict_data.code,
            status=dict_data.status,
            desc=dict_data.desc,
            created_at=dict_data.created_at,
            updated_at=dict_data.updated_at,
            items=[
                DictItemOut(
                    id=item.id,
                    label=item.label,
                    value=item.value,
                    sort=item.sort,
                    status=item.status,
                    is_default=item.is_default,
                    remark=item.remark,
                    dict_data_id=item.dict_data_id,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
                for item in dict_data.items
            ],
        )

    async def create_dict(self, dict_data: DictDataCreate) -> DictDataOut:
        """
        创建字典类型
        """
        # 检查编码是否已存在
        existing = await DictData.get_or_none(code=dict_data.code)
        if existing:
            raise ValidationError("字典编码已存在")

        d = await DictData.create(
            name=dict_data.name,
            code=dict_data.code,
            status=dict_data.status,
            desc=dict_data.desc,
        )

        return DictDataOut(
            id=d.id,
            name=d.name,
            code=d.code,
            status=d.status,
            desc=d.desc,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )

    async def update_dict(self, dict_id: int, dict_data: DictDataUpdate) -> DictDataOut:
        """
        更新字典类型
        """
        d = await DictData.get_or_none(id=dict_id)
        if not d:
            raise NotFound("字典类型不存在")

        old_code = d.code

        update_fields = {}
        for field, value in dict_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields[field] = value

        if update_fields:
            await DictData.filter(id=dict_id).update(**update_fields)
            await d.refresh_from_db()

        # 清除缓存
        await self._clear_dict_cache(old_code)
        if "code" in update_fields and update_fields["code"] != old_code:
            await self._clear_dict_cache(update_fields["code"])

        return DictDataOut(
            id=d.id,
            name=d.name,
            code=d.code,
            status=d.status,
            desc=d.desc,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )

    async def delete_dict(self, dict_id: int) -> None:
        """
        删除字典类型
        """
        d = await DictData.get_or_none(id=dict_id)
        if not d:
            raise NotFound("字典类型不存在")

        code = d.code
        await d.delete()

        # 清除缓存
        await self._clear_dict_cache(code)

    async def batch_delete_dicts(self, ids: list[int]) -> None:
        """
        批量删除字典类型
        """
        # 获取要删除的字典编码
        dicts = await DictData.filter(id__in=ids).all()
        codes = [d.code for d in dicts]

        await DictData.filter(id__in=ids).delete()

        # 清除所有相关缓存
        for code in codes:
            await self._clear_dict_cache(code)

    # ==================== 字典项 ====================

    async def get_item_page(
        self,
        page: int,
        page_size: int,
        dict_id: int | None = None,
        label: str | None = None,
        code: str | None = None,
    ) -> PageResult[DictItemOut]:
        """
        获取字典项分页列表
        """
        query = DictItems.all()

        if dict_id:
            query = query.filter(dict_data_id=dict_id)

        if label:
            query = query.filter(label__icontains=label)

        if code:
            # 关联查询：通过字典类型的 code 过滤
            query = query.filter(dict_data__code=code)

        total = await query.count()
        items = await query.order_by("sort").offset((page - 1) * page_size).limit(page_size).all()

        item_list = [
            DictItemOut(
                id=item.id,
                label=item.label,
                value=item.value,
                sort=item.sort,
                status=item.status,
                is_default=item.is_default,
                remark=item.remark,
                dict_data_id=item.dict_data_id,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

        return PageResult.create(
            total=total, page=page, page_size=page_size, results=item_list
        )

    async def get_items(self, dict_id: int) -> list[DictItemOut]:
        """
        获取字典项列表
        """
        dict_data = await DictData.get_or_none(id=dict_id)
        if not dict_data:
            raise NotFound("字典类型不存在")

        items = await DictItems.filter(dict_data_id=dict_id).order_by("sort").all()

        return [
            DictItemOut(
                id=item.id,
                label=item.label,
                value=item.value,
                sort=item.sort,
                status=item.status,
                is_default=item.is_default,
                remark=item.remark,
                dict_data_id=item.dict_data_id,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

    async def create_item(self, dict_id: int, item_data: DictItemCreate) -> DictItemOut:
        """
        创建字典项
        """
        dict_data = await DictData.get_or_none(id=dict_id)
        if not dict_data:
            raise NotFound("字典类型不存在")

        item = await DictItems.create(
            label=item_data.label,
            value=item_data.value,
            sort=item_data.sort,
            status=item_data.status,
            is_default=item_data.is_default,
            remark=item_data.remark,
            dict_data_id=dict_id,
        )

        # 清除该字典的缓存
        await self._clear_dict_cache(dict_data.code)

        return DictItemOut(
            id=item.id,
            label=item.label,
            value=item.value,
            sort=item.sort,
            status=item.status,
            is_default=item.is_default,
            remark=item.remark,
            dict_data_id=item.dict_data_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def update_item(self, dict_id: int, item_id: int, item_data: DictItemUpdate) -> DictItemOut:
        """
        更新字典项
        """
        item = await DictItems.get_or_none(id=item_id, dict_data_id=dict_id)
        if not item:
            raise NotFound("字典项不存在")

        update_fields = {}
        for field, value in item_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields[field] = value

        if update_fields:
            await DictItems.filter(id=item_id).update(**update_fields)
            await item.refresh_from_db()

        # 清除缓存
        dict_data = await DictData.get_or_none(id=dict_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.code)

        return DictItemOut(
            id=item.id,
            label=item.label,
            value=item.value,
            sort=item.sort,
            status=item.status,
            is_default=item.is_default,
            remark=item.remark,
            dict_data_id=item.dict_data_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def delete_item(self, dict_id: int, item_id: int) -> None:
        """
        删除字典项
        """
        item = await DictItems.get_or_none(id=item_id, dict_data_id=dict_id)
        if not item:
            raise NotFound("字典项不存在")

        await item.delete()

        # 清除缓存
        dict_data = await DictData.get_or_none(id=dict_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.code)

    async def create_item_flat(self, item_data: DictItemCreate) -> DictItemOut:
        """
        创建字典项（扁平接口）
        """
        # 检查字典类型是否存在
        dict_data = await DictData.get_or_none(id=item_data.dict_data_id)
        if not dict_data:
            raise NotFound("字典类型不存在")

        item = await DictItems.create(
            label=item_data.label,
            value=item_data.value,
            sort=item_data.sort,
            status=item_data.status,
            is_default=item_data.is_default,
            remark=item_data.remark,
            dict_data_id=item_data.dict_data_id,
        )

        # 清除缓存
        await self._clear_dict_cache(dict_data.code)

        return DictItemOut(
            id=item.id,
            label=item.label,
            value=item.value,
            sort=item.sort,
            status=item.status,
            is_default=item.is_default,
            remark=item.remark,
            dict_data_id=item.dict_data_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def update_item_flat(self, item_id: int, item_data: DictItemUpdate) -> DictItemOut:
        """
        更新字典项（扁平接口）
        """
        item = await DictItems.get_or_none(id=item_id)
        if not item:
            raise NotFound("字典项不存在")

        update_fields = {}
        for field, value in item_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields[field] = value

        if update_fields:
            await DictItems.filter(id=item_id).update(**update_fields)
            await item.refresh_from_db()

        # 清除缓存
        dict_data = await DictData.get_or_none(id=item.dict_data_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.code)

        return DictItemOut(
            id=item.id,
            label=item.label,
            value=item.value,
            sort=item.sort,
            status=item.status,
            is_default=item.is_default,
            remark=item.remark,
            dict_data_id=item.dict_data_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def delete_item_flat(self, item_id: int) -> None:
        """
        删除字典项（扁平接口）
        """
        item = await DictItems.get_or_none(id=item_id)
        if not item:
            raise NotFound("字典项不存在")

        dict_data_id = item.dict_data_id
        await item.delete()

        # 清除缓存
        dict_data = await DictData.get_or_none(id=dict_data_id)
        if dict_data:
            await self._clear_dict_cache(dict_data.code)

    async def batch_delete_items_flat(self, ids: list[int]) -> None:
        """
        批量删除字典项（扁平接口）
        """
        # 获取要删除的字典项及其所属字典
        items = await DictItems.filter(id__in=ids).all()
        dict_data_ids = list(set(item.dict_data_id for item in items))

        await DictItems.filter(id__in=ids).delete()

        # 清除相关字典的缓存
        dict_datas = await DictData.filter(id__in=dict_data_ids).all()
        for dict_data in dict_datas:
            await self._clear_dict_cache(dict_data.code)

    async def get_items_by_code(self, code: str) -> list[DictItemOut]:
        """
        根据编码获取字典项（带缓存）
        """
        cache_key = CacheKeys.format_key(CacheKeys.DICT_BY_CODE, code=code)

        async def _fetch_items():
            dict_data = await DictData.get_or_none(code=code, status=1)
            if not dict_data:
                return []

            items = (
                await DictItems.filter(dict_data_id=dict_data.id, status=1)
                .order_by("sort")
                .all()
            )

            return [
                {
                    "id": item.id,
                    "label": item.label,
                    "value": item.value,
                    "sort": item.sort,
                    "status": item.status,
                    "is_default": item.is_default,
                    "remark": item.remark,
                    "dict_data_id": item.dict_data_id,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                }
                for item in items
            ]

        cached_items = await cache_service.get_or_set(
            cache_key, _fetch_items, ttl=self.CACHE_TTL
        )

        return [
            DictItemOut(**item)
            for item in cached_items
        ]


# 导出服务实例
dict_service = DictService()
