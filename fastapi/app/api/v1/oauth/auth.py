"""
认证 API 路由聚合入口。

保留历史 `app.api.v1.oauth.auth.router` 导入路径，实际端点按职责拆分到
`app.api.v1.oauth.routes` 子模块。
"""

from fastapi import APIRouter

from app.api.v1.oauth.routes.captcha import get_captcha
from app.api.v1.oauth.routes.captcha import router as captcha_router
from app.api.v1.oauth.routes.login import login, login_access_token
from app.api.v1.oauth.routes.login import router as login_router
from app.api.v1.oauth.routes.menus import get_user_menus
from app.api.v1.oauth.routes.menus import router as menus_router
from app.api.v1.oauth.routes.profile import get_current_user_info
from app.api.v1.oauth.routes.profile import router as profile_router
from app.api.v1.oauth.routes.session import logout, refresh_token
from app.api.v1.oauth.routes.session import router as session_router

router = APIRouter()
router.include_router(login_router)
router.include_router(session_router)
router.include_router(profile_router)
router.include_router(menus_router)
router.include_router(captcha_router)

__all__ = [
    "get_captcha",
    "get_current_user_info",
    "get_user_menus",
    "login",
    "login_access_token",
    "logout",
    "refresh_token",
    "router",
]
