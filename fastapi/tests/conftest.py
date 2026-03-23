"""
Pytest 配置和 fixtures

提供测试数据库初始化、认证等辅助功能。
"""
import asyncio
import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from tortoise import Tortoise


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """初始化测试数据库 (session 级别，所有测试共享)"""
    # 使用内存数据库
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={
            "models": [
                "app.db.models.oauth",
                "app.db.models.system",
            ]
        },
    )
    await Tortoise.generate_schemas()

    # 初始化缓存服务（使用内存缓存）
    from app.core.cache import cache_service
    await cache_service.init()

    yield

    await Tortoise.close_connections()


@pytest_asyncio.fixture(scope="function")
async def db():
    """每个测试函数前的数据库清理"""
    yield
    # 可以在这里清理测试数据


@pytest.fixture(scope="function")
def client() -> TestClient:
    """创建测试客户端"""
    from app.main import app
    return TestClient(app)


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


def get_token_from_response(response) -> str | None:
    """从登录响应中提取 token"""
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 20000 and data.get("data"):
            return data["data"].get("accessToken")
    return None


@pytest_asyncio.fixture(scope="function")
async def test_permissions(db):
    """创建测试权限/菜单"""
    from app.db.models.system import Permissions

    # 创建根目录
    system_catalog = await Permissions.create(
        name="系统管理",
        type="CATALOG",
        sort=1,
    )

    # 创建菜单 - 使用正确的权限标识
    user_menu = await Permissions.create(
        name="用户管理",
        type="MENU",
        route_name="UserManagement",
        route_path="/system/users",
        component="system/users/index",
        sort=1,
        parent=system_catalog,
        perm="system:users:query",
    )
    role_menu = await Permissions.create(
        name="角色管理",
        type="MENU",
        route_name="RoleManagement",
        route_path="/system/roles",
        component="system/roles/index",
        sort=2,
        parent=system_catalog,
        perm="system:roles:query",
    )
    menu_menu = await Permissions.create(
        name="菜单管理",
        type="MENU",
        route_name="MenuManagement",
        route_path="/system/menus",
        component="system/menus/index",
        sort=3,
        parent=system_catalog,
        perm="system:menus:query",
    )
    dept_menu = await Permissions.create(
        name="部门管理",
        type="MENU",
        route_name="DeptManagement",
        route_path="/system/departments",
        component="system/departments/index",
        sort=4,
        parent=system_catalog,
        perm="system:departments:query",
    )
    dict_menu = await Permissions.create(
        name="字典管理",
        type="MENU",
        route_name="DictManagement",
        route_path="/system/dicts",
        component="system/dicts/index",
        sort=5,
        parent=system_catalog,
        perm="system:dicts:query",
    )
    notice_menu = await Permissions.create(
        name="通知公告",
        type="MENU",
        route_name="NoticeManagement",
        route_path="/system/notices",
        component="system/notices/index",
        sort=6,
        parent=system_catalog,
        perm="system:notices:query",
    )
    file_menu = await Permissions.create(
        name="文件管理",
        type="MENU",
        route_name="FileManagement",
        route_path="/system/files",
        component="system/files/index",
        sort=7,
        parent=system_catalog,
        perm="system:files:query",
    )

    # 创建按钮权限
    user_add = await Permissions.create(
        name="用户新增",
        type="BUTTON",
        parent=user_menu,
        perm="system:users:add",
    )
    user_edit = await Permissions.create(
        name="用户编辑",
        type="BUTTON",
        parent=user_menu,
        perm="system:users:edit",
    )
    user_delete = await Permissions.create(
        name="用户删除",
        type="BUTTON",
        parent=user_menu,
        perm="system:users:delete",
    )

    role_add = await Permissions.create(
        name="角色新增",
        type="BUTTON",
        parent=role_menu,
        perm="system:roles:add",
    )
    role_edit = await Permissions.create(
        name="角色编辑",
        type="BUTTON",
        parent=role_menu,
        perm="system:roles:edit",
    )
    role_delete = await Permissions.create(
        name="角色删除",
        type="BUTTON",
        parent=role_menu,
        perm="system:roles:delete",
    )

    menu_add = await Permissions.create(
        name="菜单新增",
        type="BUTTON",
        parent=menu_menu,
        perm="system:menus:add",
    )
    menu_edit = await Permissions.create(
        name="菜单编辑",
        type="BUTTON",
        parent=menu_menu,
        perm="system:menus:edit",
    )
    menu_delete = await Permissions.create(
        name="菜单删除",
        type="BUTTON",
        parent=menu_menu,
        perm="system:menus:delete",
    )

    dept_add = await Permissions.create(
        name="部门新增",
        type="BUTTON",
        parent=dept_menu,
        perm="system:departments:add",
    )
    dept_edit = await Permissions.create(
        name="部门编辑",
        type="BUTTON",
        parent=dept_menu,
        perm="system:departments:edit",
    )
    dept_delete = await Permissions.create(
        name="部门删除",
        type="BUTTON",
        parent=dept_menu,
        perm="system:departments:delete",
    )

    dict_add = await Permissions.create(
        name="字典新增",
        type="BUTTON",
        parent=dict_menu,
        perm="system:dicts:add",
    )
    dict_edit = await Permissions.create(
        name="字典编辑",
        type="BUTTON",
        parent=dict_menu,
        perm="system:dicts:edit",
    )
    dict_delete = await Permissions.create(
        name="字典删除",
        type="BUTTON",
        parent=dict_menu,
        perm="system:dicts:delete",
    )

    notice_add = await Permissions.create(
        name="公告新增",
        type="BUTTON",
        parent=notice_menu,
        perm="system:notices:add",
    )
    notice_edit = await Permissions.create(
        name="公告编辑",
        type="BUTTON",
        parent=notice_menu,
        perm="system:notices:edit",
    )
    notice_delete = await Permissions.create(
        name="公告删除",
        type="BUTTON",
        parent=notice_menu,
        perm="system:notices:delete",
    )
    notice_publish = await Permissions.create(
        name="公告发布",
        type="BUTTON",
        parent=notice_menu,
        perm="system:notices:publish",
    )
    notice_revoke = await Permissions.create(
        name="公告撤销",
        type="BUTTON",
        parent=notice_menu,
        perm="system:notices:revoke",
    )

    # 日志管理菜单和权限
    log_menu = await Permissions.create(
        name="日志管理",
        type="MENU",
        route_name="LogManagement",
        route_path="/system/logs",
        component="system/logs/index",
        sort=8,
        parent=system_catalog,
        perm="system:logs:query",
    )
    log_delete = await Permissions.create(
        name="日志删除",
        type="BUTTON",
        parent=log_menu,
        perm="system:logs:delete",
    )

    return {
        "system_catalog": system_catalog,
        "user_menu": user_menu,
        "role_menu": role_menu,
        "menu_menu": menu_menu,
        "dept_menu": dept_menu,
        "dict_menu": dict_menu,
        "notice_menu": notice_menu,
        "file_menu": file_menu,
        "log_menu": log_menu,
        "user_add": user_add,
        "user_edit": user_edit,
        "user_delete": user_delete,
        "role_add": role_add,
        "role_edit": role_edit,
        "role_delete": role_delete,
        "menu_add": menu_add,
        "menu_edit": menu_edit,
        "menu_delete": menu_delete,
        "dept_add": dept_add,
        "dept_edit": dept_edit,
        "dept_delete": dept_delete,
        "dict_add": dict_add,
        "dict_edit": dict_edit,
        "dict_delete": dict_delete,
        "notice_add": notice_add,
        "notice_edit": notice_edit,
        "notice_delete": notice_delete,
        "notice_publish": notice_publish,
        "notice_revoke": notice_revoke,
        "log_delete": log_delete,
    }


