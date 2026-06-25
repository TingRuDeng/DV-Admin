"""
缓存键模板。
"""


class CacheKeys:
    """缓存键常量。"""

    DICT_BY_CODE = "dict:code:{code}"
    DICT_ALL = "dict:all"
    USER_PERMISSIONS = "user:permissions:{user_id}"
    USER_MENUS = "user:menus:{user_id}"
    ROLE_PERMISSIONS = "role:permissions:{role_id}"
    ROLE_OPTIONS = "role:options"
    ROLE_DETAIL = "role:detail:{role_id}"
    DEPT_TREE = "dept:tree"
    DEPT_DETAIL = "dept:detail:{dept_id}"
    MENU_TREE = "menu:tree"
    MENU_DETAIL = "menu:detail:{menu_id}"

    @staticmethod
    def format_key(template: str, **kwargs) -> str:
        """格式化缓存键。"""
        return template.format(**kwargs)
