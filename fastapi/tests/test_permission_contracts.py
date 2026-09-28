"""FastAPI 权限码契约测试。"""

from collections.abc import Callable
from inspect import signature

from fastapi.params import Depends

from app.api.deps import PermissionChecker
from app.api.v1.system import menus, users


def _required_perms(endpoint: Callable) -> set[str]:
    """读取路由函数声明的权限依赖，避免权限码与前端/Django 契约漂移。"""
    default = signature(endpoint).parameters["current_user"].default
    assert isinstance(default, Depends)
    checker = default.dependency
    assert isinstance(checker, PermissionChecker)
    return checker.required_perms


def test_menu_endpoints_use_permissions_resource_perms():
    """菜单管理接口必须沿用 Django 权限模型的 permissions 资源名。"""
    assert _required_perms(menus.get_menus) == {"system:permissions:query"}
    assert _required_perms(menus.get_menu_options) == {"system:permissions:query"}
    assert _required_perms(menus.get_permissions) == {"system:permissions:query"}
    assert _required_perms(menus.get_menu) == {"system:permissions:query"}
    assert _required_perms(menus.create_menu) == {"system:permissions:add"}
    assert _required_perms(menus.update_menu) == {"system:permissions:edit"}
    assert _required_perms(menus.delete_menu) == {"system:permissions:delete"}




def test_user_special_actions_use_dedicated_perms():
    """用户导入、导出、重置密码必须使用细分按钮权限。"""
    assert _required_perms(users.reset_user_password) == {"system:users:password:reset"}
    assert _required_perms(users.get_import_template) == {"system:users:import"}
    assert _required_perms(users.export_users) == {"system:users:export"}
    assert _required_perms(users.import_users) == {"system:users:import"}