@pytest_asyncio.fixture(scope="function")
async def test_role(db, test_permissions):
    """创建测试角色（带权限）"""
    import uuid

    from app.db.models.system import Roles
    role_name = f"超级管理员_{uuid.uuid4().hex[:6]}"

    role = await Roles.create(
        name=role_name,
        code="admin",
        status=1,
        sort=1,
        remark="测试角色",
    )

    # 关联所有权限
    permissions = [
        test_permissions["user_menu"],
        test_permissions["role_menu"],
        test_permissions["menu_menu"],
        test_permissions["dept_menu"],
        test_permissions["dict_menu"],
        test_permissions["notice_menu"],
        test_permissions["file_menu"],
        test_permissions["log_menu"],
        # 按钮权限
        test_permissions["user_add"],
        test_permissions["user_edit"],
        test_permissions["user_delete"],
        test_permissions["role_add"],
        test_permissions["role_edit"],
        test_permissions["role_delete"],
        test_permissions["menu_add"],
        test_permissions["menu_edit"],
        test_permissions["menu_delete"],
        test_permissions["dept_add"],
        test_permissions["dept_edit"],
        test_permissions["dept_delete"],
        test_permissions["dict_add"],
        test_permissions["dict_edit"],
        test_permissions["dict_delete"],
        test_permissions["notice_add"],
        test_permissions["notice_edit"],
        test_permissions["notice_delete"],
        test_permissions["notice_publish"],
        test_permissions["notice_revoke"],
        test_permissions["log_delete"],
    ]
    await role.permissions.add(*permissions)

    return {"id": role.id, "name": role.name, "code": role.code}


