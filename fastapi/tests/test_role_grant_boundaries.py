"""Runtime guards for delegated administration, independent of sort values."""

import httpx
import pytest
import pytest_asyncio

from app.api.deps import get_current_user
from app.db.models.oauth import Users
from app.db.models.system import Departments, Permissions, Roles
from app.main import create_app
from app.schemas.system import RoleUpdate
from app.services.system.role_service import role_service
from app.services.system.user_service import user_service


@pytest_asyncio.fixture
async def grants(db):
    own = await Departments.create(name="Owned")
    shared = await Departments.create(name="Shared")
    hidden = await Departments.create(name="Hidden", parent_id=shared.id)
    codes = ("system:users:add", "system:users:edit", "system:users:import", "system:roles:add", "system:roles:edit", "system:roles:delete")
    permissions = [await Permissions.create(name=code, type="BUTTON", perm=code) for code in codes]
    dangerous = await Permissions.create(name="Outside", type="BUTTON", perm="outside:write")
    actor_role = await Roles.create(name="Delegated", code="delegated", data_scope=5, sort=999)
    await actor_role.data_depts.add(own, shared)
    await actor_role.permissions.add(*permissions)
    actor = await Users.create(username="delegate", password="!", dept_id=own.id)
    await actor.roles.add(actor_role)
    low = await Roles.create(name="Scoped", code="scoped", data_scope=2, sort=0)
    await low.permissions.add(permissions[1])
    high = await Roles.create(name="Outside role", code="outside", data_scope=2)
    await high.permissions.add(dangerous)
    user = await Users.create(username="target", password="!", dept_id=shared.id)
    await user.roles.add(low)
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: actor
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield {"actor": actor, "actor_role": actor_role, "user": user, "low": low, "high": high,
               "own": own, "shared": shared, "hidden": hidden, "permissions": permissions,
               "dangerous": dangerous, "client": client}


async def test_user_cannot_receive_permission_actor_does_not_have(grants):
    g = grants
    response = await g["client"].put(f'/api/v1/system/users/{g["user"].id}/', json={"roles": [g["high"].id]})
    assert response.status_code == 403
    assert await g["user"].roles.all().values_list("id", flat=True) == [g["low"].id]


async def test_self_role_escalation_is_rejected(grants):
    g = grants
    response = await g["client"].put(f'/api/v1/system/users/{g["actor"].id}/', json={"roles": [g["actor_role"].id, g["high"].id]})
    assert response.status_code == 403


async def test_role_scope_is_evaluated_at_target_department(grants):
    g = grants
    await Roles.filter(id=g["low"].id).update(data_scope=4)
    response = await g["client"].put(f'/api/v1/system/users/{g["user"].id}/', json={"roles": [g["low"].id]})
    assert response.status_code == 403


async def test_role_edit_rejects_holders_outside_actor_scope(grants):
    g = grants
    hidden_user = await Users.create(username="hidden-holder", password="!", dept_id=g["hidden"].id)
    await hidden_user.roles.add(g["low"])
    response = await g["client"].put(f'/api/v1/system/roles/{g["low"].id}/', json={"desc": "changed"})
    assert response.status_code == 403
    await g["low"].refresh_from_db()
    assert g["low"].desc != "changed"


async def test_menu_assignment_cannot_grant_unowned_permission(grants):
    g = grants
    response = await g["client"].put(f'/api/v1/system/roles/{g["low"].id}/menus/', json={"menuIds": [g["dangerous"].id]})
    assert response.status_code == 403


async def test_protected_role_cannot_be_renamed_to_bypass_delete(grants):
    g = grants
    await Users.filter(id=g["actor"].id).update(is_superuser=True)
    g["actor"].is_superuser = True
    await Roles.filter(id=g["high"].id).update(name="admin", code="admin")
    response = await g["client"].put(f'/api/v1/system/roles/{g["high"].id}/', json={"name": "ordinary", "code": "ordinary"})
    assert response.status_code == 400


async def test_delegated_admin_can_manage_owned_subset_without_sort_hierarchy(grants):
    g = grants
    response = await g["client"].put(f'/api/v1/system/roles/{g["low"].id}/menus/', json={"menuIds": [g["permissions"][1].id]})
    assert response.status_code == 200


