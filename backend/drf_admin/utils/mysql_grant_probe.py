"""Independent MySQL process exercising real Django view transactions."""

from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import patch

import django
from django.conf import settings
from scripts.mysql_grant_testing import credentials, isolation, schema_name, wait_for_lock


def configure():
    os.environ["DJANGO_SETTINGS_MODULE"] = "drf_admin.settings_test"
    config = credentials()
    settings.DATABASES = {"default": {
        "ENGINE": "django.db.backends.mysql", "NAME": schema_name(),
        "HOST": config["host"], "PORT": config["port"],
        "USER": config["user"], "PASSWORD": config["password"],
        "OPTIONS": {"charset": "utf8mb4", "isolation_level": isolation().lower()},
    }}
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    settings.SESSION_CACHE_ALIAS = "default"
    settings.REDIS_HOST = ""
    settings.ALLOWED_HOSTS = ["testserver"]
    settings.LOGGING_CONFIG = None
    logging.disable(logging.CRITICAL)
    django.setup()


def seed(suffix):
    from drf_admin.apps.system.models import Departments, Permissions, Roles, Users

    dept = Departments.objects.create(name=f"Dept {suffix}")
    edit = Permissions.objects.create(name=f"Edit {suffix}", type="BUTTON", perm="system:roles:edit")
    grant = Permissions.objects.create(name=f"Grant {suffix}", type="BUTTON", perm=f"demo:{suffix}:read")
    owner = Roles.objects.create(name=f"Owner {suffix}", data_scope=1)
    owner.permissions.add(edit, grant)
    actor = Users.objects.create(username=f"actor-{suffix}", password="!", dept=dept)
    actor.roles.add(owner)
    root = Users.objects.create(username=f"root-{suffix}", password="!", is_superuser=True)
    role = Roles.objects.create(name=f"Target {suffix}", data_scope=2, desc="original")
    target = Users.objects.create(username=f"target-{suffix}", password="!", dept=dept)
    target.roles.add(role)
    return actor, root, owner, role, edit, grant


def assign(actor, role, permission):
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(actor)
    response = client.put(f"/api/v1/system/roles/{role.id}/menus/", {"menuIds": [permission.id]}, format="json")
    assert response.status_code in {200, 403}, response.content
    return "committed" if response.status_code == 200 else "denied"


def race(*, warm_snapshot=False, grant_first=False, revoke_kind="permission"):
    from django.db import connection, connections, transaction
    from rest_framework.test import APIClient

    label = "grant_first" if grant_first else ("warm_snapshot" if warm_snapshot else "revoke_first")
    label = f"{label}_{revoke_kind}"
    actor, root, owner, role, edit, grant = seed(label)
    if revoke_kind == "scope":
        owner.data_scope = 5
        owner.save()
        owner.data_depts.add(actor.dept)
    ready, changed, release = Event(), Event(), Event()
    ids = {}

    def revoke():
        if revoke_kind == "permission":
            return assign(root, owner, edit)
        client = APIClient()
        client.force_authenticate(root)
        path, payload = (
            (f"users/{actor.id}", {"username": actor.username, "roles": []})
            if revoke_kind == "membership"
            else (f"roles/{owner.id}", {"name": owner.name, "deptIds": []})
        )
        response = client.put(f"/api/v1/system/{path}/", payload, format="json")
        assert response.status_code == 200, response.content
        return "committed"

    def identify(key):
        with connection.cursor() as cursor:
            cursor.execute("SELECT CONNECTION_ID(), @@transaction_isolation")
            ids[key], level = cursor.fetchone()
            assert level == isolation().replace(" ", "-")

    def blocker():
        try:
            assert ready.wait(15)
            with transaction.atomic():
                identify("blocker")
                outcome = assign(actor, role, grant) if grant_first else revoke()
                assert outcome == "committed"
                changed.set()
                assert release.wait(15)
        finally:
            connections.close_all()

    def waiter():
        try:
            with transaction.atomic():
                identify("waiter")
                if warm_snapshot:
                    list(owner.permissions.values_list("id", flat=True))
                    list(owner.data_depts.values_list("id", flat=True))
                    list(actor.roles.values_list("id", flat=True))
                ready.set()
                assert changed.wait(15)
                return revoke() if grant_first else assign(actor, role, grant)
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        blocking = pool.submit(blocker)
        waiting = pool.submit(waiter)
        try:
            if not changed.wait(15):
                for future in (blocking, waiting):
                    if future.done():
                        future.result()
                raise AssertionError("Blocker did not reach its mutation checkpoint")
            assert ids["waiter"] != ids["blocker"]
            wait_for_lock(ids["waiter"], ids["blocker"])
        finally:
            release.set()
        blocking.result(timeout=20)
        outcome = waiting.result(timeout=20)
    assert outcome == ("committed" if grant_first else "denied"), (label, outcome)
    assert list(role.permissions.values_list("id", flat=True)) == ([grant.id] if grant_first else [])
    if revoke_kind == "membership":
        assert actor.roles.count() == 0
    elif revoke_kind == "scope":
        assert owner.data_depts.count() == 0
    else:
        assert list(owner.permissions.values_list("id", flat=True)) == [edit.id]
    print(json.dumps({"case": label, "outcome": outcome, "innodb_lock_wait": True}), flush=True)


def rollback():
    from rest_framework.test import APIClient

    actor, _, _, role, _, _ = seed("rollback")
    manager = type(role.data_depts)
    original = manager.set
    written = []

    def fail_after_write(relation, *args, **kwargs):
        result = original(relation, *args, **kwargs)
        if relation.instance.pk == role.pk:
            written.extend(relation.values_list("id", flat=True))
            raise RuntimeError("injected after association write")
        return result

    client = APIClient()
    client.force_authenticate(actor)
    with patch.object(manager, "set", fail_after_write):
        response = client.put(f"/api/v1/system/roles/{role.id}/", {
            "name": role.name, "desc": "partial", "deptIds": [actor.dept_id],
        }, format="json")
        assert response.status_code == 500, response.content
        assert written == [actor.dept_id]
    role.refresh_from_db()
    assert role.desc == "original"
    assert role.data_depts.count() == 0
    print(json.dumps({"case": "rollback", "scalar_and_association_restored": True}), flush=True)


def main():
    configure()
    from django.core.management import call_command
    from django.db import connections

    try:
        call_command("migrate", verbosity=0, interactive=False)
        race()
        race(grant_first=True)
        rollback()
        race(warm_snapshot=True)
        race(warm_snapshot=True, revoke_kind="membership")
        race(warm_snapshot=True, revoke_kind="scope")
    finally:
        connections.close_all()


if __name__ == "__main__":
    main()
