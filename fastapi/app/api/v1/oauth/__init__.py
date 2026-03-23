"""
认证授权 API 模块

包含登录、登出、Token 刷新等认证相关接口。
"""

from app.api.v1.oauth.auth import router as auth_router
from fastapi import APIRouter

router = APIRouter(prefix="/oauth", tags=["认证授权"])

router.include_router(auth_router)
