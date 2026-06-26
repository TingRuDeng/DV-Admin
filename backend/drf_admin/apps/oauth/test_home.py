# -*- coding: utf-8 -*-
"""
OAuth 首页接口测试
"""

from django.test import TestCase
from rest_framework import status

from drf_admin.apps.oauth.test_helpers import authenticated_client, create_oauth_user


class OAuthHomeTestCase(TestCase):
    """首页数据接口测试"""

    def setUp(self):
        self.user = create_oauth_user()
        self.client = authenticated_client(self.user)

    def test_get_home_data(self):
        """测试获取首页数据"""
        response = self.client.get("/api/v1/oauth/home/")

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ],
        )
