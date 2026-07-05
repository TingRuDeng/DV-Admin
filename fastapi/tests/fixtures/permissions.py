"""测试权限种子构造工具。"""

MENU_SPECS = (
    ("user_menu", "用户管理", "UserManagement", "/system/users", "system/user/index", 1, "system:users:query"),
    ("role_menu", "角色管理", "RoleManagement", "/system/roles", "system/role/index", 2, "system:roles:query"),
    ("menu_menu", "菜单管理", "MenuManagement", "/system/menus", "system/menu/index", 3, "system:permissions:query"),
    ("dept_menu", "部门管理", "DeptManagement", "/system/departments", "system/dept/index", 4, "system:departments:query"),
    ("dict_menu", "字典管理", "DictManagement", "/system/dicts", "system/dict/index", 5, "system:dicts:query"),
    ("notice_menu", "通知公告", "NoticeManagement", "/system/notices", "system/notice/index", 6, "system:notices:query"),
    ("dict_item_menu", "字典项", "DictData", "/system/dict-item", "system/dict/dict-item", 7, "system:dictitems:query"),
    ("log_menu", "日志管理", "LogManagement", "/system/logs", "system/log/index", 8, "system:logs:query"),
)

BUTTON_SPECS = (
    ("user_add", "用户新增", "user_menu", "system:users:add"),
    ("user_edit", "用户编辑", "user_menu", "system:users:edit"),
    ("user_delete", "用户删除", "user_menu", "system:users:delete"),
    ("user_reset_password", "重置密码", "user_menu", "system:users:password:reset"),
    ("user_import", "用户导入", "user_menu", "system:users:import"),
    ("user_export", "用户导出", "user_menu", "system:users:export"),
    ("user_field_write", "用户敏感字段写入", "user_menu", "system:users:field:write"),
    ("role_add", "角色新增", "role_menu", "system:roles:add"),
    ("role_edit", "角色编辑", "role_menu", "system:roles:edit"),
    ("role_delete", "角色删除", "role_menu", "system:roles:delete"),
    ("menu_add", "菜单新增", "menu_menu", "system:permissions:add"),
    ("menu_edit", "菜单编辑", "menu_menu", "system:permissions:edit"),
    ("menu_delete", "菜单删除", "menu_menu", "system:permissions:delete"),
    ("dept_add", "部门新增", "dept_menu", "system:departments:add"),
    ("dept_edit", "部门编辑", "dept_menu", "system:departments:edit"),
    ("dept_delete", "部门删除", "dept_menu", "system:departments:delete"),
    ("dict_add", "字典新增", "dict_menu", "system:dicts:add"),
    ("dict_edit", "字典编辑", "dict_menu", "system:dicts:edit"),
    ("dict_delete", "字典删除", "dict_menu", "system:dicts:delete"),
    ("dict_item_add", "字典项新增", "dict_item_menu", "system:dictitems:add"),
    ("dict_item_edit", "字典项编辑", "dict_item_menu", "system:dictitems:edit"),
    ("dict_item_delete", "字典项删除", "dict_item_menu", "system:dictitems:delete"),
    ("notice_add", "公告新增", "notice_menu", "system:notices:add"),
    ("notice_edit", "公告编辑", "notice_menu", "system:notices:edit"),
    ("notice_delete", "公告删除", "notice_menu", "system:notices:delete"),
    ("notice_publish", "公告发布", "notice_menu", "system:notices:publish"),
    ("notice_revoke", "公告撤销", "notice_menu", "system:notices:revoke"),
    ("log_delete", "日志删除", "log_menu", "system:logs:delete"),
)

ROLE_PERMISSION_KEYS = tuple(key for key, *_ in MENU_SPECS) + tuple(key for key, *_ in BUTTON_SPECS)


async def _create_menu_permissions(Permissions, records: dict) -> None:
    """创建菜单权限，并保留 key 到模型实例的映射。"""
    for key, name, route_name, route_path, component, sort, perm in MENU_SPECS:
        records[key] = await Permissions.create(
            name=name,
            type="MENU",
            route_name=route_name,
            route_path=route_path,
            component=component,
            sort=sort,
            parent=records["system_catalog"],
            perm=perm,
        )


async def _create_button_permissions(Permissions, records: dict) -> None:
    """创建按钮权限，父级来自已创建的菜单权限。"""
    for key, name, parent_key, perm in BUTTON_SPECS:
        records[key] = await Permissions.create(
            name=name,
            type="BUTTON",
            parent=records[parent_key],
            perm=perm,
        )


async def create_test_permissions() -> dict:
    """创建完整测试权限树。"""
    from app.db.models.system import Permissions

    records = {
        "system_catalog": await Permissions.create(
            name="系统管理",
            type="CATALOG",
            sort=1,
        )
    }
    await _create_menu_permissions(Permissions, records)
    await _create_button_permissions(Permissions, records)
    return records


def role_permission_instances(records: dict) -> list:
    """按稳定顺序返回测试角色需要绑定的全部权限实例。"""
    return [records[key] for key in ROLE_PERMISSION_KEYS]
