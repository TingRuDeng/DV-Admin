"""
API v1 版本路由

包含所有 v1 版本的 API 路由。
"""

from app.api.v1 import files, information, oauth, system
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

router.include_router(oauth.router)
router.include_router(system.router)
router.include_router(information.router)
router.include_router(files.router)
