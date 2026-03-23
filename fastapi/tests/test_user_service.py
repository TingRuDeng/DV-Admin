"""
用户服务层测试
测试 UserService 的所有方法，包括 CRUD 操作、边界条件和异常情况
"""
import uuid
from io import BytesIO

import pytest
import pytest_asyncio

from app.core.exceptions import BusinessError, NotFound, ValidationError
from app.schemas.system import UserCreate, UserPartialUpdate, UserUpdate
from app.services.system.user_service import user_service


@pytest_asyncio.fixture
async def test_dept_for_service(db):
    """创建测试部门"""
    from app.db.models.system import Departments

    dept = await Departments.create(
        name=f"测试部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )
    return dept


@pytest_asyncio.fixture
async def test_role_for_service(db):
    """创建测试角色"""
    from app.db.models.system import Roles

    role = await Roles.create(
        name=f"测试角色_{uuid.uuid4().hex[:6]}",
        code=f"test_role_{uuid.uuid4().hex[:6]}",
        status=1,
        sort=1,
    )
    return role


@pytest_asyncio.fixture
async def test_user_for_service(db, test_dept_for_service):
    """创建测试用户"""
    from app.core.security import get_password_hash
    from app.db.models.oauth import Users

    user = await Users.create(
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        password=get_password_hash("test123"),
        name="测试用户",
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        mobile=f"138{uuid.uuid4().hex[:8]}",
        is_active=1,
        dept_id=test_dept_for_service.id,
    )
    return user


class TestUserServiceGetPage:
    """测试用户分页查询"""

    @pytest.mark.asyncio
    async def test_get_page_basic(self, db, test_user_for_service):
        """测试基本分页查询"""
        result = await user_service.get_page(page=1, page_size=10)

        assert result.total >= 1
        assert len(result.list) >= 1
        assert result.page == 1
        assert result.page_size == 10

    @pytest.mark.asyncio
    async def test_get_page_with_search(self, db, test_user_for_service):
        """测试带搜索条件的分页查询"""
        # 按用户名搜索
        result = await user_service.get_page(
            page=1,
            page_size=10,
            search=test_user_for_service.username[:10]
        )
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_get_page_with_status_filter(self, db, test_user_for_service):
        """测试按状态过滤"""
        result = await user_service.get_page(page=1, page_size=10, is_active=1)

        for user in result.list:
            assert user.is_active == 1

    @pytest.mark.asyncio
    async def test_get_page_with_dept_filter(self, db, test_user_for_service, test_dept_for_service):
        """测试按部门过滤"""
        result = await user_service.get_page(
            page=1,
            page_size=10,
            dept_id=test_dept_for_service.id
        )

        for user in result.list:
            assert user.dept_id == test_dept_for_service.id

    @pytest.mark.asyncio
    async def test_get_page_empty_result(self, db):
        """测试空结果"""
        result = await user_service.get_page(
            page=1,
            page_size=10,
            search="nonexistent_user_12345"
        )

        assert result.total == 0
        assert len(result.list) == 0


class TestUserServiceGet:
    """测试获取用户详情"""

    @pytest.mark.asyncio
    async def test_get_existing_user(self, db, test_user_for_service):
        """测试获取存在的用户"""
        result = await user_service.get(test_user_for_service.id)

        assert result.id == test_user_for_service.id
        assert result.username == test_user_for_service.username
        assert result.name == test_user_for_service.name

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, db):
        """测试获取不存在的用户"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.get(99999)

        assert "用户不存在" in str(exc_info.value)


class TestUserServiceGetForm:
    """测试获取用户表单详情"""

    @pytest.mark.asyncio
    async def test_get_form_existing_user(self, db, test_user_for_service):
        """测试获取存在的用户表单"""
        result = await user_service.get_form(test_user_for_service.id)

        assert result.id == test_user_for_service.id
        assert result.username == test_user_for_service.username
        assert hasattr(result, 'roles')

    @pytest.mark.asyncio
    async def test_get_form_nonexistent_user(self, db):
        """测试获取不存在的用户表单"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.get_form(99999)

        assert "用户不存在" in str(exc_info.value)


