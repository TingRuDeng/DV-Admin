"""
操作日志路由聚合入口。
"""
from fastapi import APIRouter

from app.api.v1.system.log_routes.analytics import router as analytics_router
from app.api.v1.system.log_routes.mutation import router as mutation_router
from app.api.v1.system.log_routes.query import router as query_router

router = APIRouter()
router.include_router(analytics_router)
router.include_router(query_router)
router.include_router(mutation_router)
