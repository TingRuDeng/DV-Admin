"""
用户管理 API 聚合入口
"""

from fastapi import APIRouter

from app.api.v1.system.user_routes.import_export import (
    export_users,
    get_import_template,
    import_users,
)
from app.api.v1.system.user_routes.import_export import router as import_export_router
from app.api.v1.system.user_routes.mutation import router as mutation_router
from app.api.v1.system.user_routes.password import reset_user_password
from app.api.v1.system.user_routes.password import router as password_router
from app.api.v1.system.user_routes.query import router as query_router

__all__ = [
    "export_users",
    "get_import_template",
    "import_users",
    "reset_user_password",
    "router",
]

router = APIRouter()

router.include_router(query_router)
router.include_router(mutation_router)
router.include_router(password_router)
router.include_router(import_export_router)
