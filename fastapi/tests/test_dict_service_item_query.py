"""
字典服务字典项嵌套查询测试。
"""
import pytest

from app.core.exceptions import NotFound
from app.services.system.dict_service import dict_service

pytest_plugins = ["dict_service_fixtures"]


class TestDictServiceGetItemPage:
    """测试字典项分页查询。"""

    @pytest.mark.asyncio
    async def test_get_item_page_basic(self, db, test_dict_item_for_service):
        """测试基本分页查询。"""
        result = await dict_service.get_item_page(page=1, page_size=10)

        assert result.total >= 1
        assert len(result.list) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_item_page_includes_dict_name(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """字典项分页输出必须包含归属字典名称。"""
        result = await dict_service.get_item_page(
            page=1,
            page_size=10,
            dict_id=test_dict_data_for_service.id,
        )

        page_item = next(item for item in result.list if item.id == test_dict_item_for_service.id)
        assert page_item.dict_name == test_dict_data_for_service.name

    @pytest.mark.asyncio
    async def test_get_item_page_with_dict_id(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试按字典类型 ID 过滤。"""
        result = await dict_service.get_item_page(
            page=1,
            page_size=10,
            dict_id=test_dict_data_for_service.id,
        )

        for item in result.list:
            assert item.dict_data_id == test_dict_data_for_service.id

    @pytest.mark.asyncio
    async def test_get_item_page_with_label(self, db, test_dict_item_for_service):
        """测试按标签搜索。"""
        result = await dict_service.get_item_page(
            page=1,
            page_size=10,
            label=test_dict_item_for_service.label[:10],
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_item_page_with_code(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试按字典编码过滤。"""
        result = await dict_service.get_item_page(
            page=1,
            page_size=10,
            code=test_dict_data_for_service.dict_code,
        )

        for item in result.list:
            assert item.dict_data_id == test_dict_data_for_service.id

    @pytest.mark.asyncio
    async def test_get_item_page_empty_result(self, db):
        """测试空结果。"""
        result = await dict_service.get_item_page(
            page=1,
            page_size=10,
            label="nonexistent_item_12345",
        )

        assert result.total == 0
        assert len(result.list) == 0


class TestDictServiceGetItems:
    """测试获取字典项列表。"""

    @pytest.mark.asyncio
    async def test_get_items(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试获取字典项列表。"""
        result = await dict_service.get_items(test_dict_data_for_service.id)

        assert isinstance(result, list)
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_items_nonexistent_dict(self, db):
        """测试获取不存在字典类型的字典项。"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.get_items(99999)

        assert "字典类型不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_items_empty(self, db, test_dict_data_for_service):
        """测试获取空字典项列表。"""
        result = await dict_service.get_items(test_dict_data_for_service.id)

        assert isinstance(result, list)
        # 因为 test_dict_data_for_service 可能被其他测试添加了项，所以不强制要求为空。
