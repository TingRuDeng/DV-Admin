"""Ten-thousand-user scope and bounded import lookup regression tests."""

import pytest
from django.db import connection
from openpyxl import Workbook
from scripts.query_performance_probe import QueryProbe

from drf_admin.apps.system.models import Departments, Notices, OperationLog, Roles, Users
from drf_admin.apps.system.services.data_scope import (
    apply_log_data_scope,
    apply_notice_admin_data_scope,
    apply_user_data_scope,
)
from drf_admin.apps.system.services.user_import_export import _build_context, _parse_columns


@pytest.fixture
def ten_thousand_users(db):
    department = Departments.objects.create(name="Visible")
    other = Departments.objects.create(name="Hidden")
    role = Roles.objects.create(name="Scope", code="scope", data_scope=Roles.DATA_SCOPE_DEPT)
    Users.objects.bulk_create([
        Users(username=f"probe-{i:05}", password="!", mobile=f"139{i:08}",
              dept_id=department.id if i < 5000 else other.id)
        for i in range(10000)
    ], batch_size=500)
    actor = Users.objects.get(username="probe-00000")
    actor.roles.add(role)
    return actor


def test_ten_thousand_user_scope_queries(ten_thousand_users):
    actor = ten_thousand_users
    visible = actor.id
    hidden = Users.objects.get(username="probe-09999").id
    for user_id in (visible, hidden):
        OperationLog.objects.create(user_id=user_id, operation="probe")
        Notices.objects.create(publisher_id=user_id, title="probe", content="probe")

    probes = []
    for label, model, apply_scope, count in (
        ("users", Users, apply_user_data_scope, 5000),
        ("logs", OperationLog, apply_log_data_scope, 1),
        ("notices", Notices, apply_notice_admin_data_scope, 1),
    ):
        with QueryProbe(f"django-{label}") as probe, connection.execute_wrapper(probe.django_execute):
            query = apply_scope(model.objects.all(), actor)
            assert query.count() == count
            page = list(query.order_by("id")[:10])
            assert len(page) == min(count, 10)
            if label != "users":
                assert getattr(page[0], "user_id" if label == "logs" else "publisher_id") == visible
        probes.append(probe)
        assert sum('FROM "system_users"' in sql for sql, _ in probe.queries) == 2
        if label != "users":
            assert sum(" IN (SELECT " in sql for sql, _ in probe.queries) == 2
    assert all(probe.metrics["max_parameters"] <= 12 for probe in probes)
    assert all(probe.metrics["queries"] <= 5 for probe in probes)


def test_import_only_preloads_batch_keys(ten_thousand_users):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["用户名*", "手机号", "部门ID", "角色ID(多个用逗号分隔)"])
    role = Roles.objects.get(code="scope")
    for i in range(1001):
        worksheet.append([f"probe-{i:05}", f"139{i:08}", ten_thousand_users.dept_id, str(role.id)])
    columns = _parse_columns(worksheet)
    with QueryProbe("django-import-context") as probe, connection.execute_wrapper(probe.django_execute):
        context = _build_context(worksheet, columns, ten_thousand_users.dept_id)
    workbook.close()
    print({"cached_usernames": len(context.existing_usernames), "cached_mobiles": len(context.existing_mobiles)})
    assert len(context.existing_usernames) == 1001
    assert len(context.existing_mobiles) == 1001
    assert probe.metrics["max_parameters"] <= 501
    assert len(context.all_depts) == len(context.all_roles) == 1
    assert len([n for sql, n in probe.queries if "system_users" in sql and " IN " in sql]) == 6


def test_scope_union_empty_disabled_and_unrestricted(db):
    department = Departments.objects.create(name="Custom scope")
    actor = Users.objects.create(username="scope-actor", password="!")
    visible = Users.objects.create(username="scope-visible", password="!", dept_id=department.id)
    hidden = Users.objects.create(username="scope-hidden", password="!")
    own = Roles.objects.create(name="Own", code="own", data_scope=Roles.DATA_SCOPE_SELF)
    custom = Roles.objects.create(name="Custom", code="custom", data_scope=Roles.DATA_SCOPE_CUSTOM)
    inactive = Roles.objects.create(name="Inactive", code="inactive", status=0, data_scope=Roles.DATA_SCOPE_ALL)
    custom.data_depts.add(department)
    actor.roles.add(own, custom, inactive)
    for user in (actor, visible, hidden):
        OperationLog.objects.create(user_id=user.id)
        Notices.objects.create(publisher_id=user.id, title="scope", content="scope")
    for expected in ({actor.id, visible.id}, set(), {actor.id, visible.id, hidden.id}):
        for model, apply_scope, field in (
            (Users, apply_user_data_scope, "id"),
            (OperationLog, apply_log_data_scope, "user_id"),
            (Notices, apply_notice_admin_data_scope, "publisher_id"),
        ):
            query = apply_scope(model.objects.all(), actor)
            assert set(query.values_list(field, flat=True)) == expected
        if expected:
            actor.roles.clear()
        else:
            actor.is_superuser = True
