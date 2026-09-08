"""Deterministic races through real services; hooks only schedule real DB work."""

import asyncio
import json
from unittest.mock import patch

from tortoise import connections
from tortoise.fields.relational import ManyToManyRelation

from app.db.models.oauth import Users
from app.db.models.system import Permissions, Roles
from app.schemas.system import RoleUpdate, UserUpdate
from app.services.system.grant_boundary import GrantBoundary
from app.services.system.role_service import role_service
from app.services.system.user_service import user_service
from scripts.mysql_grant_testing import (
    WriteFaultBlocker,
    deadlock_count,
    mysql_errno,
    wait_for_lock,
)


async def ordered_delete(kind, seed):
    actor, _, owner, role, _, _ = await seed(f"order_{kind}")
    for code in ("system:roles:delete", "system:users:edit", "system:users:delete"):
        await owner.permissions.add(await Permissions.create(name="Order permission", type="BUTTON", perm=code))
    is_user = kind.startswith("user_")
    target = await Users.filter(roles__id=role.id).first()
    ready, release = asyncio.Event(), asyncio.Event()
    ids = {}
    original = GrantBoundary.load
    before = await asyncio.to_thread(deadlock_count)

    async def gated_load(user, permission):
        name = asyncio.current_task().get_name()
        rows = await connections.get("default").execute_query_dict("SELECT CONNECTION_ID() AS id")
        ids[name] = rows[0]["id"]
        boundary = await original(user, permission)
        if name == "updater" and not ready.is_set():
            ready.set()
            await asyncio.wait_for(release.wait(), 15)
        return boundary

    async def update():
        if is_user:
            await user_service.update(target.id, UserUpdate(name="updated", role_ids=[]), current_user=actor)
        else:
            await role_service.update(role.id, RoleUpdate(desc="updated"), current_user=actor)
        return "updated"

    async def delete():
        await asyncio.wait_for(ready.wait(), 15)
        if kind == "role_delete":
            await role_service.delete(role.id, current_user=actor)
        else:
            service, pk = (user_service, target.id) if is_user else (role_service, role.id)
            delete_items = service.retry_batch_delete if kind.endswith("retry") else service.batch_delete
            result = await delete_items([pk], current_user=actor)
            assert result.failed_count == 0, result
        return "deleted"

    with patch.object(GrantBoundary, "load", gated_load):
        tasks = [asyncio.create_task(update(), name="updater"), asyncio.create_task(delete(), name="deleter")]
        try:
            await asyncio.wait_for(ready.wait(), 15)
            # The deleter identifies its connection when entering the real boundary.
            async def identified():
                while "deleter" not in ids:
                    await asyncio.sleep(0.01)
            await asyncio.wait_for(identified(), 15)
            await asyncio.to_thread(wait_for_lock, ids["deleter"], ids["updater"])
            release.set()
            results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 20)
        finally:
            release.set()
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    after = await asyncio.to_thread(deadlock_count)
    assert results == ["updated", "deleted"], (kind, results, "deadlocks", after - before)
    assert after == before
    model, pk = (Users, target.id) if is_user else (Roles, role.id)
    assert not await model.filter(id=pk).exists()
    print(json.dumps({"case": kind, "both_committed": True, "deadlocks": 0}), flush=True)


async def run_checks(seed):
    for kind in ("role_delete", "role_batch", "user_batch", "role_retry", "user_retry"):
        await ordered_delete(kind, seed)
    await cross_admin()
    for fault in ("deadlock", "timeout"):
        await write_failure(fault, seed)


async def cross_admin():
    actors = [await Users.create(username=f"cross-{n}", password="!", is_superuser=True, name="original") for n in range(2)]
    original = GrantBoundary.load
    arrived = [asyncio.Event(), asyncio.Event()]
    calls = [0, 0]
    before = await asyncio.to_thread(deadlock_count)

    async def gated(user, permission):
        boundary = await original(user, permission)
        index = int(asyncio.current_task().get_name())
        if not arrived[index].is_set():
            arrived[index].set()
            await asyncio.wait_for(arrived[1 - index].wait(), 15)
        return boundary

    async def update(index):
        calls[index] += 1
        await user_service.update(actors[1 - index].id, UserUpdate(name=f"by-{index}", role_ids=[]), current_user=actors[index])
        return "committed"

    with patch.object(GrantBoundary, "load", gated):
        tasks = [asyncio.create_task(update(n), name=str(n)) for n in range(2)]
        results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 20)
    assert results.count("committed") == 1, results
    assert [mysql_errno(result) for result in results if isinstance(result, BaseException)] == [1213], results
    assert await asyncio.to_thread(deadlock_count) == before + 1
    assert calls == [1, 1]
    for n, actor in enumerate(actors):
        await actor.refresh_from_db()
        assert actor.name == (f"by-{1 - n}" if results[1 - n] == "committed" else "original")
        assert await actor.roles.all().count() == 0
    print(json.dumps({"case": "cross_admin", "committed": 1, "deadlock_rejected": 1, "automatic_retries": 0}), flush=True)


async def write_failure(fault, seed):
    _, actor, _, role, _, grant = await seed(f"fault_{fault}")
    original = ManyToManyRelation.add
    written = []
    observed = []
    reached = asyncio.Event()
    ids = {}
    before = await asyncio.to_thread(deadlock_count)

    async def fail_after_write(relation, *args, **kwargs):
        result = await original(relation, *args, **kwargs)
        if isinstance(relation.instance, Roles) and relation.instance.id == role.id:
            written.extend(await relation.all().values_list("id", flat=True))
            connection = connections.get("default")
            ids["writer"] = (await connection.execute_query_dict("SELECT CONNECTION_ID() AS id"))[0]["id"]
            await connection.execute_query("SET SESSION innodb_lock_wait_timeout=2")
            reached.set()
            try:
                await connection.execute_query("UPDATE grant_fault_marker SET value=2 WHERE id=0")
            except Exception as exc:
                observed.append(mysql_errno(exc))
                raise
        return result

    with WriteFaultBlocker() as blocker, patch.object(ManyToManyRelation, "add", fail_after_write):
        task = asyncio.create_task(role_service.update(role.id, RoleUpdate(desc="partial", permission_ids=[grant.id]), current_user=actor))
        try:
            await asyncio.wait_for(reached.wait(), 15)
            await asyncio.to_thread(wait_for_lock, ids["writer"], blocker.connection_id)
            if fault == "deadlock":
                await asyncio.to_thread(blocker.close_cycle, Roles._meta.db_table, role.id)
            result = (await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), 10))[0]
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    assert observed == [1213 if fault == "deadlock" else 1205], (observed, result)
    assert isinstance(result, BaseException), result
    assert written == [grant.id]
    await role.refresh_from_db()
    assert role.desc == "original" and await role.permissions.all().count() == 0
    assert await asyncio.to_thread(deadlock_count) == before + (fault == "deadlock")
    print(json.dumps({"case": f"write_{fault}", "mysql_errno": observed[0], "scalar_and_association_restored": True}), flush=True)
