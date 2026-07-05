#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Sequence

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from scripts.api_endpoint_contracts import assert_endpoint_contract_catalog, iter_critical_endpoint_contracts

REPORT_PATH = Path("docs/api-contract-report.json")
REPORT_SCHEMA_VERSION = 1


def build_report() -> dict[str, Any]:
    """从关键端点契约目录生成稳定报告。"""
    assert_endpoint_contract_catalog()
    endpoints = []
    for contract in iter_critical_endpoint_contracts():
        endpoints.append(
            {
                "key": contract.key,
                "method": contract.method,
                "path": contract.path,
                "auth_required": contract.auth_required,
                "paginated": contract.paginated,
                "request_fields": list(contract.request_fields),
                "query_params": list(contract.query_params),
                "response_fields": list(contract.response_fields),
                "permissions": list(contract.permissions),
                "evidence_files": sorted({evidence.file for evidence in contract.evidence}),
            }
        )

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source": "scripts/api_endpoint_contracts.py",
        "endpoint_count": len(endpoints),
        "paginated_count": sum(1 for endpoint in endpoints if endpoint["paginated"]),
        "authenticated_count": sum(1 for endpoint in endpoints if endpoint["auth_required"]),
        "methods": sorted({endpoint["method"] for endpoint in endpoints}),
        "endpoints": endpoints,
    }


def serialize_report(report: dict[str, Any]) -> str:
    """按固定格式序列化，便于 diff 和校验。"""
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_report(root: Path) -> Path:
    """写入 API 契约报告。"""
    target = root / REPORT_PATH
    target.write_text(serialize_report(build_report()), encoding="utf-8")
    return target


def main(argv: Sequence[str] | None = None) -> int:
    """命令行入口。"""
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]).resolve() if args else Path.cwd().resolve()
    target = write_report(root)
    print(target.relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
