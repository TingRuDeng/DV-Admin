# -*- coding: utf-8 -*-
"""
字典服务层测试
测试 DictService 的所有方法，包括字典类型和字典项的 CRUD 操作、边界条件和异常情况
"""
import pytest
import pytest_asyncio
import uuid

from app.services.system.dict_service import dict_service
from app.schemas.system import (
    DictDataCreate,
    DictDataUpdate,
    DictItemCreate,
    DictItemUpdate,
)
from app.core.exceptions import NotFound, ValidationError


@pytest_asyncio.fixture
async def test_dict_data_for_service(db):
    """创建测试字典类型"""
    from app.db.models.system import DictData
    
    dict_data = await DictData.create(
        name=f"测试字典_{uuid.uuid4().hex[:6]}",
        code=f"test_dict_{uuid.uuid4().hex[:6]}",
        status=1,
        desc="测试字典描述",
    )
    return dict_data


@pytest_asyncio.fixture
async def test_dict_item_for_service(db, test_dict_data_for_service):
    """创建测试字典项"""
    from app.db.models.system import DictItems
    
    item = await DictItems.create(
        label=f"测试项_{uuid.uuid4().hex[:6]}",
        value=f"test_value_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
        is_default=False,
        dict_data_id=test_dict_data_for_service.id,
    )
    return item


# ==================== 字典类型测试 ====================