class TestUserServiceCreate:
    """测试创建用户"""

    @pytest.mark.asyncio
    async def test_create_user_basic(self, db, test_dept_for_service):
        """测试基本创建用户"""
        unique_username = f"newuser_{uuid.uuid4().hex[:8]}"
        user_data = UserCreate(
            username=unique_username,
            name="新用户",
            email=f"newuser_{uuid.uuid4().hex[:8]}@example.com",
            mobile=f"139{uuid.uuid4().hex[:8]}",
            password="test123",
            is_active=1,
            dept_id=test_dept_for_service.id,
        )

        result = await user_service.create(user_data)

        assert result.username == unique_username
        assert result.name == "新用户"
        assert result.is_active == 1

    @pytest.mark.asyncio
    async def test_create_user_with_roles(self, db, test_dept_for_service, test_role_for_service):
        """测试创建用户并关联角色"""
        unique_username = f"newuser_{uuid.uuid4().hex[:8]}"
        user_data = UserCreate(
            username=unique_username,
            name="新用户",
            email=f"newuser_{uuid.uuid4().hex[:8]}@example.com",
            mobile=f"139{uuid.uuid4().hex[:8]}",
            password="test123",
            is_active=1,
            dept_id=test_dept_for_service.id,
            role_ids=[test_role_for_service.id],
        )

        result = await user_service.create(user_data)

        assert result.username == unique_username
        # 验证角色关联
        from app.db.models.oauth import Users
        user = await Users.get(id=result.id)
        await user.fetch_related("roles")
        assert len(user.roles) == 1

    @pytest.mark.asyncio
    async def test_create_duplicate_username(self, db, test_user_for_service):
        """测试创建重复用户名"""
        user_data = UserCreate(
            username=test_user_for_service.username,
            name="重复用户",
            email=f"dup_{uuid.uuid4().hex[:8]}@example.com",
            mobile=f"137{uuid.uuid4().hex[:8]}",
            password="test123",
            is_active=1,
        )

        with pytest.raises(ValidationError) as exc_info:
            await user_service.create(user_data)

        assert "用户名已存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_duplicate_mobile(self, db, test_user_for_service):
        """测试创建重复手机号"""
        user_data = UserCreate(
            username=f"newuser_{uuid.uuid4().hex[:8]}",
            name="重复手机号",
            email=f"dup_{uuid.uuid4().hex[:8]}@example.com",
            mobile=test_user_for_service.mobile,
            password="test123",
            is_active=1,
        )

        with pytest.raises(ValidationError) as exc_info:
            await user_service.create(user_data)

        assert "手机号已存在" in str(exc_info.value)


class TestUserServiceUpdate:
    """测试更新用户"""

    @pytest.mark.asyncio
    async def test_update_user_basic(self, db, test_user_for_service):
        """测试基本更新用户"""
        update_data = UserUpdate(
            name="更新后的名字",
            email=f"updated_{uuid.uuid4().hex[:8]}@example.com",
        )

        result = await user_service.update(test_user_for_service.id, update_data)

        assert result.name == "更新后的名字"

    @pytest.mark.asyncio
    async def test_update_user_with_roles(self, db, test_user_for_service, test_role_for_service):
        """测试更新用户角色"""
        update_data = UserUpdate(
            role_ids=[test_role_for_service.id]
        )

        result = await user_service.update(test_user_for_service.id, update_data)

        # 验证角色更新
        from app.db.models.oauth import Users
        user = await Users.get(id=test_user_for_service.id)
        await user.fetch_related("roles")
        assert len(user.roles) == 1

    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, db):
        """测试更新不存在的用户"""
        update_data = UserUpdate(name="更新名字")

        with pytest.raises(NotFound) as exc_info:
            await user_service.update(99999, update_data)

        assert "用户不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_duplicate_mobile(self, db, test_user_for_service, test_dept_for_service):
        """测试更新为已存在的手机号"""
        # 创建另一个用户
        from app.core.security import get_password_hash
        from app.db.models.oauth import Users

        other_user = await Users.create(
            username=f"other_{uuid.uuid4().hex[:8]}",
            password=get_password_hash("test123"),
            name="其他用户",
            mobile=f"158{uuid.uuid4().hex[:8]}",
            is_active=1,
        )

        # 尝试更新为其他用户的手机号
        update_data = UserUpdate(mobile=other_user.mobile)

        with pytest.raises(ValidationError) as exc_info:
            await user_service.update(test_user_for_service.id, update_data)

        assert "手机号已存在" in str(exc_info.value)


class TestUserServicePartialUpdate:
    """测试局部更新用户"""

    @pytest.mark.asyncio
    async def test_partial_update_status(self, db, test_user_for_service):
        """测试更新用户状态"""
        update_data = UserPartialUpdate(is_active=0)

        result = await user_service.partial_update(test_user_for_service.id, update_data)

        assert result.is_active == 0

    @pytest.mark.asyncio
    async def test_partial_update_nonexistent_user(self, db):
        """测试更新不存在的用户状态"""
        update_data = UserPartialUpdate(is_active=0)

        with pytest.raises(NotFound) as exc_info:
            await user_service.partial_update(99999, update_data)

        assert "用户不存在" in str(exc_info.value)


