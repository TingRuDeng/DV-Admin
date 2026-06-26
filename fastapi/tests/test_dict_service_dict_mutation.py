"""
字典服务字典类型写操作测试。
"""
import uuid

import pytest

from app.core.exceptions import NotFound, ValidationError
from app.schemas.system import DictDataCreate, DictDataUpdate
from app.services.system.dict_service import dict_service

pytest_plugins = ["dict_service_fixtures"]


class TestDictServiceCreateDict:
    """测试创建字典类型。"""

    @pytest.mark.asyncio
    async def test_create_dict_basic(self, db):
        """测试基本创建字典类型。"""
        dict_data = DictDataCreate(
            name=f"新字典_{uuid.uuid4().hex[:8]}",
            dict_code=f"new_dict_{uuid.uuid4().hex[:8]}",
            status=1,
            remark="新字典描述",
        )

        result = await dict_service.create_dict(dict_data)

        assert result.name == dict_data.name
        assert result.dict_code == dict_data.dict_code
        assert result.status == 1

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, db, test_dict_data_for_service):
        """测试创建重复编码。"""
        dict_data = DictDataCreate(
            name=f"重复字典_{uuid.uuid4().hex[:8]}",
            dict_code=test_dict_data_for_service.dict_code,
            status=1,
        )

        with pytest.raises(ValidationError) as exc_info:
            await dict_service.create_dict(dict_data)

        assert "字典编码已存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_dict_with_all_fields(self, db):
        """测试创建字典类型包含所有字段。"""
        dict_data = DictDataCreate(
            name=f"完整字典_{uuid.uuid4().hex[:8]}",
            dict_code=f"full_dict_{uuid.uuid4().hex[:8]}",
            status=1,
            remark="这是一个完整的字典描述",
        )

        result = await dict_service.create_dict(dict_data)

        assert result.name == dict_data.name
        assert result.dict_code == dict_data.dict_code
        assert result.status == 1
        assert result.remark == "这是一个完整的字典描述"


class TestDictServiceUpdateDict:
    """测试更新字典类型。"""

    @pytest.mark.asyncio
    async def test_update_dict_basic(self, db, test_dict_data_for_service):
        """测试基本更新字典类型。"""
        update_data = DictDataUpdate(
            name="更新后的字典名",
            remark="更新后的描述",
        )

        result = await dict_service.update_dict(test_dict_data_for_service.id, update_data)

        assert result.name == "更新后的字典名"
        assert result.remark == "更新后的描述"

    @pytest.mark.asyncio
    async def test_update_dict_status(self, db, test_dict_data_for_service):
        """测试更新字典类型状态。"""
        update_data = DictDataUpdate(status=0)

        result = await dict_service.update_dict(test_dict_data_for_service.id, update_data)

        assert result.status == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_dict(self, db):
        """测试更新不存在的字典类型。"""
        update_data = DictDataUpdate(name="更新名字")

        with pytest.raises(NotFound) as exc_info:
            await dict_service.update_dict(99999, update_data)

        assert "字典类型不存在" in str(exc_info.value)


class TestDictServiceDeleteDict:
    """测试删除字典类型。"""

    @pytest.mark.asyncio
    async def test_delete_dict(self, db):
        """测试删除字典类型。"""
        from app.db.models.system import DictData

        # 创建一个新字典类型用于删除。
        dict_to_delete = await DictData.create(
            name=f"待删除字典_{uuid.uuid4().hex[:8]}",
            dict_code=f"del_dict_{uuid.uuid4().hex[:8]}",
            status=1,
        )

        await dict_service.delete_dict(dict_to_delete.id)

        # 验证字典类型已删除。
        deleted_dict = await DictData.get_or_none(id=dict_to_delete.id)
        assert deleted_dict is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_dict(self, db):
        """测试删除不存在的字典类型。"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.delete_dict(99999)

        assert "字典类型不存在" in str(exc_info.value)


class TestDictServiceBatchDeleteDicts:
    """测试批量删除字典类型。"""

    @pytest.mark.asyncio
    async def test_batch_delete_dicts(self, db):
        """测试批量删除字典类型。"""
        from app.db.models.system import DictData

        dict_ids = []
        for i in range(3):
            dict_data = await DictData.create(
                name=f"批量字典_{i}_{uuid.uuid4().hex[:8]}",
                dict_code=f"batch_dict_{i}_{uuid.uuid4().hex[:8]}",
                status=1,
            )
            dict_ids.append(dict_data.id)

        await dict_service.batch_delete_dicts(dict_ids)

        for dict_id in dict_ids:
            deleted_dict = await DictData.get_or_none(id=dict_id)
            assert deleted_dict is None

    @pytest.mark.asyncio
    async def test_batch_delete_dicts_empty_list(self, db):
        """测试批量删除空列表。"""
        await dict_service.batch_delete_dicts([])
