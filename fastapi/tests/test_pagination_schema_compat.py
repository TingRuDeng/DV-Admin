"""
Pagination schema backward-compatibility tests.
"""

from app.schemas.base import PageResult
from app.schemas.system import (
    NoticeAdminPageResult,
    NoticeMyPageOut,
    NoticeMyPageResult,
    NoticePageOut,
    OperationLogOut,
    OperationLogPageResult,
)


class TestPaginationSchemaCompat:
    """Ensure internal legacy accessors still work while API stays list/total."""

    def test_page_result_exposes_legacy_accessors(self):
        result = PageResult.create(total=3, page=1, page_size=10, results=[1, 2, 3])

        assert result.list == [1, 2, 3]
        assert result.total == 3
        assert result.results == [1, 2, 3]
        assert result.count == 3

    def test_notice_page_results_expose_legacy_accessors(self):
        admin_item = NoticePageOut(id=1, title="系统通知")
        my_item = NoticeMyPageOut(id=2, title="我的通知", is_read=1)

        admin_page = NoticeAdminPageResult(list=[admin_item], total=1)
        my_page = NoticeMyPageResult(list=[my_item], total=1)

        assert admin_page.results == [admin_item]
        assert admin_page.count == 1
        assert my_page.results == [my_item]
        assert my_page.count == 1

    def test_operation_log_page_result_exposes_legacy_accessors(self):
        log_item = OperationLogOut(
            id=1,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        page = OperationLogPageResult(list=[log_item], total=1)

        assert page.results == [log_item]
        assert page.count == 1
