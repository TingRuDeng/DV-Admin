"""
OAuth schema tests.
"""

from app.schemas.oauth import UserInfo, UserProfile


class TestUserSchemas:
    """Test oauth user schemas."""

    def test_user_info_accepts_roles_json_string(self):
        user_info = UserInfo(
            id=1,
            username="admin",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            roles='["admin"]',
        )

        assert user_info.roles == '["admin"]'

    def test_user_profile_accepts_roles_list(self):
        user_profile = UserProfile(
            id=1,
            username="admin",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            roles=[{"id": 1, "name": "管理员", "code": "admin"}],
        )

        assert user_profile.roles == [{"id": 1, "name": "管理员", "code": "admin"}]
