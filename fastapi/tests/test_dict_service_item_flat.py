"""
字典服务字典项扁平接口和编码查询测试
"""
import uuid

import pytest

from app.core.exceptions import NotFound
from app.schemas.system import DictItemCreate, DictItemUpdate
from app.services.system.dict_service import dict_service

pytest_plugins = ["dict_service_fixtures"]

class TestDictServiceCreateItemFlat:
    """测试扁平接口创建字典项"""

    @pytest.mark.asyncio
    async def test_create_item_flat_basic(self, db, test_dict_data_for_service):
        """测试扁平接口基本创建字典项"""
        item_data = DictItemCreate(
            label=f"扁平项_{uuid.uuid4().hex[:8]}",
            value=f"flat_value_{uuid.uuid4().hex[:8]}",
            status=1,
            dict_data_id=test_dict_data_for_service.id,
        )

        result = await dict_service.create_item_flat(item_data)

        assert result.label == item_data.label
        assert result.value == item_data.value
        assert result.dict_data_id == test_dict_data_for_service.id

    @pytest.mark.asyncio
    async def test_create_item_flat_nonexistent_dict(self, db):
        """测试扁平接口在不存在字典类型下创建字典项"""
        item_data = DictItemCreate(
            label=f"字典项_{uuid.uuid4().hex[:8]}",
            value=f"value_{uuid.uuid4().hex[:8]}",
            status=1,
            dict_data_id=99999,
        )

        with pytest.raises(NotFound) as exc_info:
            await dict_service.create_item_flat(item_data)

        assert "字典类型不存在" in str(exc_info.value)


class TestDictServiceUpdateItemFlat:
    """测试扁平接口更新字典项"""

    @pytest.mark.asyncio
    async def test_update_item_flat_basic(self, db, test_dict_item_for_service):
        """测试扁平接口基本更新字典项"""
        update_data = DictItemUpdate(
            label="扁平更新后的标签",
        )

        result = await dict_service.update_item_flat(test_dict_item_for_service.id, update_data)

        assert result.label == "扁平更新后的标签"

    @pytest.mark.asyncio
    async def test_update_item_flat_nonexistent(self, db):
        """测试扁平接口更新不存在的字典项"""
        update_data = DictItemUpdate(label="更新标签")

        with pytest.raises(NotFound) as exc_info:
            await dict_service.update_item_flat(99999, update_data)

        assert "字典项不存在" in str(exc_info.value)


class TestDictServiceDeleteItemFlat:
    """测试扁平接口删除字典项"""

    @pytest.mark.asyncio
    async def test_delete_item_flat(self, db, test_dict_data_for_service):
        """测试扁平接口删除字典项"""
        from app.db.models.system import DictItems

        # 创建一个新字典项用于删除
        item_to_delete = await DictItems.create(
            label=f"扁平删除项_{uuid.uuid4().hex[:8]}",
            value=f"flat_del_value_{uuid.uuid4().hex[:8]}",
            status=1,
            dict_data_id=test_dict_data_for_service.id,
        )

        await dict_service.delete_item_flat(item_to_delete.id)

        # 验证字典项已删除
        deleted_item = await DictItems.get_or_none(id=item_to_delete.id)
        assert deleted_item is None

    @pytest.mark.asyncio
    async def test_delete_item_flat_nonexistent(self, db):
        """测试扁平接口删除不存在的字典项"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.delete_item_flat(99999)

        assert "字典项不存在" in str(exc_info.value)


class TestDictServiceBatchDeleteItemsFlat:
    """测试扁平接口批量删除字典项"""

    @pytest.mark.asyncio
    async def test_batch_delete_items_flat(self, db, test_dict_data_for_service):
        """测试扁平接口批量删除字典项"""
        from app.db.models.system import DictItems

        # 创建多个字典项
        item_ids = []
        for i in range(3):
            item = await DictItems.create(
                label=f"批量项_{i}_{uuid.uuid4().hex[:8]}",
                value=f"batch_value_{i}_{uuid.uuid4().hex[:8]}",
                status=1,
                dict_data_id=test_dict_data_for_service.id,
            )
            item_ids.append(item.id)

        # 批量删除
        await dict_service.batch_delete_items_flat(item_ids)

        # 验证字典项已删除
        for item_id in item_ids:
            deleted_item = await DictItems.get_or_none(id=item_id)
            assert deleted_item is None

    @pytest.mark.asyncio
    async def test_batch_delete_items_flat_empty_list(self, db):
        """测试扁平接口批量删除空列表"""
        # 应该不抛出异常
        await dict_service.batch_delete_items_flat([])


class TestDictServiceGetItemsByCode:
    """测试根据编码获取字典项"""

    @pytest.mark.asyncio
    async def test_get_items_by_code(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试根据编码获取字典项"""
        result = await dict_service.get_items_by_code(test_dict_data_for_service.dict_code)

        assert isinstance(result, list)
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_items_by_code_nonexistent(self, db):
        """测试根据不存在的编码获取字典项"""
        result = await dict_service.get_items_by_code("nonexistent_code_12345")

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_items_by_code_inactive_dict(self, db):
        """测试根据禁用字典类型的编码获取字典项"""
        from app.db.models.system import DictData

        # 创建禁用的字典类型
        inactive_dict = await DictData.create(
            name=f"禁用字典_{uuid.uuid4().hex[:8]}",
            dict_code=f"inactive_dict_{uuid.uuid4().hex[:8]}",
            status=0,
        )

        result = await dict_service.get_items_by_code(inactive_dict.dict_code)

        # 应该返回空列表（因为字典类型被禁用）
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_items_by_code_only_active_items(self, db):
        """测试只返回激活状态的字典项"""
        from app.db.models.system import DictData, DictItems

        # 创建字典类型
        dict_data = await DictData.create(
            name=f"激活测试字典_{uuid.uuid4().hex[:8]}",
            dict_code=f"active_test_dict_{uuid.uuid4().hex[:8]}",
            status=1,
        )

        # 创建激活的字典项
        active_item = await DictItems.create(
            label="激活项",
            value="active_value",
            status=1,
            dict_data_id=dict_data.id,
        )

        # 创建禁用的字典项
        inactive_item = await DictItems.create(
            label="禁用项",
            value="inactive_value",
            status=0,
            dict_data_id=dict_data.id,
        )

        result = await dict_service.get_items_by_code(dict_data.dict_code)

        # 应该只返回激活的字典项
        assert len(result) == 1
        assert result[0].value == "active_value"
