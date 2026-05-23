"""
共享路由契约静态测试
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(rel: str) -> str:
    """读取仓库文本文件。"""
    return (ROOT / rel).read_text(encoding="utf-8")


def test_user_reset_password_route_is_aligned():
    django_urls = read_text("backend/drf_admin/apps/system/urls.py")
    fastapi_users = read_text("fastapi/app/api/v1/system/users.py")
    frontend_user_api = read_text("frontend/src/api/system/user-api.ts")
    api_docs = read_text("docs/API_ENDPOINTS.md")

    assert "users/<int:pk>/password/reset/" in django_urls
    assert '/{user_id}/password/reset/' in fastapi_users
    assert '${USER_BASE_URL}/${id}/password/reset/' in frontend_user_api
    assert "/api/v1/system/users/{id}/password/reset/" in api_docs


def test_role_menu_ids_route_is_aligned():
    django_urls = read_text("backend/drf_admin/apps/system/urls.py")
    fastapi_roles = read_text("fastapi/app/api/v1/system/roles.py")
    frontend_role_api = read_text("frontend/src/api/system/role-api.ts")
    api_docs = read_text("docs/API_ENDPOINTS.md")

    assert "roles/<int:pk>/menu-ids/" in django_urls
    assert '/{role_id}/menu-ids/' in fastapi_roles
    assert '${ROLE_BASE_URL}/${roleId}/menu-ids/' in frontend_role_api
    assert "/api/v1/system/roles/{id}/menu-ids/" in api_docs


def test_information_avatar_route_is_documented_as_current_path():
    fastapi_profile = read_text("fastapi/app/api/v1/information/profile.py")
    frontend_information_api = read_text("frontend/src/api/information-api.ts")
    api_docs = read_text("docs/API_ENDPOINTS.md")

    assert '"/change-avatar/"' in fastapi_profile
    assert '${INFO_BASE_URL}/change-avatar/' in frontend_information_api
    assert "/api/v1/information/change-avatar/" in api_docs
