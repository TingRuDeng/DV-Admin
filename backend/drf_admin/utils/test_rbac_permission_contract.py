from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from scripts.api_endpoint_contracts import iter_critical_endpoint_contracts

from drf_admin.apps.system.models import Permissions, Roles, Users
from drf_admin.apps.system.views.users import UsersViewSet
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
