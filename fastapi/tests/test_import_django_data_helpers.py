"""
Django 数据导入 helper 测试

覆盖导入模块公开辅助入口存在性。
"""

import pytest


@pytest.mark.asyncio
async def test_init_function_exists(db):
    """初始化函数必须保持可调用。"""
    from app.db.import_django_data import init

    assert callable(init)


@pytest.mark.asyncio
async def test_import_data_function_exists(db):
    """导入函数必须保持可调用。"""
    from app.db.import_django_data import import_data

    assert callable(import_data)


@pytest.mark.asyncio
async def test_main_function_exists(db):
    """主函数必须保持可调用。"""
    from app.db.import_django_data import main

    assert callable(main)
