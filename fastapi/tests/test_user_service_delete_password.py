"""用户服务删除和密码测试。"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import BusinessError, NotFound
from app.services.system.user_service import user_service

pytest_plugins = ["user_service_fixtures"]


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

        await user_service.delete(user_to_delete.id)

        # 验证用户已删除
        deleted_user = await Users.get_or_none(id=user_to_delete.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, db):
        """测试删除不存在的用户"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.delete(99999)

        assert "用户不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_self(self, db, test_user_for_service):
        """测试删除当前登录用户"""
        with pytest.raises(BusinessError) as exc_info:
            await user_service.delete(
                test_user_for_service.id,
                current_user=test_user_for_service,
            )

        assert "不能删除当前登录用户" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_hidden_user_returns_not_found(self, db, scoped_user_context):
        """范围外用户按不存在处理，且不得被删除。"""
        hidden_user = scoped_user_context["hidden_user"]

        with pytest.raises(NotFound):
            await user_service.delete(
                hidden_user.id,
                current_user=scoped_user_context["operator"],
            )

        assert await hidden_user.__class__.filter(id=hidden_user.id).exists()


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
        result = await user_service.batch_delete(user_ids)

        assert result.status == "succeeded"
        assert result.success_count == 3
        assert result.failed_count == 0

        # 验证用户已删除
        for user_id in user_ids:
            deleted_user = await Users.get_or_none(id=user_id)
            assert deleted_user is None

    @pytest.mark.asyncio
    async def test_batch_delete_includes_self(self, db, test_user_for_service):
        """测试批量删除包含当前用户"""
        test_user_for_service.is_superuser = True
        result = await user_service.batch_delete(
            [test_user_for_service.id],
            current_user=test_user_for_service,
        )

        assert result.status == "failed"
        assert result.failures[0].error_code == "PROTECTED_OBJECT"
        assert "当前登录用户" in result.failures[0].message

    @pytest.mark.asyncio
    async def test_batch_delete_is_atomic_across_data_scope(self, db, scoped_user_context):
        """批量目标混入范围外用户时全部拒绝，不删除范围内用户。"""
        visible_user = scoped_user_context["visible_user"]
        hidden_user = scoped_user_context["hidden_user"]

        with pytest.raises(NotFound):
            await user_service.batch_delete(
                [visible_user.id, hidden_user.id],
                current_user=scoped_user_context["operator"],
            )

        assert await visible_user.__class__.filter(id=visible_user.id).exists()
        assert await hidden_user.__class__.filter(id=hidden_user.id).exists()


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

    @pytest.mark.asyncio
    async def test_get_options_filters_by_data_scope(self, db, scoped_user_context):
        """用户选项不得泄露范围外用户。"""
        result = await user_service.get_options(
            current_user=scoped_user_context["operator"],
        )

        option_ids = {option["value"] for option in result}
        assert scoped_user_context["visible_user"].id in option_ids
        assert scoped_user_context["hidden_user"].id not in option_ids


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
    async def test_reset_password_revokes_existing_tokens(self, db, test_user_for_service):
        """重置密码前必须撤销该用户已有的 access/refresh token。"""
        with patch(
            "app.services.system.user_services.mutation.token_blacklist_service"
            ".revoke_all_user_tokens",
            new_callable=AsyncMock,
            return_value=True,
        ) as revoke_all:
            await user_service.reset_password(test_user_for_service.id)

        revoke_all.assert_awaited_once_with(
            test_user_for_service.id,
            reason="password_reset",
        )

    @pytest.mark.asyncio
    async def test_reset_password_stops_when_token_revocation_fails(
        self,
        db,
        test_user_for_service,
    ):
        """令牌撤销失败时不得继续写入新密码。"""
        from app.core.security import verify_password
        from app.db.models.oauth import Users

        original_password = (await Users.get(id=test_user_for_service.id)).password
        with patch(
            "app.services.system.user_services.mutation.token_blacklist_service"
            ".revoke_all_user_tokens",
            new_callable=AsyncMock,
            return_value=False,
        ):
            with pytest.raises(BusinessError, match="令牌"):
                await user_service.reset_password(test_user_for_service.id)

        user = await Users.get(id=test_user_for_service.id)
        assert user.password == original_password
        assert verify_password("test123", user.password)

    @pytest.mark.asyncio
    async def test_reset_password_nonexistent_user(self, db):
        """测试重置不存在用户的密码"""
        with pytest.raises(NotFound) as exc_info:
            await user_service.reset_password(99999)

        assert "用户不存在" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_reset_password_hidden_user_returns_not_found(
        self,
        db,
        scoped_user_context,
    ):
        """不得重置范围外用户密码。"""
        with pytest.raises(NotFound):
            await user_service.reset_password(
                scoped_user_context["hidden_user"].id,
                current_user=scoped_user_context["operator"],
            )
