"""用户服务写操作测试。"""

import uuid

import pytest

from app.core.exceptions import NotFound, ValidationError
from app.db.models.oauth import Users
from app.db.models.system import Permissions, Roles
from app.schemas.system import UserCreate, UserPartialUpdate, UserUpdate
from app.services.system.user_service import user_service

pytest_plugins = ["user_service_fixtures"]

class TestUserServiceCreate:
    """测试创建用户"""

    async def create_operator(self, permission_codes: tuple[str, ...] = ()) -> Users:
        """创建字段权限测试操作人。"""
        role = await Roles.create(
            name=f"字段写入角色_{uuid.uuid4().hex[:8]}",
            code=f"field_write_{uuid.uuid4().hex[:8]}",
            status=1,
        )
        for code in permission_codes:
            permission = await Permissions.create(name=code, type="BUTTON", perm=code)
            await role.permissions.add(permission)
        operator = await Users.create(
            username=f"operator_{uuid.uuid4().hex[:8]}",
            password="admin123",
            name="字段操作人",
            is_active=1,
        )
        await operator.roles.add(role)
        return operator

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

    @pytest.mark.asyncio
    async def test_create_rejects_sensitive_fields_without_write_permission(self, db):
        """无字段写入权限时，创建用户不得写入手机号和邮箱。"""
        operator = await self.create_operator()
        user_data = UserCreate(
            username=f"sensitive_create_{uuid.uuid4().hex[:8]}",
            name="敏感创建",
            email=f"sensitive_{uuid.uuid4().hex[:8]}@example.com",
            mobile=f"139{uuid.uuid4().hex[:8]}",
            password="test123",
            is_active=1,
        )

        with pytest.raises(ValidationError) as exc_info:
            await user_service.create(user_data, current_user=operator)

        assert "字段写入权限" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_allows_sensitive_fields_with_write_permission(self, db):
        """拥有字段写入权限时，创建用户可以写入手机号和邮箱。"""
        operator = await self.create_operator(("system:users:field:write",))
        mobile = f"139{uuid.uuid4().hex[:8]}"
        email = f"plain_{uuid.uuid4().hex[:8]}@example.com"
        user_data = UserCreate(
            username=f"plain_create_{uuid.uuid4().hex[:8]}",
            name="允许创建",
            email=email,
            mobile=mobile,
            password="test123",
            is_active=1,
        )

        result = await user_service.create(user_data, current_user=operator)

        created = await Users.get(id=result.id)
        assert created.mobile == mobile
        assert created.email == email


class TestUserServiceUpdate:
    """测试更新用户"""

    async def create_operator(self, permission_codes: tuple[str, ...] = ()) -> Users:
        """创建字段权限测试操作人。"""
        role = await Roles.create(
            name=f"字段写入角色_{uuid.uuid4().hex[:8]}",
            code=f"field_write_{uuid.uuid4().hex[:8]}",
            status=1,
        )
        for code in permission_codes:
            permission = await Permissions.create(name=code, type="BUTTON", perm=code)
            await role.permissions.add(permission)
        operator = await Users.create(
            username=f"operator_{uuid.uuid4().hex[:8]}",
            password="admin123",
            name="字段操作人",
            is_active=1,
        )
        await operator.roles.add(role)
        return operator

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

    @pytest.mark.asyncio
    async def test_update_rejects_sensitive_fields_without_write_permission(
        self,
        db,
        test_user_for_service,
    ):
        """无字段写入权限时，更新用户不得写入手机号和邮箱。"""
        operator = await self.create_operator()
        update_data = UserUpdate(
            email=f"sensitive_{uuid.uuid4().hex[:8]}@example.com",
            mobile=f"139{uuid.uuid4().hex[:8]}",
        )

        with pytest.raises(ValidationError) as exc_info:
            await user_service.update(
                test_user_for_service.id,
                update_data,
                current_user=operator,
            )

        assert "字段写入权限" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_allows_sensitive_fields_with_write_permission(
        self,
        db,
        test_user_for_service,
    ):
        """拥有字段写入权限时，更新用户可以写入手机号和邮箱。"""
        operator = await self.create_operator(("system:users:field:write",))
        mobile = f"139{uuid.uuid4().hex[:8]}"
        email = f"plain_{uuid.uuid4().hex[:8]}@example.com"
        update_data = UserUpdate(email=email, mobile=mobile)

        await user_service.update(
            test_user_for_service.id,
            update_data,
            current_user=operator,
        )

        await test_user_for_service.refresh_from_db()
        assert test_user_for_service.mobile == mobile
        assert test_user_for_service.email == email


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
