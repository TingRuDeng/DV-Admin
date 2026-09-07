"""Runtime delegated-role authorization boundaries."""

from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from drf_admin.apps.system.models import Departments, Permissions, Roles, Users


class RoleGrantBoundaryTests(TestCase):
    def setUp(self):
        self.own = Departments.objects.create(name="Owned")
        self.shared = Departments.objects.create(name="Shared")
        self.hidden = Departments.objects.create(name="Hidden", parent=self.shared)
        codes = ("system:users:add", "system:users:edit", "system:users:import", "system:roles:add", "system:roles:edit", "system:roles:delete")
        self.permissions = [Permissions.objects.create(name=code, type="BUTTON", perm=code) for code in codes]
        self.dangerous = Permissions.objects.create(name="Outside", type="BUTTON", perm="outside:write")
        self.actor_role = Roles.objects.create(name="Delegated", code="delegated", data_scope=5, sort=999)
        self.actor_role.data_depts.add(self.own, self.shared)
        self.actor_role.permissions.add(*self.permissions)
        self.actor = Users.objects.create_user(username="delegate", password="old", dept=self.own)
        self.actor.roles.add(self.actor_role)
        self.low = Roles.objects.create(name="Scoped", code="scoped", data_scope=2, sort=0)
        self.low.permissions.add(self.permissions[1])
        self.high = Roles.objects.create(name="Outside role", code="outside", data_scope=2)
        self.high.permissions.add(self.dangerous)
        self.user = Users.objects.create_user(username="target", password="old", dept=self.shared)
        self.user.roles.add(self.low)
        self.client = APIClient()
        self.client.force_authenticate(self.actor)

    def test_unowned_user_role_and_self_escalation_are_rejected(self):
        for user, roles in ((self.user, [self.high.id]), (self.actor, [self.actor_role.id, self.high.id])):
            with self.subTest(user=user.id):
                response = self.client.put(f"/api/v1/system/users/{user.id}/", {"username": user.username, "roles": roles}, format="json")
                self.assertEqual(response.status_code, 403)
        self.assertEqual(list(self.user.roles.values_list("id", flat=True)), [self.low.id])

    def test_scope_uses_target_department_instead_of_enum_ranking(self):
        self.low.data_scope = Roles.DATA_SCOPE_DEPT_AND_CHILDREN
        self.low.save()
        response = self.client.put(f"/api/v1/system/users/{self.user.id}/", {"username": self.user.username, "roles": [self.low.id]}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_role_with_outside_holder_cannot_be_changed(self):
        user = Users.objects.create_user(username="hidden-holder", password="old", dept=self.hidden)
        user.roles.add(self.low)
        response = self.client.put(f"/api/v1/system/roles/{self.low.id}/", {"name": self.low.name, "desc": "changed"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.low.refresh_from_db()
        self.assertNotEqual(self.low.desc, "changed")

    def test_canonical_and_compat_menu_assignments_cannot_escalate(self):
        response = self.client.put(f"/api/v1/system/roles/{self.low.id}/menus/", {"menuIds": [self.dangerous.id]}, format="json")
        self.assertEqual(response.status_code, 403)
        response = self.client.patch(f"/api/v1/system/roles/{self.low.id}/", {"permissions": [self.dangerous.id]}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_protected_role_cannot_be_renamed_to_allow_deletion(self):
        self.actor.is_superuser = True
        self.actor.save()
        self.high.name = self.high.code = "admin"
        self.high.save()
        response = self.client.put(f"/api/v1/system/roles/{self.high.id}/", {"name": "ordinary", "code": "ordinary"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_owned_subset_is_manageable_despite_sort_value(self):
        response = self.client.put(f"/api/v1/system/roles/{self.low.id}/menus/", {"menuIds": [self.permissions[1].id]}, format="json")
        self.assertEqual(response.status_code, 200)

    def test_create_checks_explicit_and_default_roles_without_orphans(self):
        for default in (False, True):
            self.high.is_default = default
            self.high.save()
            payload = {"username": "denied-create", "deptId": self.shared.id}
            if not default:
                payload["roles"] = [self.high.id]
            response = self.client.post("/api/v1/system/users/", payload, format="json")
            self.assertEqual(response.status_code, 403)
            self.assertFalse(Users.objects.filter(username="denied-create").exists())

    def test_multi_role_union_allows_a_bounded_grant(self):
        extra = Roles.objects.create(name="Extra", data_scope=5)
        extra.permissions.add(self.dangerous)
        extra.data_depts.add(self.hidden)
        self.actor.roles.add(extra)
        response = self.client.put(f"/api/v1/system/users/{self.user.id}/", {"username": self.user.username, "roles": [self.high.id]}, format="json")
        self.assertEqual(response.status_code, 200)

    def test_disabled_actor_role_cannot_reuse_cached_permission(self):
        from drf_admin.utils.permissions import RBACPermission

        self.assertIn("system:roles:edit", RBACPermission.get_user_permissions(self.actor))
        Roles.objects.filter(id=self.actor_role.id).update(status=0)
        response = self.client.put(f"/api/v1/system/roles/{self.low.id}/menus/", {"menuIds": []}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_outside_holder_blocks_disable_delete_and_batch(self):
        holder = Users.objects.create_user(username="outside", dept=self.hidden)
        holder.roles.add(self.low)
        path = f"/api/v1/system/roles/{self.low.id}/"
        self.assertEqual(self.client.put(path, {"name": self.low.name, "status": 0}, format="json").status_code, 403)
        self.assertEqual(self.client.delete(path).status_code, 403)
        result = self.client.delete("/api/v1/system/roles/", {"ids": [self.low.id]}, format="json")
        self.assertEqual(result.json()["data"]["failures"][0]["errorCode"], "PERMISSION_DENIED")
        self.assertTrue(Roles.objects.filter(id=self.low.id, status=1).exists())

    def test_import_preserves_valid_rows_and_rejects_escalation(self):
        from drf_admin.apps.system.services.user_import_export import import_users
        from drf_admin.apps.system.test_user_import_export import build_import_file

        upload = build_import_file([
            ["valid-import", "Valid", "", "", "0", self.shared.id, str(self.low.id)],
            ["denied-import", "Denied", "", "", "0", self.shared.id, str(self.high.id)],
        ])
        result = import_users(upload, dept_id=self.shared.id, current_user=self.actor)
        self.assertEqual((result["validCount"], result["invalidCount"]), (1, 1))
        self.assertTrue(Users.objects.filter(username="valid-import").exists())
        self.assertFalse(Users.objects.filter(username="denied-import").exists())

    def test_partial_relation_failure_rolls_back_scalar_and_association(self):
        manager_type = type(self.user.roles)
        with patch.object(manager_type, "set", side_effect=RuntimeError("injected relation failure")) as assign:
            response = self.client.put(f"/api/v1/system/users/{self.user.id}/", {"username": self.user.username, "name": "partial write", "roles": [self.low.id]}, format="json")
            self.assertEqual(response.status_code, 500)
            assign.assert_called_once()
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.name, "partial write")
        self.assertEqual(list(self.user.roles.values_list("id", flat=True)), [self.low.id])
