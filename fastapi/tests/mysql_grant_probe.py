"""Independent MySQL process: real service transactions, no SQLite pytest fixtures."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from tortoise import Tortoise
from tortoise.fields.relational import ManyToManyRelation
from tortoise.transactions import in_transaction

from app.core.exceptions import PermissionDenied
from app.db.models.oauth import Users
from app.db.models.system import Departments, Permissions, Roles
from app.schemas.system import RoleUpdate, UserUpdate
from app.services.system.role_service import role_service
from app.services.system.user_service import user_service
from scripts.mysql_grant_testing import credentials, isolation, schema_name, wait_for_lock


async def seed(suffix):
    dept = await Departments.create(name=f"Dept {suffix}")
    edit = await Permissions.create(name=f"Edit {suffix}", type="BUTTON", perm="system:roles:edit")
    grant = await Permissions.create(name=f"Grant {suffix}", type="BUTTON", perm=f"demo:{suffix}:read")
    owner = await Roles.create(name=f"Owner {suffix}", data_scope=1)
    await owner.permissions.add(edit, grant)
    actor = await Users.create(username=f"actor-{suffix}", password="!", dept_id=dept.id)
    await actor.roles.add(owner)
    root = await Users.create(username=f"root-{suffix}", password="!", is_superuser=True)
    role = await Roles.create(name=f"Target {suffix}", data_scope=2, desc="original")
    target = await Users.create(username=f"target-{suffix}", password="!", dept_id=dept.id)
    await target.roles.add(role)
    return actor, root, owner, role, edit, grant


async def race(*, warm_snapshot=False, grant_first=False, revoke_kind="permission"):
    label = "grant_first" if grant_first else ("warm_snapshot" if warm_snapshot else "revoke_first")
    label = f"{label}_{revoke_kind}"
    actor, root, owner, role, edit, grant = await seed(label)
    if revoke_kind == "scope":
        owner.data_scope = 5
        await owner.save()
        await owner.data_depts.add(await Departments.get(id=actor.dept_id))
    ready, changed, release = asyncio.Event(), asyncio.Event(), asyncio.Event()
    ids = {}

    async def connection_id(connection, key):
        rows = await connection.execute_query_dict("SELECT CONNECTION_ID() AS id, @@transaction_isolation AS level")
        ids[key] = rows[0]["id"]
        assert rows[0]["level"] == isolation().replace(" ", "-")

    async def revoke():
        if revoke_kind == "membership":
            await user_service.update(actor.id, UserUpdate(role_ids=[]), current_user=root)
        elif revoke_kind == "scope":
            await role_service.update(owner.id, RoleUpdate(dept_ids=[]), current_user=root)
        else:
            await role_service.assign_menus(owner.id, [edit.id], current_user=root)

    async def assign():
        await role_service.assign_menus(role.id, [grant.id], current_user=actor)

    async def blocker():
        await asyncio.wait_for(ready.wait(), 15)
        async with in_transaction() as connection:
            await connection_id(connection, "blocker")
            await (assign() if grant_first else revoke())
            changed.set()
            await asyncio.wait_for(release.wait(), 15)

    async def waiter():
        try:
            async with in_transaction() as connection:
                await connection_id(connection, "waiter")
                if warm_snapshot:
                    await owner.permissions.all().values_list("id", flat=True)
                    await owner.data_depts.all().values_list("id", flat=True)
                    await actor.roles.all().values_list("id", flat=True)
                ready.set()
                await asyncio.wait_for(changed.wait(), 15)
                await (revoke() if grant_first else assign())
            return "committed"
        except PermissionDenied:
            return "denied"

    tasks = [asyncio.create_task(blocker()), asyncio.create_task(waiter())]
    try:
        await asyncio.wait_for(changed.wait(), 15)
        assert ids["waiter"] != ids["blocker"]
        await asyncio.to_thread(wait_for_lock, ids["waiter"], ids["blocker"])
        release.set()
        _, outcome = await asyncio.wait_for(asyncio.gather(*tasks), 20)
        assert outcome == ("committed" if grant_first else "denied"), (label, outcome)
        assert await role.permissions.all().values_list("id", flat=True) == ([grant.id] if grant_first else [])
        if revoke_kind == "membership":
            assert await actor.roles.all().count() == 0
        elif revoke_kind == "scope":
            assert await owner.data_depts.all().count() == 0
        else:
            assert await owner.permissions.all().values_list("id", flat=True) == [edit.id]
        print(json.dumps({"case": label, "outcome": outcome, "innodb_lock_wait": True}), flush=True)
    finally:
        release.set()
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def rollback():
    actor, _, _, role, _, grant = await seed("rollback")
    original = ManyToManyRelation.add
    written = []

    async def fail_after_write(relation, *args, **kwargs):
        result = await original(relation, *args, **kwargs)
        if isinstance(relation.instance, Roles) and relation.instance.id == role.id:
            written.extend(await relation.all().values_list("id", flat=True))
            raise RuntimeError("injected after association write")
        return result

    with patch.object(ManyToManyRelation, "add", fail_after_write):
        try:
            await role_service.update(role.id, RoleUpdate(desc="partial", permission_ids=[grant.id]), current_user=actor)
        except RuntimeError as exc:
            assert "injected" in str(exc)
        else:
            raise AssertionError("Expected injected write failure")
    assert written == [grant.id]
    await role.refresh_from_db()
    assert role.desc == "original"
    assert await role.permissions.all().count() == 0
    print(json.dumps({"case": "rollback", "scalar_and_association_restored": True}), flush=True)


async def main():
    from mysql_lock_order_probe import run_checks

    config = credentials()
    config["database"] = schema_name()
    config["init_command"] = f"SET SESSION TRANSACTION ISOLATION LEVEL {isolation()}"
    await Tortoise.init(config={
        "connections": {"default": {"engine": "tortoise.backends.mysql", "credentials": config}},
        "apps": {"models": {"models": ["app.db.models.oauth", "app.db.models.system"], "default_connection": "default"}},
    })
    try:
        await Tortoise.generate_schemas()
        await race()
        await race(grant_first=True)
        await rollback()
        await race(warm_snapshot=True)
        await race(warm_snapshot=True, revoke_kind="membership")
        await race(warm_snapshot=True, revoke_kind="scope")
        await run_checks(seed)
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
