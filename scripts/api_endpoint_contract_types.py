from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractEvidence:
    """端点契约对应的代码或文档证据。"""

    file: str
    snippets: tuple[str, ...]


@dataclass(frozen=True)
class EndpointContract:
    """关键端点的共享契约，用于锁定前端、Django 与 FastAPI 的共同边界。"""

    key: str
    method: str
    path: str
    auth_required: bool
    request_fields: tuple[str, ...] = ()
    query_params: tuple[str, ...] = ()
    response_fields: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    paginated: bool = False
    evidence: tuple[ContractEvidence, ...] = ()
