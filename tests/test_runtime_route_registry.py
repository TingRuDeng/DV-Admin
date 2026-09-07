import unittest
from unittest.mock import patch

from scripts import api_runtime_route_contracts as contracts


class RuntimeRouteRegistryTests(unittest.TestCase):
    def test_paths_normalize_across_frameworks(self):
        samples = (
            "/api/v1/system/users/{id}/",
            "api/v1/system/users/<int:pk>/",
            "^api/v1/system/users/(?P<pk>[^/.]+)/$",
        )
        for sample in samples:
            self.assertEqual(
                contracts.normalize_path(sample), "/api/v1/system/users/{}"
            )

    def test_adding_removing_or_changing_method_is_not_silently_accepted(self):
        for backend in contracts.BOTH:
            baseline = contracts.expected_routes(backend)
            contracts.assert_runtime_routes(backend, baseline)
            selected = ("GET", "/api/v1/system/users")
            for changed in (
                baseline | {("GET", "/new-module/escape")},
                baseline - {selected},
                (baseline - {selected}) | {("TRACE", selected[1])},
                baseline | {("GET", "/health/new-business-route")},
                baseline | {("HEAD", "/new-head-only")},
                baseline | {("OPTIONS", "/new-options-only")},
            ):
                with self.subTest(backend=backend), self.assertRaises(AssertionError):
                    contracts.assert_runtime_routes(backend, changed)

    def test_only_implicit_methods_and_explicit_framework_paths_are_excluded(self):
        for backend in contracts.BOTH:
            baseline = contracts.expected_routes(backend)
            extra = {
                ("HEAD", "/api/v1/system/users"),
                ("OPTIONS", "/api/v1/system/users"),
                ("GET", "/health/live"),
            }
            contracts.assert_runtime_routes(backend, baseline | extra)

    def test_duplicate_registry_entries_fail(self):
        with patch.object(
            contracts,
            "SUPPLEMENTAL_ROUTES",
            contracts.SUPPLEMENTAL_ROUTES + (contracts.SUPPLEMENTAL_ROUTES[0],),
        ):
            with self.assertRaisesRegex(AssertionError, "Duplicate route"):
                contracts.assert_runtime_route_registry()
