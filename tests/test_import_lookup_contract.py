"""Import key collection and chunk size stay identical across deployments."""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "fastapi/app/core/import_lookup.py"
spec = importlib.util.spec_from_file_location("import_lookup_contract", SOURCE)
lookup = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lookup
spec.loader.exec_module(lookup)


class ImportLookupContractTests(unittest.TestCase):
    def test_packaged_copies_match(self):
        self.assertEqual(SOURCE.read_bytes(), (ROOT / "backend/drf_admin/utils/import_lookup.py").read_bytes())

    def test_batches_are_bounded_and_ordered(self):
        self.assertEqual([len(batch) for batch in lookup.query_batches(range(1001))], [500, 500, 1])
        self.assertEqual(list(lookup.query_batches(set())), [])
        self.assertEqual(list(lookup.query_batches({4, 2, 1})), [[1, 2, 4]])

    def test_collects_only_references_without_replacing_row_validation(self):
        keys = lookup.collect_import_keys(
            [(" user ", " 13900000000 ", "7", "3, 4,3"), (None, None, "invalid", "bad"), ("user", "", 8, None)],
            username=0, mobile=1, dept=2, role=3, default_dept=9,
        )
        self.assertEqual(keys.usernames, {"user"})
        self.assertEqual(keys.mobiles, {"13900000000"})
        self.assertEqual(keys.departments, {7, 8, 9})
        self.assertEqual(keys.roles, {3, 4})
