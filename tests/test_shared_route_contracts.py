"""
共享路由契约静态测试
"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(rel: str) -> str:
    """读取仓库文本文件。"""
    return (ROOT / rel).read_text(encoding="utf-8")


class SharedRouteContractsTestCase(unittest.TestCase):
    def test_user_reset_password_route_is_aligned(self):
        django_urls = read_text("backend/drf_admin/apps/system/urls.py")
        fastapi_users = read_text(
            "fastapi/app/api/v1/system/user_routes/password.py"
        )
        frontend_user_api = read_text("frontend/src/api/system/user-api.ts")
        api_docs = read_text("docs/API_ENDPOINTS.md")

        self.assertIn("users/<int:pk>/password/reset/", django_urls)
        self.assertIn('/{user_id}/password/reset/', fastapi_users)
        self.assertIn('${USER_BASE_URL}/${id}/password/reset/', frontend_user_api)
        self.assertIn("/api/v1/system/users/{id}/password/reset/", api_docs)

    def test_role_menu_ids_route_is_aligned(self):
        django_urls = read_text("backend/drf_admin/apps/system/urls.py")
        fastapi_roles = read_text("fastapi/app/api/v1/system/roles.py")
        frontend_role_api = read_text("frontend/src/api/system/role-api.ts")
        api_docs = read_text("docs/API_ENDPOINTS.md")

        self.assertIn("roles/<int:pk>/menu-ids/", django_urls)
        self.assertIn('/{role_id}/menu-ids/', fastapi_roles)
        self.assertIn('${ROLE_BASE_URL}/${roleId}/menu-ids/', frontend_role_api)
        self.assertIn("/api/v1/system/roles/{id}/menu-ids/", api_docs)

    def test_information_avatar_route_is_documented_as_current_path(self):
        fastapi_profile = read_text("fastapi/app/api/v1/information/profile.py")
        frontend_information_api = read_text("frontend/src/api/information-api.ts")
        api_docs = read_text("docs/API_ENDPOINTS.md")

        self.assertIn('"/change-avatar/"', fastapi_profile)
        self.assertIn('${INFO_BASE_URL}/change-avatar/', frontend_information_api)
        self.assertIn("/api/v1/information/change-avatar/", api_docs)


if __name__ == "__main__":
    unittest.main()
