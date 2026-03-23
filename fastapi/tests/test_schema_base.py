"""
Schema 基类测试
测试 base schema 的功能
"""

from app.schemas.base import PageResult


class TestPageResult:
    """测试分页结果"""

    def test_create_basic(self):
        """测试基本创建"""
        result = PageResult.create(
            total=100,
            page=1,
            page_size=10,
            results=[1, 2, 3],
        )

        assert result.total == 100
        assert result.page == 1
        assert result.page_size == 10
        assert result.list == [1, 2, 3]
        assert result.total_pages == 10

    def test_create_empty(self):
        """测试空结果"""
        result = PageResult.create(
            total=0,
            page=1,
            page_size=10,
            results=[],
        )

        assert result.total == 0
        assert result.total_pages == 0

    def test_create_single_page(self):
        """测试单页结果"""
        result = PageResult.create(
            total=5,
            page=1,
            page_size=10,
            results=[1, 2, 3, 4, 5],
        )

        assert result.total_pages == 1

    def test_create_exact_pages(self):
        """测试正好整除的页数"""
        result = PageResult.create(
            total=20,
            page=1,
            page_size=10,
            results=[],
        )

        assert result.total_pages == 2

    def test_create_with_remainder(self):
        """测试有余数的页数"""
        result = PageResult.create(
            total=25,
            page=1,
            page_size=10,
            results=[],
        )

        assert result.total_pages == 3
