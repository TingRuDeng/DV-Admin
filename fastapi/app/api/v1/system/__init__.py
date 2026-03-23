"""
系统管理 API 模块

包含用户、角色、部门、菜单、字典等系统管理接口。
"""

from app.api.v1.system.depts import router as depts_router
from app.api.v1.system.dict_items import router as dict_items_router
from app.api.v1.system.dicts import router as dicts_router
from app.api.v1.system.logs import router as logs_router
from app.api.v1.system.menus import router as menus_router
from app.api.v1.system.notices import router as notices_router
from app.api.v1.system.roles import router as roles_router
from app.api.v1.system.users import router as users_router
from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["系统管理"])

router.include_router(users_router, prefix="/users")
router.include_router(roles_router, prefix="/roles")
router.include_router(menus_router, prefix="/menus")
router.include_router(depts_router, prefix="/departments")
router.include_router(dicts_router, prefix="/dicts")
router.include_router(dict_items_router, prefix="/dict-items")
router.include_router(notices_router, prefix="/notices")
router.include_router(logs_router, prefix="/logs")
