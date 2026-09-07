"""Ten-thousand-user query shape guards; timing is informational only."""

import pytest_asyncio
from openpyxl import Workbook
from tortoise import Tortoise

from app.db.models.oauth import Users
from app.db.models.system import Departments, Notices, OperationLog, Roles
from app.services.system.data_scope import (
    apply_log_data_scope,
    apply_notice_admin_data_scope,
    apply_user_data_scope,
)
from app.services.system.user_service import user_service
from scripts.query_performance_probe import QueryProbe


@pytest_asyncio.fixture
async def ten_thousand_users(db):
    department = await Departments.create(name="Visible")
    other = await Departments.create(name="Hidden")
    role = await Roles.create(name="Scope", code="scope", data_scope=Roles.DATA_SCOPE_DEPT)
    await Users.bulk_create([
        Users(username=f"probe-{i:05}", password="!", mobile=f"139{i:08}",
              dept_id=department.id if i < 5000 else other.id)
        for i in range(10000)
    ], batch_size=500)
    actor = await Users.get(username="probe-00000")
    await actor.roles.add(role)
    return actor


def capture_queries(monkeypatch, probe):
    connection = Tortoise.get_connection("default")
    original = connection.execute_query

    async def execute(sql, values=None):
        probe.record(sql, values)
        return await original(sql, values)

    monkeypatch.setattr(connection, "execute_query", execute)


async def test_ten_thousand_user_scope_queries(ten_thousand_users, monkeypatch):
    actor = ten_thousand_users
    visible = actor.id
    hidden = (await Users.get(username="probe-09999")).id
    for user_id in (visible, hidden):
        await OperationLog.create(user_id=user_id, operation="probe")
        await Notices.create(publisher_id=user_id, title="probe", content="probe")

    probes = []
    for label, model, apply_scope, count in (
        ("users", Users, apply_user_data_scope, 5000),
        ("logs", OperationLog, apply_log_data_scope, 1),
        ("notices", Notices, apply_notice_admin_data_scope, 1),
    ):
        with monkeypatch.context() as patcher, QueryProbe(f"fastapi-{label}") as probe:
            capture_queries(patcher, probe)
            query = await apply_scope(model.all(), actor)
            assert await query.count() == count
            page = await query.order_by("id").limit(10)
            assert len(page) == min(count, 10)
            if label != "users":
                assert getattr(page[0], "user_id" if label == "logs" else "publisher_id") == visible
        probes.append(probe)
        assert sum('FROM "system_users"' in sql for sql, _ in probe.queries) == 2
        if label != "users":
            assert sum(" IN (SELECT " in sql for sql, _ in probe.queries) == 2
    assert all(probe.metrics["max_parameters"] <= 12 for probe in probes)
    assert all(probe.metrics["queries"] <= 5 for probe in probes)


async def test_import_only_preloads_batch_keys(ten_thousand_users, monkeypatch):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["用户名*", "手机号", "部门ID", "角色ID(多个用逗号分隔)"])
    role = await Roles.get(code="scope")
    for i in range(1001):
        worksheet.append([f"probe-{i:05}", f"139{i:08}", ten_thousand_users.dept_id, str(role.id)])
    columns = user_service._parse_import_columns(worksheet)
    with QueryProbe("fastapi-import-context") as probe:
        capture_queries(monkeypatch, probe)
        context = await user_service._build_import_context(worksheet, columns, ten_thousand_users.dept_id)
    workbook.close()
    print({"cached_usernames": len(context.existing_usernames), "cached_mobiles": len(context.existing_mobiles)})
    assert len(context.existing_usernames) == 1001
    assert len(context.existing_mobiles) == 1001
    assert probe.metrics["max_parameters"] <= 501
    assert len(context.all_depts) == len(context.all_roles) == 1
    assert len([n for sql, n in probe.queries if "system_users" in sql and " IN " in sql]) == 6


async def test_scope_union_empty_disabled_and_unrestricted(db):
    department = await Departments.create(name="Custom scope")
    actor = await Users.create(username="scope-actor", password="!")
    visible = await Users.create(username="scope-visible", password="!", dept_id=department.id)
    hidden = await Users.create(username="scope-hidden", password="!")
    own = await Roles.create(name="Own", code="own", data_scope=Roles.DATA_SCOPE_SELF)
    custom = await Roles.create(name="Custom", code="custom", data_scope=Roles.DATA_SCOPE_CUSTOM)
    inactive = await Roles.create(name="Inactive", code="inactive", status=0, data_scope=Roles.DATA_SCOPE_ALL)
    await custom.data_depts.add(department)
    await actor.roles.add(own, custom, inactive)
    for user in (actor, visible, hidden):
        await OperationLog.create(user_id=user.id)
        await Notices.create(publisher_id=user.id, title="scope", content="scope")
    for expected in ({actor.id, visible.id}, set(), {actor.id, visible.id, hidden.id}):
        for model, apply_scope, field in (
            (Users, apply_user_data_scope, "id"),
            (OperationLog, apply_log_data_scope, "user_id"),
            (Notices, apply_notice_admin_data_scope, "publisher_id"),
        ):
            query = await apply_scope(model.all(), actor)
            assert set(await query.values_list(field, flat=True)) == expected
        if expected:
            await actor.roles.clear()
        else:
            actor.is_superuser = True
