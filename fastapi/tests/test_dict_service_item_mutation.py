"""
字典服务字典项嵌套写操作测试。
"""
import uuid

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import NotFound
from app.schemas.system import DictItemCreate, DictItemUpdate
from app.services.system.dict_service import dict_service

pytest_plugins = ["dict_service_fixtures"]


class TestDictServiceCreateItem:
    """测试创建字典项。"""

    def test_create_item_rejects_overlength_label(self):
        """测试创建字典项拒绝超长标签。"""
        with pytest.raises(PydanticValidationError):
            DictItemCreate(
                label="测" * 33,
                value="valid_value",
                status=1,
                dict_data_id=1,
            )

    def test_create_item_rejects_overlength_value(self):
        """测试创建字典项拒绝超长值。"""
        with pytest.raises(PydanticValidationError):
            DictItemCreate(
                label="有效标签",
                value="v" * 33,
                status=1,
                dict_data_id=1,
            )

    @pytest.mark.asyncio
    async def test_create_item_basic(self, db, test_dict_data_for_service):
        """测试基本创建字典项。"""
        item_data = DictItemCreate(
            label=f"新字典项_{uuid.uuid4().hex[:8]}",
            value=f"new_value_{uuid.uuid4().hex[:8]}",
            status=1,
            dict_data_id=test_dict_data_for_service.id,
        )

        result = await dict_service.create_item(test_dict_data_for_service.id, item_data)

        assert result.label == item_data.label
        assert result.value == item_data.value
        assert result.dict_data_id == test_dict_data_for_service.id

    @pytest.mark.asyncio
    async def test_create_item_nonexistent_dict(self, db):
        """测试在不存在字典类型下创建字典项。"""
        item_data = DictItemCreate(
            label=f"字典项_{uuid.uuid4().hex[:8]}",
            value=f"value_{uuid.uuid4().hex[:8]}",
            status=1,
            dict_data_id=99999,
        )

        with pytest.raises(NotFound) as exc_info:
            await dict_service.create_item(99999, item_data)

        assert "字典类型不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_item_with_status(self, db, test_dict_data_for_service):
        """测试创建字典项包含状态字段。"""
        item_data = DictItemCreate(
            label=f"完整字典项_{uuid.uuid4().hex[:8]}",
            value=f"full_value_{uuid.uuid4().hex[:8]}",
            status=1,
            dict_data_id=test_dict_data_for_service.id,
        )

        result = await dict_service.create_item(test_dict_data_for_service.id, item_data)

        assert result.label == item_data.label
        assert result.value == item_data.value
        assert result.status == 1


class TestDictServiceUpdateItem:
    """测试更新字典项。"""

    def test_update_item_rejects_overlength_label(self):
        """测试更新字典项拒绝超长标签。"""
        with pytest.raises(PydanticValidationError):
            DictItemUpdate(label="测" * 33)

    def test_update_item_rejects_overlength_value(self):
        """测试更新字典项拒绝超长值。"""
        with pytest.raises(PydanticValidationError):
            DictItemUpdate(value="v" * 33)

    @pytest.mark.asyncio
    async def test_update_item_basic(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试基本更新字典项。"""
        update_data = DictItemUpdate(
            label="更新后的标签",
        )

        result = await dict_service.update_item(
            test_dict_data_for_service.id,
            test_dict_item_for_service.id,
            update_data,
        )

        assert result.label == "更新后的标签"

    @pytest.mark.asyncio
    async def test_update_item_status(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试更新字典项状态。"""
        update_data = DictItemUpdate(status=0)

        result = await dict_service.update_item(
            test_dict_data_for_service.id,
            test_dict_item_for_service.id,
            update_data,
        )

        assert result.status == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_item(self, db, test_dict_data_for_service):
        """测试更新不存在的字典项。"""
        update_data = DictItemUpdate(label="更新标签")

        with pytest.raises(NotFound) as exc_info:
            await dict_service.update_item(test_dict_data_for_service.id, 99999, update_data)

        assert "字典项不存在" in str(exc_info.value)


class TestDictServiceDeleteItem:
    """测试删除字典项。"""

    @pytest.mark.asyncio
    async def test_delete_item(self, db, test_dict_data_for_service):
        """测试删除字典项。"""
        from app.db.models.system import DictItems

        # 创建一个新字典项用于删除。
        item_to_delete = await DictItems.create(
            label=f"待删除项_{uuid.uuid4().hex[:8]}",
            value=f"del_value_{uuid.uuid4().hex[:8]}",
            status=1,
            dict_data_id=test_dict_data_for_service.id,
        )

        await dict_service.delete_item(test_dict_data_for_service.id, item_to_delete.id)

        # 验证字典项已删除。
        deleted_item = await DictItems.get_or_none(id=item_to_delete.id)
        assert deleted_item is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_item(self, db, test_dict_data_for_service):
        """测试删除不存在的字典项。"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.delete_item(test_dict_data_for_service.id, 99999)

        assert "字典项不存在" in str(exc_info.value)
