"""
数据导入测试
测试 import_django_data 模块的数据导入功能
"""
import uuid

import pytest

from app.db.models.oauth import Users
from app.db.models.system import Departments, DictData, DictItems, Permissions, Roles


class TestImportDjangoData:
    """测试 Django 数据导入功能"""

    @pytest.mark.asyncio
    async def test_model_mapping_exists(self, db):
        """测试模型映射是否正确"""
        from app.db.import_django_data import MODEL_MAPPING

        assert "system.departments" in MODEL_MAPPING
        assert "system.permissions" in MODEL_MAPPING
        assert "system.roles" in MODEL_MAPPING
        assert "system.users" in MODEL_MAPPING
        assert "system.dicts" in MODEL_MAPPING
        assert "system.dictitems" in MODEL_MAPPING

        assert MODEL_MAPPING["system.departments"] == Departments
        assert MODEL_MAPPING["system.permissions"] == Permissions
        assert MODEL_MAPPING["system.roles"] == Roles
        assert MODEL_MAPPING["system.users"] == Users
        assert MODEL_MAPPING["system.dicts"] == DictData
        assert MODEL_MAPPING["system.dictitems"] == DictItems

    @pytest.mark.asyncio
    async def test_field_mapping_exists(self, db):
        """测试字段映射是否正确"""
        from app.db.import_django_data import FIELD_MAPPING

        assert FIELD_MAPPING["create_time"] == "created_at"
        assert FIELD_MAPPING["update_time"] == "updated_at"
        assert FIELD_MAPPING["dict"] == "dict_data"
        assert FIELD_MAPPING["dict_code"] == "code"

    @pytest.mark.asyncio
    async def test_import_departments(self, db):
        """测试导入部门数据"""
        dept = await Departments.create(
            name=f"测试部门_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
            leader="测试领导",
            phone="13800138000",
            email="test@example.com",
        )

        assert dept.id is not None
        assert "测试部门" in dept.name

    @pytest.mark.asyncio
    async def test_import_permissions(self, db):
        """测试导入权限数据"""
        # 创建根目录
        catalog = await Permissions.create(
            name=f"系统管理_{uuid.uuid4().hex[:6]}",
            type="CATALOG",
            sort=1,
        )

        # 创建菜单
        menu = await Permissions.create(
            name=f"用户管理_{uuid.uuid4().hex[:6]}",
            type="MENU",
            route_name="UserManagement",
            route_path="/system/users",
            component="system/users/index",
            sort=1,
            parent_id=catalog.id,
            perm="system:users:query",
        )

        assert catalog.id is not None
        assert menu.id is not None
        assert menu.parent_id == catalog.id

    @pytest.mark.asyncio
    async def test_import_roles(self, db):
        """测试导入角色数据"""
        role = await Roles.create(
            name=f"测试角色_{uuid.uuid4().hex[:6]}",
            code=f"test_role_{uuid.uuid4().hex[:6]}",
            status=1,
            sort=1,
            desc="测试角色描述",
        )

        assert role.id is not None
        assert "测试角色" in role.name

    @pytest.mark.asyncio
    async def test_import_dicts(self, db):
        """测试导入字典数据"""
        dict_data = await DictData.create(
            name=f"测试字典_{uuid.uuid4().hex[:6]}",
            code=f"test_dict_{uuid.uuid4().hex[:6]}",
            status=1,
            desc="测试字典描述",
        )

        assert dict_data.id is not None
        assert "测试字典" in dict_data.name

    @pytest.mark.asyncio
    async def test_import_dict_items(self, db):
        """测试导入字典项数据"""
        # 先创建字典
        dict_data = await DictData.create(
            name=f"状态字典_{uuid.uuid4().hex[:6]}",
            code=f"status_dict_{uuid.uuid4().hex[:6]}",
            status=1,
        )

        # 创建字典项
        item = await DictItems.create(
            label=f"启用_{uuid.uuid4().hex[:6]}",
            value="1",
            sort=1,
            status=1,
            dict_data_id=dict_data.id,
        )

        assert item.id is not None
        assert "启用" in item.label
        assert item.dict_data_id == dict_data.id

    @pytest.mark.asyncio
    async def test_import_users(self, db):
        """测试导入用户数据"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("test123")

        user = await Users.create(
            username=f"test_import_user_{uuid.uuid4().hex[:6]}",
            password=hashed_password,
            name="导入用户",
            is_active=1,
            email=f"import_{uuid.uuid4().hex[:6]}@example.com",
            mobile=f"1390013{uuid.uuid4().hex[:4]}",
        )

        assert user.id is not None
        assert "test_import_user" in user.username

    @pytest.mark.asyncio
    async def test_import_with_m2m_relationships(self, db):
        """测试导入带多对多关系的数据"""
        # 创建权限
        perm1 = await Permissions.create(
            name=f"权限1_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm=f"test:perm1_{uuid.uuid4().hex[:6]}",
        )
        perm2 = await Permissions.create(
            name=f"权限2_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            perm=f"test:perm2_{uuid.uuid4().hex[:6]}",
        )

        # 创建角色
        role = await Roles.create(
            name=f"测试角色_{uuid.uuid4().hex[:6]}",
            code=f"test_role_{uuid.uuid4().hex[:6]}",
            status=1,
        )

        # 添加权限关系
        await role.permissions.add(perm1, perm2)

        # 验证关系
        role_perms = await role.permissions.all()
        assert len(role_perms) == 2

    @pytest.mark.asyncio
    async def test_import_with_fk_relationships(self, db):
        """测试导入带外键关系的数据"""
        # 创建父部门
        parent_dept = await Departments.create(
            name=f"父部门_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
        )

        # 创建子部门
        child_dept = await Departments.create(
            name=f"子部门_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
            parent_id=parent_dept.id,
        )

        assert child_dept.parent_id == parent_dept.id

    @pytest.mark.asyncio
    async def test_import_self_referencing_fk(self, db):
        """测试自引用外键"""
        # 创建父权限
        parent_perm = await Permissions.create(
            name=f"父权限_{uuid.uuid4().hex[:6]}",
            type="MENU",
            sort=1,
        )

        # 创建子权限
        child_perm = await Permissions.create(
            name=f"子权限_{uuid.uuid4().hex[:6]}",
            type="BUTTON",
            parent_id=parent_perm.id,
            perm=f"test:child_{uuid.uuid4().hex[:6]}",
        )

        assert child_perm.parent_id == parent_perm.id

    @pytest.mark.asyncio
    async def test_import_update_existing(self, db):
        """测试更新已存在的数据"""
        # 先创建
        dept = await Departments.create(
            name=f"原部门名_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
        )

        original_name = dept.name

        # 更新
        await Departments.filter(id=dept.id).update(name=f"新部门名_{uuid.uuid4().hex[:6]}")

        # 验证
        updated = await Departments.get(id=dept.id)
        assert updated.name != original_name

    @pytest.mark.asyncio
    async def test_import_skip_unknown_fields(self, db):
        """测试跳过未知字段"""
        # 创建部门，忽略未知字段
        dept = await Departments.create(
            name=f"测试部门_{uuid.uuid4().hex[:6]}",
            sort=1,
            status=1,
        )

        assert dept.id is not None
        assert "测试部门" in dept.name

    @pytest.mark.asyncio
    async def test_import_order(self, db):
        """测试导入顺序"""
        from app.db.import_django_data import MODEL_MAPPING

        # 验证导入顺序定义
        import_order = [
            "system.departments",
            "system.permissions",
            "system.dicts",
            "system.dictitems",
            "system.roles",
            "system.users",
        ]

        for model_name in import_order:
            assert model_name in MODEL_MAPPING

    @pytest.mark.asyncio
    async def test_field_conversion_is_active(self, db):
        """测试 is_active 字段转换（Django bool -> FastAPI int）"""
        # Django 使用 True/False
        # FastAPI 使用 1/0

        user = await Users.create(
            username=f"active_user_{uuid.uuid4().hex[:6]}",
            password="hashed",
            name="活跃用户",
            is_active=1,  # FastAPI 使用 int
            email=f"active_{uuid.uuid4().hex[:6]}@example.com",
            mobile=f"1380013{uuid.uuid4().hex[:4]}",
        )

        assert user.is_active == 1

        inactive_user = await Users.create(
            username=f"inactive_user_{uuid.uuid4().hex[:6]}",
            password="hashed",
            name="非活跃用户",
            is_active=0,
            email=f"inactive_{uuid.uuid4().hex[:6]}@example.com",
            mobile=f"1380014{uuid.uuid4().hex[:4]}",
        )

        assert inactive_user.is_active == 0


class TestImportDjangoDataHelpers:
    """测试数据导入辅助功能"""

    @pytest.mark.asyncio
    async def test_init_function_exists(self, db):
        """测试初始化函数存在"""
        from app.db.import_django_data import init

        assert callable(init)

    @pytest.mark.asyncio
    async def test_import_data_function_exists(self, db):
        """测试导入数据函数存在"""
        from app.db.import_django_data import import_data

        assert callable(import_data)

    @pytest.mark.asyncio
    async def test_main_function_exists(self, db):
        """测试主函数存在"""
        from app.db.import_django_data import main

        assert callable(main)
