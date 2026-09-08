"""Real view races with scheduling hooks, not mocked locks or authorization."""

import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, current_thread
from unittest.mock import patch

from django.db import connection, connections
from rest_framework.test import APIClient
from scripts.mysql_grant_testing import (
    WriteFaultBlocker,
    deadlock_count,
    mysql_errno,
    wait_for_lock,
)

from drf_admin.apps.system.models import Permissions, Roles, Users
from drf_admin.apps.system.services.grant_boundary import GrantBoundary


def ordered_delete(kind, seed):
    actor, _, owner, role, _, _ = seed(f"order_{kind}")
    for code in ("system:roles:delete", "system:users:edit", "system:users:delete"):
        owner.permissions.add(Permissions.objects.create(name="Order permission", type="BUTTON", perm=code))
    is_user = kind.startswith("user_")
    target = Users.objects.get(roles=role)
    ready, release, identified = Event(), Event(), Event()
    ids = {}
    original = GrantBoundary.load
    before = deadlock_count()

    def gated_load(user, permission):
        name = current_thread().name
        with connection.cursor() as cursor:
            cursor.execute("SELECT CONNECTION_ID()")
            ids[name] = cursor.fetchone()[0]
        if name == "deleter":
            identified.set()
        boundary = original(user, permission)
        if name == "updater" and not ready.is_set():
            ready.set()
            assert release.wait(15)
        return boundary

    def request(name):
        current_thread().name = name
        client = APIClient()
        client.force_authenticate(actor)
        try:
            if name == "updater":
                if is_user:
                    path, payload = f"users/{target.id}", {"username": target.username, "name": "updated", "roles": []}
                else:
                    path, payload = f"roles/{role.id}", {"name": role.name, "desc": "updated"}
                response = client.put(f"/api/v1/system/{path}/", payload, format="json")
                assert response.status_code == 200, response.content
                return "updated"
            assert ready.wait(15)
            if kind == "role_delete":
                response = client.delete(f"/api/v1/system/roles/{role.id}/")
                assert response.status_code == 204, response.content
            else:
                resource, pk = ("users", target.id) if is_user else ("roles", role.id)
                if kind.endswith("retry"):
                    response = client.post(f"/api/v1/system/{resource}/batch-delete/retry/", {"ids": [pk]}, format="json")
                else:
                    response = client.delete(f"/api/v1/system/{resource}/", {"ids": [pk]}, format="json")
                assert response.status_code == 200, response.content
                assert response.json()["data"]["failedCount"] == 0, response.content
            return "deleted"
        finally:
            connections.close_all()

    with patch.object(GrantBoundary, "load", gated_load), ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(request, name) for name in ("updater", "deleter")]
        try:
            assert ready.wait(15) and identified.wait(15)
            wait_for_lock(ids["deleter"], ids["updater"])
        finally:
            release.set()
        results = []
        for future in futures:
            try:
                results.append(future.result(timeout=20))
            except Exception as exc:
                results.append(repr(exc))
    after = deadlock_count()
    assert results == ["updated", "deleted"], (kind, results, "deadlocks", after - before)
    assert after == before
    model, pk = (Users, target.id) if is_user else (Roles, role.id)
    assert not model.objects.filter(id=pk).exists()
    print(json.dumps({"case": kind, "both_committed": True, "deadlocks": 0}), flush=True)


def run_checks(seed):
    for kind in ("role_delete", "role_batch", "user_batch", "role_retry", "user_retry"):
        ordered_delete(kind, seed)
    cross_admin()
    for fault in ("deadlock", "timeout"):
        write_failure(fault, seed)


def cross_admin():
    actors = [Users.objects.create(username=f"cross-{n}", password="!", is_superuser=True, name="original") for n in range(2)]
    original = GrantBoundary.load
    barrier = Barrier(2)
    arrived = set()
    calls = [0, 0]
    before = deadlock_count()

    def gated(user, permission):
        boundary = original(user, permission)
        if user.pk not in arrived:
            arrived.add(user.pk)
            barrier.wait(timeout=15)
        return boundary

    def update(index):
        client = APIClient()
        client.force_authenticate(actors[index])
        calls[index] += 1
        try:
            response = client.put(f"/api/v1/system/users/{actors[1 - index].pk}/", {
                "username": actors[1 - index].username, "name": f"by-{index}", "roles": [],
            }, format="json")
            return response.status_code
        finally:
            connections.close_all()

    with patch.object(GrantBoundary, "load", gated), ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(update, n) for n in range(2)]
        results = [future.result(timeout=20) for future in futures]
    # Preserve the existing Django DatabaseError response contract.
    assert sorted(results) == [200, 507], results
    assert deadlock_count() == before + 1
    assert calls == [1, 1]
    for n, actor in enumerate(actors):
        actor.refresh_from_db()
        assert actor.name == (f"by-{1 - n}" if results[1 - n] == 200 else "original")
        assert actor.roles.count() == 0
    print(json.dumps({"case": "cross_admin", "committed": 1, "deadlock_rejected": 1, "automatic_retries": 0}), flush=True)


def write_failure(fault, seed):
    _, actor, _, role, _, _ = seed(f"fault_{fault}")
    # The full role update writes departments; permissions use a separate endpoint.
    from drf_admin.apps.system.models import Departments

    dept = Departments.objects.first()
    manager = type(role.data_depts)
    original = manager.set
    written, observed = [], []
    reached = Event()
    ids = {}
    before = deadlock_count()

    def fail_after_write(relation, *args, **kwargs):
        result = original(relation, *args, **kwargs)
        if relation.instance.pk == role.pk:
            written.extend(relation.values_list("id", flat=True))
            with connection.cursor() as cursor:
                cursor.execute("SELECT CONNECTION_ID()")
                ids["writer"] = cursor.fetchone()[0]
                cursor.execute("SET SESSION innodb_lock_wait_timeout=2")
                reached.set()
                try:
                    cursor.execute("UPDATE grant_fault_marker SET value=2 WHERE id=0")
                except Exception as exc:
                    observed.append(mysql_errno(exc))
                    raise
        return result

    def write():
        client = APIClient()
        client.force_authenticate(actor)
        try:
            return client.put(f"/api/v1/system/roles/{role.pk}/", {
                "name": role.name, "desc": "partial", "deptIds": [dept.pk],
            }, format="json").status_code
        finally:
            connections.close_all()

    with WriteFaultBlocker() as blocker, patch.object(manager, "set", fail_after_write), ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(write)
        if not reached.wait(15):
            raise AssertionError(("write checkpoint not reached", future.result(timeout=1)))
        wait_for_lock(ids["writer"], blocker.connection_id)
        if fault == "deadlock":
            blocker.close_cycle(Roles._meta.db_table, role.pk)
        status = future.result(timeout=10)
    assert status == 507, (status, observed)
    assert observed == [1213 if fault == "deadlock" else 1205], observed
    assert written == [dept.pk]
    role.refresh_from_db()
    assert role.desc == "original" and role.data_depts.count() == 0
    assert deadlock_count() == before + (fault == "deadlock")
    print(json.dumps({"case": f"write_{fault}", "mysql_errno": observed[0], "scalar_and_association_restored": True}), flush=True)
