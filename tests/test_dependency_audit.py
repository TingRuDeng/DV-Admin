"""生产依赖审计门禁测试。"""

import unittest
from datetime import date

from scripts.validate_dependency_audit import (
    AuditValidationError,
    evaluate_audit,
    parse_exemptions,
)

ADVISORY_ID = "GHSA-example-0000-0000"
PACKAGE = "transitive-package"
PATH = ".>host-package>transitive-package"


def report(*, severity: str = "high", paths: list[str] | None = None):
    return {
        "advisories": {
            "123": {
                "github_advisory_id": ADVISORY_ID,
                "module_name": PACKAGE,
                "severity": severity,
                "url": "https://example.invalid/advisory",
                "findings": [{"paths": paths or [PATH]}],
            }
        }
    }


def exemption_payload(
    *,
    introduced_at: str = "2026-07-28",
    expires_at: str = "2026-08-31",
    paths: list[str] | None = None,
):
    return {
        "version": 1,
        "exemptions": [
            {
                "id": ADVISORY_ID,
                "package": PACKAGE,
                "paths": paths or [PATH],
                "introducedAt": introduced_at,
                "expiresAt": expires_at,
                "owner": "DV-Admin Team",
                "reason": "等待宿主依赖发布兼容修复。",
                "tracking": "docs/TECH_DEBT.md#dependency-audit",
            }
        ],
    }


class DependencyAuditTests(unittest.TestCase):
    def test_unexempted_high_advisory_fails(self):
        violations, unused = evaluate_audit(report(), [], minimum_severity="high")

        self.assertEqual(len(violations), 1)
        self.assertEqual(unused, [])

    def test_scoped_unexpired_exemption_passes(self):
        exemptions = parse_exemptions(
            exemption_payload(),
            today=date(2026, 7, 28),
        )

        violations, unused = evaluate_audit(
            report(),
            exemptions,
            minimum_severity="high",
        )

        self.assertEqual(violations, [])
        self.assertEqual(unused, [])

    def test_new_dependency_path_is_not_covered_by_existing_exemption(self):
        exemptions = parse_exemptions(
            exemption_payload(),
            today=date(2026, 7, 28),
        )

        violations, _ = evaluate_audit(
            report(paths=[PATH, ".>another-host>transitive-package"]),
            exemptions,
            minimum_severity="high",
        )

        self.assertIn("未豁免路径", violations[0])

    def test_missing_findings_fails_closed(self):
        malformed = report()
        del malformed["advisories"]["123"]["findings"]
        exemptions = parse_exemptions(exemption_payload(), today=date(2026, 7, 28))

        with self.assertRaisesRegex(AuditValidationError, "findings 必须是非空数组"):
            evaluate_audit(malformed, exemptions, minimum_severity="high")

    def test_empty_or_invalid_finding_paths_fail_closed(self):
        exemptions = parse_exemptions(exemption_payload(), today=date(2026, 7, 28))
        for paths in ([], [""], [None]):
            with self.subTest(paths=paths):
                malformed = report()
                malformed["advisories"]["123"]["findings"] = [{"paths": paths}]
                with self.assertRaisesRegex(
                    AuditValidationError,
                    "finding.paths 必须是非空字符串数组",
                ):
                    evaluate_audit(malformed, exemptions, minimum_severity="high")

    def test_expired_exemption_fails_even_before_audit_evaluation(self):
        with self.assertRaisesRegex(AuditValidationError, "已于 2026-07-27 过期"):
            parse_exemptions(
                exemption_payload(
                    introduced_at="2026-07-01",
                    expires_at="2026-07-27",
                ),
                today=date(2026, 7, 28),
            )

    def test_future_exemption_cannot_be_used_early(self):
        with self.assertRaisesRegex(AuditValidationError, "尚未生效"):
            parse_exemptions(
                exemption_payload(introduced_at="2026-07-29"),
                today=date(2026, 7, 28),
            )

    def test_advisory_below_threshold_does_not_fail(self):
        violations, unused = evaluate_audit(
            report(severity="moderate"),
            [],
            minimum_severity="high",
        )

        self.assertEqual(violations, [])
        self.assertEqual(unused, [])

    def test_invalid_exemption_schema_fails_closed(self):
        with self.assertRaisesRegex(AuditValidationError, "version=1"):
            parse_exemptions({}, today=date(2026, 7, 28))


if __name__ == "__main__":
    unittest.main()
