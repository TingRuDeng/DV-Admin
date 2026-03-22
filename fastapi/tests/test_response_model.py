# -*- coding: utf-8 -*-
"""
响应模型测试
测试 ResponseModel 的功能
"""
import pytest

from app.schemas.base import ResponseModel


class TestResponseModel:
    """测试响应模型"""

    def test_success_with_data(self):
        """测试成功响应带数据"""
        data = {"id": 1, "name": "test"}
        response = ResponseModel.success(data=data)
        
        assert response.code == 20000
        assert response.message == "success"
        assert response.data == data

    def test_success_with_message(self):
        """测试成功响应带自定义消息"""
        response = ResponseModel.success(data=None, message="操作成功")
        
        assert response.code == 20000
        assert response.message == "操作成功"

    def test_error_default(self):
        """测试错误响应默认值"""
        response = ResponseModel.error()
        
        assert response.code == 500
        assert response.message == "error"
        assert response.data is None

    def test_error_custom(self):
        """测试错误响应自定义"""
        response = ResponseModel.error(code=400, message="参数错误")
        
        assert response.code == 400
        assert response.message == "参数错误"

    def test_error_with_code(self):
        """测试错误响应带状态码"""
        response = ResponseModel.error(code=404, message="资源不存在")
        
        assert response.code == 404
        assert response.message == "资源不存在"


class TestPageQuery:
    """测试分页查询参数"""

    def test_offset_first_page(self):
        """测试第一页偏移量"""
        from app.schemas.base import PageQuery
        
        query = PageQuery(page=1, page_size=10)
        assert query.offset == 0

    def test_offset_second_page(self):
        """测试第二页偏移量"""
        from app.schemas.base import PageQuery
        
        query = PageQuery(page=2, page_size=10)
        assert query.offset == 10

    def test_offset_custom_page_size(self):
        """测试自定义每页数量"""
        from app.schemas.base import PageQuery
        
        query = PageQuery(page=3, page_size=20)
        assert query.offset == 40

    def test_default_values(self):
        """测试默认值"""
        from app.schemas.base import PageQuery
        
        query = PageQuery()
        assert query.page == 1
        assert query.page_size == 10
        assert query.search is None
        assert query.ordering is None
