"""分页查询参数依赖。"""

from dataclasses import dataclass

from fastapi import Query


@dataclass(frozen=True)
class PaginationParams:
    """标准分页参数。"""

    page: int
    page_size: int


def page_params(
    page_num: int | None = Query(None, alias="pageNum", ge=1, description="页码"),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页数量"),
    legacy_page: int | None = Query(None, alias="page", ge=1, include_in_schema=False),
) -> PaginationParams:
    """解析对外 pageNum/pageSize，并短期兼容旧 page 参数。"""
    return PaginationParams(page=page_num or legacy_page or 1, page_size=page_size)