class TestUserServiceDelete:
    """测试删除用户"""

    @pytest.mark.asyncio
    async def test_delete_user(self, db, test_dept_for_service):
        """测试删除用户"""
        from app.core.security import get_password_hash
        from app.db.models.oauth import Users

        # 创建一个新用户用于删除
        user_to_delete = await Users.create(
            username=f"delete_{uuid.uuid4().hex[:8]}",
            password=get_password_hash("test123"),
            name="待删除用户",
            mobile=f"157{uuid.uuid4().hex[:8]}",
            is_active=1,
            dept_id=test_dept_for_service.id,
        )

        # 使用不同的用户ID作为当前用户
        await user_service.delete(user_to_delete.id, current_user_id=99999)

        # 验证用户已删除
        deleted_user = await Users.get_or_none(id=user_to_delete.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, db):
        """测试删除不存在的用户"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.delete(99999, current_user_id=88888)

        assert "用户不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_self(self, db, test_user_for_service):
        """测试删除当前登录用户"""
        with pytest.raises(BusinessError) as exc_info:
            await user_service.delete(test_user_for_service.id, current_user_id=test_user_for_service.id)

        assert "不能删除当前登录用户" in str(exc_info.value)


class TestUserServiceBatchDelete:
    """测试批量删除用户"""

    @pytest.mark.asyncio
    async def test_batch_delete_users(self, db, test_dept_for_service):
        """测试批量删除用户"""
        from app.core.security import get_password_hash
        from app.db.models.oauth import Users

        # 创建多个用户
        user_ids = []
        for i in range(3):
            user = await Users.create(
                username=f"batch_{i}_{uuid.uuid4().hex[:8]}",
                password=get_password_hash("test123"),
                name=f"批量用户{i}",
                mobile=f"156{uuid.uuid4().hex[:8]}",
                is_active=1,
                dept_id=test_dept_for_service.id,
            )
            user_ids.append(user.id)

        # 批量删除
        await user_service.batch_delete(user_ids, current_user_id=99999)

        # 验证用户已删除
        for user_id in user_ids:
            deleted_user = await Users.get_or_none(id=user_id)
            assert deleted_user is None

    @pytest.mark.asyncio
    async def test_batch_delete_includes_self(self, db, test_user_for_service):
        """测试批量删除包含当前用户"""
        with pytest.raises(BusinessError) as exc_info:
            await user_service.batch_delete([test_user_for_service.id, 99999], current_user_id=test_user_for_service.id)

        assert "不能删除当前登录用户" in str(exc_info.value)


class TestUserServiceGetOptions:
    """测试获取用户选项"""

    @pytest.mark.asyncio
    async def test_get_options(self, db, test_user_for_service):
        """测试获取用户下拉选项"""
        result = await user_service.get_options()

        assert isinstance(result, list)
        assert len(result) >= 1

        # 验证格式
        for option in result:
            assert "value" in option
            assert "label" in option

    @pytest.mark.asyncio
    async def test_get_options_only_active(self, db, test_dept_for_service):
        """测试只返回激活状态的用户"""
        from app.core.security import get_password_hash
        from app.db.models.oauth import Users

        # 创建一个禁用的用户
        inactive_user = await Users.create(
            username=f"inactive_{uuid.uuid4().hex[:8]}",
            password=get_password_hash("test123"),
            name="禁用用户",
            mobile=f"155{uuid.uuid4().hex[:8]}",
            is_active=0,
            dept_id=test_dept_for_service.id,
        )

        result = await user_service.get_options()

        # 验证禁用用户不在选项中
        option_ids = [opt["value"] for opt in result]
        assert inactive_user.id not in option_ids


class TestUserServiceResetPassword:
    """测试重置密码"""

    @pytest.mark.asyncio
    async def test_reset_password(self, db, test_user_for_service):
        """测试重置密码"""

        await user_service.reset_password(test_user_for_service.id)

        # 验证密码已更新（无法直接验证密码值，但可以验证没有异常）
        from app.db.models.oauth import Users
        user = await Users.get(id=test_user_for_service.id)
        assert user is not None

    @pytest.mark.asyncio
    async def test_reset_password_nonexistent_user(self, db):
        """测试重置不存在用户的密码"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.reset_password(99999)

        assert "用户不存在" in str(exc_info.value)


class TestUserServiceImportExport:
    """测试用户导入导出"""

    @pytest.mark.asyncio
    async def test_get_import_template(self, db):
        """测试获取导入模板"""
        result = await user_service.get_import_template()

        assert "filename" in result
        assert "content" in result
        assert result["filename"].endswith(".xlsx")

    @pytest.mark.asyncio
    async def test_export_users(self, db, test_user_for_service):
        """测试导出用户"""
        result = await user_service.export_users()

        assert "filename" in result
        assert "content" in result
        assert result["filename"].endswith(".csv")

    @pytest.mark.asyncio
    async def test_import_users_valid(self, db, test_dept_for_service, test_role_for_service):
        """测试导入有效用户"""
        from io import BytesIO

        import openpyxl

        # 创建测试 Excel 文件
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["用户名*", "姓名", "邮箱", "手机号", "性别", "部门ID", "角色ID(多个用逗号分隔)"])
        ws.append([
            f"import_{uuid.uuid4().hex[:8]}",
            "导入用户",
            f"import_{uuid.uuid4().hex[:8]}@example.com",
            f"159{uuid.uuid4().hex[:8]}",
            "1",
            str(test_dept_for_service.id),
            str(test_role_for_service.id)
        ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        result = await user_service.import_users(buffer, dept_id=test_dept_for_service.id)

        assert result.valid_count >= 1
        assert result.invalid_count == 0

    @pytest.mark.asyncio
    async def test_import_users_invalid_file(self, db):
        """测试导入无效文件"""
        # 创建无效的文件内容
        buffer = BytesIO(b"invalid content")

        with pytest.raises(ValidationError):
            await user_service.import_users(buffer)
