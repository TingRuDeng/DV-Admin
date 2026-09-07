"""Framework-independent delegation algebra and packaged policy parity."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "fastapi/app/core/grant_policy.py"
spec = importlib.util.spec_from_file_location("grant_policy_contract", SOURCE)
policy = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = policy
spec.loader.exec_module(policy)


class GrantPolicyContractTests(unittest.TestCase):
    def test_backend_policy_copies_match(self):
        self.assertEqual(SOURCE.read_bytes(), (ROOT / "backend/drf_admin/utils/grant_policy.py").read_bytes())

    def test_all_cannot_be_inferred_from_current_department_ids(self):
        role = policy.Role(1, frozenset({1}), 5, frozenset({10, 20}))
        actor = policy.Subject(1, 10, (role,))
        grant = policy.Role(2, frozenset({1}), 1, frozenset())
        boundary = policy.GrantPolicy(actor, {10: None, 20: None})
        with self.assertRaises(policy.GrantDenied):
            boundary.check_user(policy.Subject(2, 20, (grant,)))

    def test_self_domain_is_bound_to_identity(self):
        role = policy.Role(1, frozenset({1}), 2, frozenset())
        actor = policy.Subject(1, 10, (role,))
        boundary = policy.GrantPolicy(actor, {10: None})
        boundary.check_user(actor)
        with self.assertRaises(policy.GrantDenied):
            boundary.check_user(policy.Subject(2, 10, (role,)))

    def test_disabled_roles_cannot_supply_authority(self):
        role = policy.Role(1, frozenset({1}), 1, frozenset(), active=False)
        actor = policy.Subject(1, 10, (role,))
        boundary = policy.GrantPolicy(actor, {10: None})
        self.assertFalse(boundary.permissions)
        with self.assertRaises(policy.GrantDenied):
            boundary.check_user(actor)

    def test_reserved_frontend_root_identity_cannot_be_delegated(self):
        actor = policy.Subject(1, 10, (policy.Role(1, frozenset(), 1, frozenset()),))
        target = policy.Subject(2, 10, (policy.Role(2, frozenset(), 2, frozenset(), code="ROOT"),))
        with self.assertRaises(policy.GrantDenied):
            policy.GrantPolicy(actor, {10: None}).check_user(target)
