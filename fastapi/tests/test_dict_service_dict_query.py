"""
字典服务字典类型查询测试。
"""
import uuid

import pytest

from app.core.exceptions import NotFound
from app.services.system.dict_service import dict_service

pytest_plugins = ["dict_service_fixtures"]


class TestDictServiceGetDictPage:
    """测试字典类型分页查询。"""

    @pytest.mark.asyncio
    async def test_get_dict_page_basic(self, db, test_dict_data_for_service):
        """测试基本分页查询。"""
        result = await dict_service.get_dict_page(page=1, page_size=10)

        assert result.total >= 1
        assert len(result.list) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_dict_page_with_search(self, db, test_dict_data_for_service):
        """测试带搜索条件的分页查询。"""
        result = await dict_service.get_dict_page(
            page=1,
            page_size=10,
            search=test_dict_data_for_service.name[:10],
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_dict_page_empty_result(self, db):
        """测试空结果。"""
        result = await dict_service.get_dict_page(
            page=1,
            page_size=10,
            search="nonexistent_dict_12345",
        )

        assert result.total == 0
        assert len(result.list) == 0

    @pytest.mark.asyncio
    async def test_get_dict_page_pagination(self, db):
        """测试分页功能。"""
        from app.db.models.system import DictData

        # 创建多个字典类型用于覆盖分页边界。
        for i in range(15):
            await DictData.create(
                name=f"分页字典_{i}_{uuid.uuid4().hex[:6]}",
                dict_code=f"page_dict_{i}_{uuid.uuid4().hex[:6]}",
                status=1,
            )

        result1 = await dict_service.get_dict_page(page=1, page_size=10)
        assert len(result1.results) == 10

        result2 = await dict_service.get_dict_page(page=2, page_size=10)
        assert len(result2.results) >= 5


class TestDictServiceGetDict:
    """测试获取字典类型详情。"""

    @pytest.mark.asyncio
    async def test_get_dict_existing(self, db, test_dict_data_for_service):
        """测试获取存在的字典类型。"""
        result = await dict_service.get_dict(test_dict_data_for_service.id)

        assert result.id == test_dict_data_for_service.id
        assert result.name == test_dict_data_for_service.name
        assert result.dict_code == test_dict_data_for_service.dict_code

    @pytest.mark.asyncio
    async def test_get_dict_nonexistent(self, db):
        """测试获取不存在的字典类型。"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.get_dict(99999)

        assert "字典类型不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_dict_with_items(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试获取带字典项的字典类型。"""
        result = await dict_service.get_dict(test_dict_data_for_service.id)

        assert result.id == test_dict_data_for_service.id
        assert hasattr(result, "items")
        assert len(result.items) >= 1
