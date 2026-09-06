from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from scripts.api_endpoint_contracts import iter_critical_endpoint_contracts

from drf_admin.apps.system.models import Permissions, Roles, Users
from drf_admin.apps.system.views.notices import NoticesViewSet
from drf_admin.apps.system.views.roles import RolesViewSet
from drf_admin.apps.system.views.users import (
    UserExportAPIView,
    UserImportAPIView,
    UserImportTemplateAPIView,
    UsersViewSet,
)
from drf_admin.utils.permissions import RBACPermission


def endpoint_contracts_by_key():
    """按 key 获取共享端点契约，避免权限码断言重复维护。"""
    return {contract.key: contract for contract in iter_critical_endpoint_contracts()}


class RBACPermissionContractTestCase(TestCase):
    """直接验证 RBAC 权限边界，避免测试环境默认 AllowAny 掩盖权限漂移。"""

    def setUp(self):
        cache.clear()
        self.factory = APIRequestFactory()

    def create_user_with_permissions(self, *permission_codes: str) -> Users:
        """创建带指定权限码的用户，用于验证 RBACPermission 判定。"""
        role = Roles.objects.create(name="权限契约角色", code="rbac-contract", status=1, sort=1)
        permissions = [
            Permissions.objects.create(name=code, perm=code, type="BUTTON", sort=index)
            for index, code in enumerate(permission_codes, start=1)
        ]
        role.permissions.add(*permissions)
        user = Users.objects.create_user(
            username="rbac-user",
            password="testpass123",
            name="权限契约用户",
            is_active=1,
        )
        user.roles.add(role)
        return user

    def request_with_user(self, method: str, path: str, user):
        """构造带用户的 Django request，供权限类直接读取。"""
        request = getattr(self.factory, method)(path)
        request.user = user
        return request

    def test_user_with_required_permission_can_access_viewset_action(self):
        """用户拥有 action 所需权限时，RBACPermission 必须放行。"""
        user = self.create_user_with_permissions("system:users:add")
        view = UsersViewSet()
        view.action = "create"

        allowed = RBACPermission().has_permission(
            self.request_with_user("post", "/api/v1/system/users/", user),
            view,
        )

        assert allowed is True

    def test_user_missing_required_permission_is_denied(self):
        """用户缺少 action 所需权限时，RBACPermission 必须拒绝。"""
        user = self.create_user_with_permissions("system:users:query")
        view = UsersViewSet()
        view.action = "create"

        allowed = RBACPermission().has_permission(
            self.request_with_user("post", "/api/v1/system/users/", user),
            view,
        )

        assert allowed is False

    def test_role_permission_change_invalidates_assigned_user_cache(self):
        """角色撤权后必须清除关联用户的权限缓存。"""
        user = self.create_user_with_permissions("system:users:query")
        role = user.roles.get()

        assert "system:users:query" in RBACPermission.get_user_permissions(user)

        role.permissions.clear()

        assert "system:users:query" not in RBACPermission.get_user_permissions(user)

    def test_permission_delete_invalidates_assigned_user_cache(self):
        """权限对象被删除时也必须清除缓存，级联删除不会触发 m2m_changed。"""
        permission_code = "system:users:query"
        user = self.create_user_with_permissions(permission_code)
        permission = Permissions.objects.get(perm=permission_code)

        assert permission_code in RBACPermission.get_user_permissions(user)

        permission.delete()

        assert permission_code not in RBACPermission.get_user_permissions(user)

    def test_role_delete_invalidates_assigned_user_cache(self):
        """角色删除后必须清除关联用户缓存，避免级联删除绕过 m2m_changed。"""
        permission_code = "system:roles:delete-cache"
        user = self.create_user_with_permissions(permission_code)
        role = user.roles.get()

        assert permission_code in RBACPermission.get_user_permissions(user)

        role.delete()

        assert permission_code not in RBACPermission.get_user_permissions(user)

    def test_permission_update_invalidates_assigned_user_cache(self):
        """权限码修改后必须清除关联用户缓存。"""
        old_code = "system:permission:old-code"
        new_code = "system:permission:new-code"
        user = self.create_user_with_permissions(old_code)
        permission = Permissions.objects.get(perm=old_code)

        assert old_code in RBACPermission.get_user_permissions(user)

        permission.perm = new_code
        permission.save(update_fields=["perm"])

        permissions = RBACPermission.get_user_permissions(user)
        assert old_code not in permissions
        assert new_code in permissions

    def test_operation_without_required_permissions_is_denied(self):
        """非白名单接口没有权限声明时必须拒绝，避免新增接口默认裸奔。"""
        user = self.create_user_with_permissions("system:users:add")
        view = SimpleNamespace(action="custom", required_permissions={})

        allowed = RBACPermission().has_permission(
            self.request_with_user("get", "/api/v1/system/users/custom/", user),
            view,
        )

        assert allowed is False

    def test_white_list_path_is_allowed_without_authentication(self):
        """白名单路径必须先于 RBAC 权限判断放行。"""
        view = SimpleNamespace(action="login", required_permissions={})

        allowed = RBACPermission().has_permission(
            self.request_with_user("post", "/api/v1/oauth/login/", AnonymousUser()),
            view,
        )

        assert allowed is True

    def test_users_viewset_permissions_match_endpoint_catalog(self):
        """用户写操作权限码必须和共享端点契约一致。"""
        contracts = endpoint_contracts_by_key()
        view = UsersViewSet()

        assert view.required_permissions["create"] == list(contracts["users_create"].permissions)
        assert view.required_permissions["update"] == list(contracts["users_update"].permissions)
        assert view.required_permissions["multiple_delete"] == list(contracts["users_delete"].permissions)
        assert view.required_permissions["retry_batch_delete"] == list(
            contracts["users_delete_retry"].permissions
        )

    def test_role_and_notice_retry_permissions_match_endpoint_catalog(self):
        """角色和通知逐条重试必须复用各自批量删除权限。"""
        contracts = endpoint_contracts_by_key()

        assert RolesViewSet().required_permissions["retry_batch_delete"] == list(
            contracts["roles_delete_retry"].permissions
        )
        assert NoticesViewSet().required_permissions["retry_batch_delete"] == list(
            contracts["notices_delete_retry"].permissions
        )

    def test_user_import_export_permissions_match_endpoint_catalog(self):
        """Django 特殊入口必须使用导入导出专用权限。"""
        contracts = endpoint_contracts_by_key()

        assert UserImportTemplateAPIView().required_permissions["get"] == list(
            contracts["users_template"].permissions
        )
        assert UserImportAPIView().required_permissions["post"] == list(
            contracts["users_import"].permissions
        )
        assert UserExportAPIView().required_permissions["post"] == list(
            contracts["users_export"].permissions
        )