@pytest.mark.parametrize("default", [False, True])
async def test_create_checks_explicit_and_default_roles_before_creating_user(grants, default):
    g = grants
    payload = {"username": "forbidden-create", "deptId": g["shared"].id}
    if default:
        await Roles.filter(id=g["high"].id).update(is_default=1)
    else:
        payload["roles"] = [g["high"].id]
    response = await g["client"].post('/api/v1/system/users/', json=payload)
    assert response.status_code == 403
    assert not await Users.filter(username="forbidden-create").exists()


async def test_multiple_actor_roles_form_a_union(grants):
    g = grants
    extra = await Roles.create(name="Extra authority", data_scope=5)
    await extra.permissions.add(g["dangerous"])
    await extra.data_depts.add(g["hidden"])
    await g["actor"].roles.add(extra)
    response = await g["client"].put(f'/api/v1/system/users/{g["user"].id}/', json={"roles": [g["high"].id]})
    assert response.status_code == 200
    assert await g["user"].roles.all().values_list("id", flat=True) == [g["high"].id]


async def test_cached_permission_does_not_authorize_after_database_revocation(grants):
    g = grants
    assert "system:roles:edit" in await g["actor"].get_permissions()
    await g["actor_role"].permissions.remove(g["permissions"][4])
    response = await g["client"].put(f'/api/v1/system/roles/{g["low"].id}/', json={"desc": "stale grant"})
    assert response.status_code == 403


@pytest.mark.parametrize("action", ["disable", "delete", "batch"])
async def test_outside_holders_block_all_role_mutations(grants, action):
    g = grants
    holder = await Users.create(username="outside-holder", password="!", dept_id=g["hidden"].id)
    await holder.roles.add(g["low"])
    path = f'/api/v1/system/roles/{g["low"].id}/'
    if action == "disable":
        response = await g["client"].put(path, json={"status": 0})
    elif action == "delete":
        response = await g["client"].delete(path)
    else:
        response = await g["client"].request("DELETE", '/api/v1/system/roles/', json={"ids": [g["low"].id]})
        assert response.json()["data"]["failures"][0]["errorCode"] == "PERMISSION_DENIED"
        assert await Roles.filter(id=g["low"].id).exists()
        return
    assert response.status_code == 403
    assert await Roles.filter(id=g["low"].id, status=1).exists()


async def test_import_rejects_only_forbidden_rows(grants):
    from io import BytesIO

    from openpyxl import Workbook

    g = grants
    book = Workbook()
    book.active.append(["用户名*", "部门ID", "角色ID(多个用逗号分隔)"])
    book.active.append(["accepted-import", g["shared"].id, str(g["low"].id)])
    book.active.append(["denied-import", g["shared"].id, str(g["high"].id)])
    buffer = BytesIO()
    book.save(buffer)
    book.close()
    buffer.seek(0)
    result = await user_service.import_users(buffer, current_user=g["actor"])
    assert (result.valid_count, result.invalid_count) == (1, 1)
    assert await Users.filter(username="accepted-import").exists()
    assert not await Users.filter(username="denied-import").exists()


async def test_role_scalar_and_relation_changes_rollback_together(grants, monkeypatch):
    from tortoise.fields.relational import ManyToManyRelation

    g = grants
    original_add = ManyToManyRelation.add

    async def fail_add(self, *args, **kwargs):
        if isinstance(self.instance, Roles) and self.instance.id == g["low"].id:
            raise RuntimeError("injected relation failure")
        return await original_add(self, *args, **kwargs)

    monkeypatch.setattr(ManyToManyRelation, "add", fail_add)
    with pytest.raises(RuntimeError, match="injected"):
        await role_service.update(g["low"].id, RoleUpdate(desc="partial write", permission_ids=[g["permissions"][1].id]), current_user=g["actor"])
    await g["low"].refresh_from_db()
    assert g["low"].desc != "partial write"
    assert await g["low"].permissions.all().values_list("id", flat=True) == [g["permissions"][1].id]