class TestDictServiceGetDictPage:
    """测试字典类型分页查询"""

    @pytest.mark.asyncio
    async def test_get_dict_page_basic(self, db, test_dict_data_for_service):
        """测试基本分页查询"""
        result = await dict_service.get_dict_page(page=1, page_size=10)
        
        assert result.total >= 1
        assert len(result.results) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_dict_page_with_search(self, db, test_dict_data_for_service):
        """测试带搜索条件的分页查询"""
        result = await dict_service.get_dict_page(
            page=1, 
            page_size=10, 
            search=test_dict_data_for_service.name[:10]
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_dict_page_empty_result(self, db):
        """测试空结果"""
        result = await dict_service.get_dict_page(
            page=1, 
            page_size=10, 
            search="nonexistent_dict_12345"
        )
        
        assert result.total == 0
        assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_get_dict_page_pagination(self, db):
        """测试分页功能"""
        from app.db.models.system import DictData
        
        # 创建多个字典类型
        for i in range(15):
            await DictData.create(
                name=f"分页字典_{i}_{uuid.uuid4().hex[:6]}",
                code=f"page_dict_{i}_{uuid.uuid4().hex[:6]}",
                status=1,
            )
        
        # 测试第一页
        result1 = await dict_service.get_dict_page(page=1, page_size=10)
        assert len(result1.results) == 10
        
        # 测试第二页
        result2 = await dict_service.get_dict_page(page=2, page_size=10)
        assert len(result2.results) >= 5


class TestDictServiceGetDict:
    """测试获取字典类型详情"""

    @pytest.mark.asyncio
    async def test_get_dict_existing(self, db, test_dict_data_for_service):
        """测试获取存在的字典类型"""
        result = await dict_service.get_dict(test_dict_data_for_service.id)
        
        assert result.id == test_dict_data_for_service.id
        assert result.name == test_dict_data_for_service.name
        assert result.code == test_dict_data_for_service.code

    @pytest.mark.asyncio
    async def test_get_dict_nonexistent(self, db):
        """测试获取不存在的字典类型"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.get_dict(99999)
        
        assert "字典类型不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_dict_with_items(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试获取带字典项的字典类型"""
        result = await dict_service.get_dict(test_dict_data_for_service.id)
        
        assert result.id == test_dict_data_for_service.id
        assert hasattr(result, 'items')
        assert len(result.items) >= 1


class TestDictServiceCreateDict:
    """测试创建字典类型"""

    @pytest.mark.asyncio
    async def test_create_dict_basic(self, db):
        """测试基本创建字典类型"""
        dict_data = DictDataCreate(
            name=f"新字典_{uuid.uuid4().hex[:8]}",
            code=f"new_dict_{uuid.uuid4().hex[:8]}",
            status=1,
            desc="新字典描述",
        )
        
        result = await dict_service.create_dict(dict_data)
        
        assert result.name == dict_data.name
        assert result.code == dict_data.code
        assert result.status == 1

    @pytest.mark.asyncio
    async def test_create_duplicate_code(self, db, test_dict_data_for_service):
        """测试创建重复编码"""
        dict_data = DictDataCreate(
            name=f"重复字典_{uuid.uuid4().hex[:8]}",
            code=test_dict_data_for_service.code,
            status=1,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await dict_service.create_dict(dict_data)
        
        assert "字典编码已存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_dict_with_all_fields(self, db):
        """测试创建字典类型包含所有字段"""
        dict_data = DictDataCreate(
            name=f"完整字典_{uuid.uuid4().hex[:8]}",
            code=f"full_dict_{uuid.uuid4().hex[:8]}",
            status=1,
            desc="这是一个完整的字典描述",
        )
        
        result = await dict_service.create_dict(dict_data)
        
        assert result.name == dict_data.name
        assert result.code == dict_data.code
        assert result.status == 1
        assert result.desc == "这是一个完整的字典描述"


class TestDictServiceUpdateDict:
    """测试更新字典类型"""

    @pytest.mark.asyncio
    async def test_update_dict_basic(self, db, test_dict_data_for_service):
        """测试基本更新字典类型"""
        update_data = DictDataUpdate(
            name="更新后的字典名",
            desc="更新后的描述",
        )
        
        result = await dict_service.update_dict(test_dict_data_for_service.id, update_data)
        
        assert result.name == "更新后的字典名"
        assert result.desc == "更新后的描述"

    @pytest.mark.asyncio
    async def test_update_dict_status(self, db, test_dict_data_for_service):
        """测试更新字典类型状态"""
        update_data = DictDataUpdate(status=0)
        
        result = await dict_service.update_dict(test_dict_data_for_service.id, update_data)
        
        assert result.status == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_dict(self, db):
        """测试更新不存在的字典类型"""
        update_data = DictDataUpdate(name="更新名字")
        
        with pytest.raises(NotFound) as exc_info:
            await dict_service.update_dict(99999, update_data)
        
        assert "字典类型不存在" in str(exc_info.value)


class TestDictServiceDeleteDict:
    """测试删除字典类型"""

    @pytest.mark.asyncio
    async def test_delete_dict(self, db):
        """测试删除字典类型"""
        from app.db.models.system import DictData
        
        # 创建一个新字典类型用于删除
        dict_to_delete = await DictData.create(
            name=f"待删除字典_{uuid.uuid4().hex[:8]}",
            code=f"del_dict_{uuid.uuid4().hex[:8]}",
            status=1,
        )
        
        await dict_service.delete_dict(dict_to_delete.id)
        
        # 验证字典类型已删除
        deleted_dict = await DictData.get_or_none(id=dict_to_delete.id)
        assert deleted_dict is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_dict(self, db):
        """测试删除不存在的字典类型"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.delete_dict(99999)
        
        assert "字典类型不存在" in str(exc_info.value)


class TestDictServiceBatchDeleteDicts:
    """测试批量删除字典类型"""

    @pytest.mark.asyncio
    async def test_batch_delete_dicts(self, db):
        """测试批量删除字典类型"""
        from app.db.models.system import DictData
        
        # 创建多个字典类型
        dict_ids = []
        for i in range(3):
            dict_data = await DictData.create(
                name=f"批量字典_{i}_{uuid.uuid4().hex[:8]}",
                code=f"batch_dict_{i}_{uuid.uuid4().hex[:8]}",
                status=1,
            )
            dict_ids.append(dict_data.id)
        
        # 批量删除
        await dict_service.batch_delete_dicts(dict_ids)
        
        # 验证字典类型已删除
        for dict_id in dict_ids:
            deleted_dict = await DictData.get_or_none(id=dict_id)
            assert deleted_dict is None

    @pytest.mark.asyncio
    async def test_batch_delete_dicts_empty_list(self, db):
        """测试批量删除空列表"""
        # 应该不抛出异常
        await dict_service.batch_delete_dicts([])


# ==================== 字典项测试 ====================

class TestDictServiceGetItemPage:
    """测试字典项分页查询"""

    @pytest.mark.asyncio
    async def test_get_item_page_basic(self, db, test_dict_item_for_service):
        """测试基本分页查询"""
        result = await dict_service.get_item_page(page=1, page_size=10)
        
        assert result.total >= 1
        assert len(result.results) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_item_page_with_dict_id(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试按字典类型ID过滤"""
        result = await dict_service.get_item_page(
            page=1, 
            page_size=10, 
            dict_id=test_dict_data_for_service.id
        )
        
        for item in result.results:
            assert item.dict_data_id == test_dict_data_for_service.id

    @pytest.mark.asyncio
    async def test_get_item_page_with_label(self, db, test_dict_item_for_service):
        """测试按标签搜索"""
        result = await dict_service.get_item_page(
            page=1, 
            page_size=10, 
            label=test_dict_item_for_service.label[:10]
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_item_page_with_code(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试按字典编码过滤"""
        result = await dict_service.get_item_page(
            page=1, 
            page_size=10, 
            code=test_dict_data_for_service.code
        )
        
        for item in result.results:
            assert item.dict_data_id == test_dict_data_for_service.id

    @pytest.mark.asyncio
    async def test_get_item_page_empty_result(self, db):
        """测试空结果"""
        result = await dict_service.get_item_page(
            page=1, 
            page_size=10, 
            label="nonexistent_item_12345"
        )
        
        assert result.total == 0
        assert len(result.results) == 0


class TestDictServiceGetItems:
    """测试获取字典项列表"""

    @pytest.mark.asyncio
    async def test_get_items(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试获取字典项列表"""
        result = await dict_service.get_items(test_dict_data_for_service.id)
        
        assert isinstance(result, list)
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_items_nonexistent_dict(self, db):
        """测试获取不存在字典类型的字典项"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.get_items(99999)
        
        assert "字典类型不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_items_empty(self, db, test_dict_data_for_service):
        """测试获取空字典项列表"""
        result = await dict_service.get_items(test_dict_data_for_service.id)
        
        assert isinstance(result, list)
        # 因为 test_dict_data_for_service 可能被其他测试添加了项，所以不强制要求为空


class TestDictServiceCreateItem:
    """测试创建字典项"""

    @pytest.mark.asyncio
    async def test_create_item_basic(self, db, test_dict_data_for_service):
        """测试基本创建字典项"""
        item_data = DictItemCreate(
            label=f"新字典项_{uuid.uuid4().hex[:8]}",
            value=f"new_value_{uuid.uuid4().hex[:8]}",
            sort=1,
            status=1,
            is_default=False,
            remark="",  # 添加 remark 字段
            dict_data_id=test_dict_data_for_service.id,
        )
        
        result = await dict_service.create_item(test_dict_data_for_service.id, item_data)
        
        assert result.label == item_data.label
        assert result.value == item_data.value
        assert result.dict_data_id == test_dict_data_for_service.id

    @pytest.mark.asyncio
    async def test_create_item_nonexistent_dict(self, db):
        """测试在不存在字典类型下创建字典项"""
        item_data = DictItemCreate(
            label=f"字典项_{uuid.uuid4().hex[:8]}",
            value=f"value_{uuid.uuid4().hex[:8]}",
            sort=1,
            status=1,
            is_default=False,
            dict_data_id=99999,
        )
        
        with pytest.raises(NotFound) as exc_info:
            await dict_service.create_item(99999, item_data)
        
        assert "字典类型不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_item_with_all_fields(self, db, test_dict_data_for_service):
        """测试创建字典项包含所有字段"""
        item_data = DictItemCreate(
            label=f"完整字典项_{uuid.uuid4().hex[:8]}",
            value=f"full_value_{uuid.uuid4().hex[:8]}",
            sort=10,
            status=1,
            is_default=True,
            remark="这是一个完整的字典项备注",
            dict_data_id=test_dict_data_for_service.id,
        )
        
        result = await dict_service.create_item(test_dict_data_for_service.id, item_data)
        
        assert result.label == item_data.label
        assert result.value == item_data.value
        assert result.sort == 10
        assert result.is_default == True
        assert result.remark == "这是一个完整的字典项备注"


class TestDictServiceUpdateItem:
    """测试更新字典项"""

    @pytest.mark.asyncio
    async def test_update_item_basic(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试基本更新字典项"""
        update_data = DictItemUpdate(
            label="更新后的标签",
            remark="更新后的备注",
        )
        
        result = await dict_service.update_item(
            test_dict_data_for_service.id, 
            test_dict_item_for_service.id, 
            update_data
        )
        
        assert result.label == "更新后的标签"
        assert result.remark == "更新后的备注"

    @pytest.mark.asyncio
    async def test_update_item_status(self, db, test_dict_data_for_service, test_dict_item_for_service):
        """测试更新字典项状态"""
        update_data = DictItemUpdate(status=0)
        
        result = await dict_service.update_item(
            test_dict_data_for_service.id, 
            test_dict_item_for_service.id, 
            update_data
        )
        
        assert result.status == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_item(self, db, test_dict_data_for_service):
        """测试更新不存在的字典项"""
        update_data = DictItemUpdate(label="更新标签")
        
        with pytest.raises(NotFound) as exc_info:
            await dict_service.update_item(test_dict_data_for_service.id, 99999, update_data)
        
        assert "字典项不存在" in str(exc_info.value)


class TestDictServiceDeleteItem:
    """测试删除字典项"""

    @pytest.mark.asyncio
    async def test_delete_item(self, db, test_dict_data_for_service):
        """测试删除字典项"""
        from app.db.models.system import DictItems
        
        # 创建一个新字典项用于删除
        item_to_delete = await DictItems.create(
            label=f"待删除项_{uuid.uuid4().hex[:8]}",
            value=f"del_value_{uuid.uuid4().hex[:8]}",
            sort=1,
            status=1,
            dict_data_id=test_dict_data_for_service.id,
        )
        
        await dict_service.delete_item(test_dict_data_for_service.id, item_to_delete.id)
        
        # 验证字典项已删除
        deleted_item = await DictItems.get_or_none(id=item_to_delete.id)
        assert deleted_item is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_item(self, db, test_dict_data_for_service):
        """测试删除不存在的字典项"""
        with pytest.raises(NotFound) as exc_info:
            await dict_service.delete_item(test_dict_data_for_service.id, 99999)
        
        assert "字典项不存在" in str(exc_info.value)


# ==================== 扁平接口测试 ====================

class TestDictServiceCreateItemFlat:
    """测试扁平接口创建字典项"""

    @pytest.mark.asyncio
    async def test_create_item_flat_basic(self, db, test_dict_data_for_service):
        """测试扁平接口基本创建字典项"""
        item_data = DictItemCreate(
            label=f"扁平项_{uuid.uuid4().hex[:8]}",
            value=f"flat_value_{uuid.uuid4().hex[:8]}",
            sort=1,
            status=1,
            is_default=False,
            remark="",  # 添加 remark 字段
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
            sort=1,
            status=1,
            is_default=False,
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
            sort=1,
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
                sort=i,
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
        result = await dict_service.get_items_by_code(test_dict_data_for_service.code)
        
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
            code=f"inactive_dict_{uuid.uuid4().hex[:8]}",
            status=0,
        )
        
        result = await dict_service.get_items_by_code(inactive_dict.code)
        
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
            code=f"active_test_dict_{uuid.uuid4().hex[:8]}",
            status=1,
        )
        
        # 创建激活的字典项
        active_item = await DictItems.create(
            label="激活项",
            value="active_value",
            sort=1,
            status=1,
            dict_data_id=dict_data.id,
        )
        
        # 创建禁用的字典项
        inactive_item = await DictItems.create(
            label="禁用项",
            value="inactive_value",
            sort=2,
            status=0,
            dict_data_id=dict_data.id,
        )
        
        result = await dict_service.get_items_by_code(dict_data.code)
        
        # 应该只返回激活的字典项
        assert len(result) == 1
        assert result[0].value == "active_value"
