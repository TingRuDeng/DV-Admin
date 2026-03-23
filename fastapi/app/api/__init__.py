"""
API 路由模块

包含所有 API 路由的注册和配置。
"""

from app.api.v1 import router as api_v1_router

__all__ = ["api_v1_router"]
