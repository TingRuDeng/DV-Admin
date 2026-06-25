"""
缓存键模板测试。
"""
from app.core.cache import CacheKeys


class TestCacheKeys:
    """测试缓存键常量。"""

    def test_format_key(self):
        """测试格式化缓存键。"""
        key = CacheKeys.format_key(CacheKeys.DICT_BY_CODE, code="test_code")
        assert key == "dict:code:test_code"

    def test_format_key_user_permissions(self):
        """测试格式化用户权限缓存键。"""
        key = CacheKeys.format_key(CacheKeys.USER_PERMISSIONS, user_id=123)
        assert key == "user:permissions:123"

    def test_format_key_role_detail(self):
        """测试格式化角色详情缓存键。"""
        key = CacheKeys.format_key(CacheKeys.ROLE_DETAIL, role_id=456)
        assert key == "role:detail:456"

    def test_format_key_dept_detail(self):
        """测试格式化部门详情缓存键。"""
        key = CacheKeys.format_key(CacheKeys.DEPT_DETAIL, dept_id=789)
        assert key == "dept:detail:789"

    def test_format_key_menu_detail(self):
        """测试格式化菜单详情缓存键。"""
        key = CacheKeys.format_key(CacheKeys.MENU_DETAIL, menu_id=101)
        assert key == "menu:detail:101"
