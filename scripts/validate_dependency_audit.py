#!/usr/bin/env python3
"""校验前端生产依赖审计结果及有期限、限定依赖路径的临时豁免。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = REPO_ROOT / "frontend"
DEFAULT_EXEMPTIONS = FRONTEND_ROOT / "dependency-audit-exemptions.json"
SEVERITY_RANK = {
    "info": 0,
    "low": 1,
    "moderate": 2,
    "high": 3,
    "critical": 4,
}


class AuditValidationError(ValueError):
    """依赖审计输入或豁免配置不合法。"""


@dataclass(frozen=True)
class Exemption:
    """只对指定公告、包和依赖路径生效的临时豁免。"""

    advisory_id: str
    package: str
    paths: frozenset[str]
    introduced_at: date
    expires_at: date
    owner: str
    reason: str
    tracking: str


def _required_string(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AuditValidationError(f"豁免字段 {key} 必须是非空字符串")
    return value.strip()


def _parse_iso_date(item: dict[str, Any], key: str) -> date:
    raw_value = _required_string(item, key)
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise AuditValidationError(f"豁免字段 {key} 必须使用 YYYY-MM-DD: {raw_value}") from exc


def parse_exemptions(payload: Any, *, today: date) -> list[Exemption]:
    """解析并校验豁免配置；任何已过期条目都会使门禁失败。"""
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise AuditValidationError("豁免配置必须是 version=1 的对象")
    raw_exemptions = payload.get("exemptions")
    if not isinstance(raw_exemptions, list):
        raise AuditValidationError("豁免配置 exemptions 必须是数组")

    exemptions: list[Exemption] = []
    identities: set[tuple[str, str]] = set()
    for index, item in enumerate(raw_exemptions):
        if not isinstance(item, dict):
            raise AuditValidationError(f"第 {index + 1} 个豁免必须是对象")
        raw_paths = item.get("paths")
        if (
            not isinstance(raw_paths, list)
            or not raw_paths
            or any(not isinstance(path, str) or not path.strip() for path in raw_paths)
        ):
            raise AuditValidationError(f"第 {index + 1} 个豁免 paths 必须是非空字符串数组")

        advisory_id = _required_string(item, "id")
        package = _required_string(item, "package")
        identity = (advisory_id, package)
        if identity in identities:
            raise AuditValidationError(f"重复豁免: {advisory_id} / {package}")
        identities.add(identity)

        introduced_at = _parse_iso_date(item, "introducedAt")
        expires_at = _parse_iso_date(item, "expiresAt")
        if introduced_at > expires_at:
            raise AuditValidationError(f"豁免 {advisory_id} 的 introducedAt 晚于 expiresAt")
        if introduced_at > today:
            raise AuditValidationError(
                f"豁免 {advisory_id} / {package} 尚未生效: {introduced_at.isoformat()}"
            )
        if today > expires_at:
            raise AuditValidationError(
                f"豁免 {advisory_id} / {package} 已于 {expires_at.isoformat()} 过期"
            )

        exemptions.append(
            Exemption(
                advisory_id=advisory_id,
                package=package,
                paths=frozenset(path.strip() for path in raw_paths),
                introduced_at=introduced_at,
                expires_at=expires_at,
                owner=_required_string(item, "owner"),
                reason=_required_string(item, "reason"),
                tracking=_required_string(item, "tracking"),
            )
        )
    return exemptions


def _advisory_paths(advisory: dict[str, Any]) -> frozenset[str]:
    paths: set[str] = set()
    findings = advisory.get("findings")
    if not isinstance(findings, list) or not findings:
        raise AuditValidationError("pnpm audit advisory.findings 必须是非空数组")
    for finding in findings:
        if not isinstance(finding, dict):
            raise AuditValidationError("pnpm audit finding 必须是对象")
        finding_paths = finding.get("paths")
        if (
            not isinstance(finding_paths, list)
            or not finding_paths
            or any(not isinstance(path, str) or not path for path in finding_paths)
        ):
            raise AuditValidationError("pnpm audit finding.paths 必须是非空字符串数组")
        paths.update(finding_paths)
    return frozenset(paths)


def evaluate_audit(
    report: Any,
    exemptions: list[Exemption],
    *,
    minimum_severity: str,
) -> tuple[list[str], list[str]]:
    """返回未豁免违规和未再命中的历史豁免。"""
    if minimum_severity not in SEVERITY_RANK:
        raise AuditValidationError(f"未知 severity: {minimum_severity}")
    if not isinstance(report, dict) or not isinstance(report.get("advisories"), dict):
        raise AuditValidationError("pnpm audit 输出缺少 advisories 对象")

    exemption_map = {
        (exemption.advisory_id, exemption.package): exemption for exemption in exemptions
    }
    used_exemptions: set[tuple[str, str]] = set()
    violations: list[str] = []

    for raw_id, raw_advisory in report["advisories"].items():
        if not isinstance(raw_advisory, dict):
            raise AuditValidationError(f"pnpm audit advisory {raw_id} 必须是对象")
        severity = raw_advisory.get("severity")
        if not isinstance(severity, str) or severity not in SEVERITY_RANK:
            raise AuditValidationError(f"pnpm audit advisory {raw_id} 的 severity 非法")
        if SEVERITY_RANK[severity] < SEVERITY_RANK[minimum_severity]:
            continue

        package = raw_advisory.get("module_name")
        if not isinstance(package, str) or not package:
            raise AuditValidationError(f"pnpm audit advisory {raw_id} 缺少 module_name")
        advisory_id = str(raw_advisory.get("github_advisory_id") or raw_id)
        identity = (advisory_id, package)
        exemption = exemption_map.get(identity)
        paths = _advisory_paths(raw_advisory)
        if exemption is None:
            url = raw_advisory.get("url") or ""
            violations.append(f"{severity}: {advisory_id} / {package} {url}".rstrip())
            continue

        uncovered_paths = paths - exemption.paths
        if uncovered_paths:
            violations.append(
                f"{severity}: {advisory_id} / {package} 出现未豁免路径: "
                + ", ".join(sorted(uncovered_paths))
            )
            continue
        used_exemptions.add(identity)

    unused = [
        f"{exemption.advisory_id} / {exemption.package}"
        for exemption in exemptions
        if (exemption.advisory_id, exemption.package) not in used_exemptions
    ]
    return violations, unused


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditValidationError(f"无法读取 JSON {path}: {exc}") from exc


def run_pnpm_audit() -> dict[str, Any]:
    """运行 pnpm 生产依赖审计；漏洞返回码 1 由后续策略判断。"""
    try:
        completed = subprocess.run(
            ["pnpm", "audit", "--prod", "--json"],
            cwd=FRONTEND_ROOT,
            capture_output=True,
            check=False,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditValidationError(f"pnpm audit 执行失败: {exc}") from exc
    if completed.returncode not in (0, 1):
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise AuditValidationError(f"pnpm audit 返回码 {completed.returncode}: {detail}")
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        detail = completed.stderr.strip() or completed.stdout[:500]
        raise AuditValidationError(f"pnpm audit 未返回合法 JSON: {detail}") from exc
    if not isinstance(report, dict):
        raise AuditValidationError("pnpm audit JSON 顶层必须是对象")
    return report


def _vulnerability_summary(report: dict[str, Any]) -> str:
    metadata = report.get("metadata", {})
    vulnerabilities = metadata.get("vulnerabilities", {}) if isinstance(metadata, dict) else {}
    if not isinstance(vulnerabilities, dict):
        return "unknown"
    return ", ".join(
        f"{severity}={vulnerabilities.get(severity, 0)}"
        for severity in ("critical", "high", "moderate", "low")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-json", type=Path, help="读取已有 pnpm audit JSON，跳过联网审计")
    parser.add_argument("--exemptions", type=Path, default=DEFAULT_EXEMPTIONS)
    parser.add_argument("--minimum-severity", choices=SEVERITY_RANK, default="high")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    try:
        exemptions = parse_exemptions(load_json(args.exemptions), today=args.today)
        report = load_json(args.audit_json) if args.audit_json else run_pnpm_audit()
        violations, unused = evaluate_audit(
            report,
            exemptions,
            minimum_severity=args.minimum_severity,
        )
    except AuditValidationError as exc:
        print(f"Dependency audit validation failed: {exc}", file=sys.stderr)
        return 2

    print(f"pnpm production audit: {_vulnerability_summary(report)}")
    for item in unused:
        print(f"warning: 当前审计未命中豁免 {item}，可评估删除")
    if violations:
        print("Dependency audit gate failed:", file=sys.stderr)
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1
    print(
        f"Dependency audit gate passed "
        f"(minimum={args.minimum_severity}, active_exemptions={len(exemptions)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
