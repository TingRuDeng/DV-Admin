"""
Django 数据导入关系测试

覆盖导入目标模型的外键、多对多和自引用关系。
"""

import uuid

import pytest

from app.db.models.system import Departments, Permissions, Roles


@pytest.mark.asyncio
async def test_import_permissions(db):
    """权限模型应支持菜单父子关系。"""
    catalog = await Permissions.create(
        name=f"系统管理_{uuid.uuid4().hex[:6]}",
        type="CATALOG",
        sort=1,
    )
    menu = await Permissions.create(
        name=f"用户管理_{uuid.uuid4().hex[:6]}",
        type="MENU",
        route_name="UserManagement",
        route_path="/system/users",
        component="system/user/index",
        sort=1,
        parent_id=catalog.id,
        perm="system:users:query",
    )

    assert catalog.id is not None
    assert menu.id is not None
    assert menu.parent_id == catalog.id


@pytest.mark.asyncio
async def test_import_with_m2m_relationships(db):
    """角色权限多对多关系应可写入并读取。"""
    perm1 = await Permissions.create(
        name=f"权限1_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        perm=f"test:perm1_{uuid.uuid4().hex[:6]}",
    )
    perm2 = await Permissions.create(
        name=f"权限2_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        perm=f"test:perm2_{uuid.uuid4().hex[:6]}",
    )
    role = await Roles.create(
        name=f"测试角色_{uuid.uuid4().hex[:6]}",
        code=f"test_role_{uuid.uuid4().hex[:6]}",
        status=1,
    )

    await role.permissions.add(perm1, perm2)

    role_perms = await role.permissions.all()
    assert len(role_perms) == 2


@pytest.mark.asyncio
async def test_import_with_fk_relationships(db):
    """部门父子外键关系应可写入。"""
    parent_dept = await Departments.create(
        name=f"父部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
    )
    child_dept = await Departments.create(
        name=f"子部门_{uuid.uuid4().hex[:6]}",
        sort=1,
        status=1,
        parent_id=parent_dept.id,
    )

    assert child_dept.parent_id == parent_dept.id


@pytest.mark.asyncio
async def test_import_self_referencing_fk(db):
    """权限自引用父子关系应可写入。"""
    parent_perm = await Permissions.create(
        name=f"父权限_{uuid.uuid4().hex[:6]}",
        type="MENU",
        sort=1,
    )
    child_perm = await Permissions.create(
        name=f"子权限_{uuid.uuid4().hex[:6]}",
        type="BUTTON",
        parent_id=parent_perm.id,
        perm=f"test:child_{uuid.uuid4().hex[:6]}",
    )

    assert child_perm.parent_id == parent_perm.id


@pytest.mark.asyncio
async def test_import_oidc_identity_after_users(db):
    """单点登录身份在用户之后导入，Django 的 user 外键与时间字段映射到 FastAPI 字段。"""
    from app.db.django_import_config import IMPORT_ORDER, MODEL_MAPPING
    from app.db.django_import_state import ImportTasks, ModelImportContext
    from app.db.django_import_writer import import_model_items
    from app.db.models.oauth import OidcIdentity, Users

    assert IMPORT_ORDER.index("oauth.oidcidentity") > IMPORT_ORDER.index("system.users")
    user = await Users.create(username=f"sso_{uuid.uuid4().hex[:8]}", password="!unusable")
    context = ModelImportContext("oauth.oidcidentity", MODEL_MAPPING["oauth.oidcidentity"], ImportTasks())
    await import_model_items(
        context,
        [
            {
                "model": "oauth.oidcidentity",
                "pk": 7,
                "fields": {
                    "create_time": "2026-09-01T08:00:00",
                    "update_time": "2026-09-02T08:00:00",
                    "issuer": "https://idp.example.test",
                    "subject": "subject-7",
                    "user": user.id,
                    "email": "sso@example.com",
                    "last_login_at": None,
                },
            }
        ],
    )

    identity = await OidcIdentity.get(id=7)
    assert identity.user_id == user.id
    assert (identity.issuer, identity.subject, identity.email) == (
        "https://idp.example.test",
        "subject-7",
        "sso@example.com",
    )
    assert identity.last_login_at is None
    assert identity.created_at.date().isoformat() == "2026-09-01"