@pytest_asyncio.fixture(scope="function")
async def test_dept(db):
    """创建测试部门"""
    from app.db.models.system import Departments

    dept = await Departments.create(
        name="测试公司",
        sort=1,
        status=1,
        leader="管理员",
        phone="13800138000",
    )
    return {"id": dept.id, "name": dept.name}


@pytest_asyncio.fixture(scope="function")
async def test_user_with_role(db, test_role, test_dept):
    """创建测试用户（带角色和部门）"""
    from passlib.context import CryptContext

    from app.db.models.oauth import Users
    from app.db.models.system import Roles

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("admin123")

    # 使用唯一手机号
    unique_mobile = f"1380013{str(uuid.uuid4())[:4]}"

    user = await Users.create(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        password=hashed_password,
        name="管理员",
        is_active=1,
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        mobile=unique_mobile,
        dept_id=test_dept["id"],
    )

    # 关联角色 - 需要传递角色实例
    role = await Roles.get(id=test_role["id"])
    await user.roles.add(role)

    return {
        "id": user.id,
        "username": user.username,
        "password": "admin123",
        "name": user.name,
    }


@pytest_asyncio.fixture(scope="function")
async def test_user(db) -> dict:
    """创建测试用户（每个测试使用唯一的手机号）"""
    from passlib.context import CryptContext

    from app.db.models.oauth import Users

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("admin123")

    # 使用唯一手机号
    unique_mobile = f"1380013{str(uuid.uuid4())[:4]}"

    user = await Users.create(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        password=hashed_password,
        name="管理员",
        is_active=1,
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        mobile=unique_mobile,
    )

    return {
        "id": user.id,
        "username": user.username,
        "password": "admin123",
        "name": user.name,
    }


@pytest.fixture(scope="function")
async def auth_headers(client: TestClient, test_user_with_role) -> dict:
    """
    获取认证 headers（登录获取 token）
    """
    try:
        response = client.post("/api/v1/oauth/login/", json={
            "username": test_user_with_role["username"],
            "password": test_user_with_role["password"]
        })
        token = get_token_from_response(response)
        if token:
            return {"Authorization": f"Bearer {token}"}
    except Exception:
        pass
    return {}


@pytest.fixture(scope="function")
def auth_client(client: TestClient, auth_headers: dict) -> TestClient | None:
    """
    创建带认证的测试客户端
    """
    if not auth_headers:
        pytest.skip("无法获取认证 token，跳过需要认证的测试")

    test_client = TestClient(client.app)
    test_client.headers.update(auth_headers)
    return test_client
