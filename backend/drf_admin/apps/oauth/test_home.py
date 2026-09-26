# -*- coding: utf-8 -*-
"""
OAuth 首页接口测试
"""

from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from drf_admin.apps.oauth.test_helpers import (
    authenticated_client,
    create_oauth_user,
    create_role_with_permission,
)
from drf_admin.apps.oauth.views.home import HomeAPIView
from drf_admin.apps.system.models import Roles
from drf_admin.utils.permissions import RBACPermission

USER_QUERY_PERM = "system:users:query"


class OAuthHomeTestCase(TestCase):
    """首页数据接口测试"""

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.factory = APIRequestFactory()

    def _has_permission(self, user):
        # 测试设置默认 AllowAny，这里直接调用 RBAC 权限类，验证真实部署下的放行规则
        request = self.factory.get("/api/v1/oauth/home/")
        request.user = user
        return RBACPermission().has_permission(request, HomeAPIView())

    def test_user_query_permission_is_required(self):
        allowed_user = create_oauth_user(username="homeviewer")
        allowed_user.roles.add(
            create_role_with_permission(role_code="home-viewer", permission_code=USER_QUERY_PERM)
        )
        denied_user = create_oauth_user(username="homeguest")
        superuser = create_oauth_user(username="homeadmin")
        superuser.is_superuser = True
        superuser.save(update_fields=["is_superuser"])

        self.assertIs(self._has_permission(allowed_user), True)
        self.assertIs(self._has_permission(denied_user), False)
        self.assertIs(self._has_permission(superuser), True)

    def test_user_count_respects_data_scope(self):
        viewer = create_oauth_user(username="selfscope")
        role = create_role_with_permission(role_code="self-scope", permission_code=USER_QUERY_PERM)
        role.data_scope = Roles.DATA_SCOPE_SELF
        role.save(update_fields=["data_scope"])
        viewer.roles.add(role)
        create_oauth_user(username="someone1")
        create_oauth_user(username="someone2")

        response = authenticated_client(viewer).get("/api/v1/oauth/home/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], 20000)
        self.assertEqual(response.data["data"]["users"], 1)
        self.assertIn("visits", response.data["data"])
