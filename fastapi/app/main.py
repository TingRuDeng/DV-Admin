# -*- coding: utf-8 -*-
"""
DV-Admin FastAPI 主应用入口

基于 FastAPI + Tortoise ORM 的异步后端服务。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from tortoise.contrib.fastapi import register_tortoise

from app.api.health import router as health_router
from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    APIException,
    AuthenticationError,
    PermissionDenied,
    ValidationError,
    api_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.redis import redis_manager
from app.middleware import RequestLoggingMiddleware, SlowQueryMiddleware
from app.utils.logger import setup_logger
from app.core.cache import cache_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    在应用启动时初始化资源，在应用关闭时清理资源。
    """
    # 启动时初始化
    # 初始化日志系统
    setup_logger(
        log_level=settings.log_level,
        log_format=settings.log_format,
        app_name=settings.app_name,
        environment=settings.app_env,
        log_file=settings.log_file,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
    )
    logger.info("应用启动中...")

    # 初始化 Redis 连接
    try:
        await redis_manager.init()
        logger.info("Redis 连接初始化成功")
    except Exception as e:
        logger.warning(f"Redis 连接初始化失败: {e}，Token 黑名单功能将不可用")

    # 初始化缓存服务
    try:
        await cache_service.init()
        logger.info("缓存服务初始化成功")
    except Exception as e:
        logger.warning(f"缓存服务初始化失败: {e}")

    yield

    # 关闭时清理
    logger.info("应用关闭中...")

    # 关闭 Redis 连接
    try:
        await redis_manager.close()
        logger.info("Redis 连接已关闭")
    except Exception as e:
        logger.error(f"关闭 Redis 连接时出错: {e}")


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例
    """
    app = FastAPI(
        title=settings.app_name,
        description="DV-Admin FastAPI 后端服务",
        version=settings.version,
        docs_url="/api/swagger/",
        redoc_url="/api/redoc/",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # 注册 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册慢查询日志中间件（在请求日志中间件之前）
    app.add_middleware(
        SlowQueryMiddleware,
        slow_threshold_ms=settings.slow_query_threshold_ms,
        very_slow_threshold_ms=settings.very_slow_query_threshold_ms,
    )

    # 注册请求日志中间件
    app.add_middleware(
        RequestLoggingMiddleware,
        log_request_body=True,
        log_response_body=False,
        max_body_length=1000,
    )

    # 挂载静态文件目录
    import os
    if not os.path.exists(settings.upload_dir):
        os.makedirs(settings.upload_dir)
    app.mount("/media", StaticFiles(directory=settings.upload_dir), name="media")

    # 注册异常处理器
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(AuthenticationError, api_exception_handler)
    app.add_exception_handler(PermissionDenied, api_exception_handler)
    app.add_exception_handler(ValidationError, api_exception_handler)
    app.add_exception_handler(status.HTTP_422_UNPROCESSABLE_CONTENT, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 注册 API 路由
    app.include_router(api_v1_router)

    # 注册健康检查路由（不使用 /api 前缀）
    app.include_router(health_router)

    # 根路径
    @app.get("/", tags=["根路径"])
    async def root():
        """根路径"""
        return {
            "name": settings.app_name,
            "version": settings.version,
            "docs": "/api/swagger",
        }

    # 注册 Tortoise ORM
    register_tortoise(
        app,
        config=settings.tortoise_orm_config,
        generate_schemas=settings.is_development,
        add_exception_handlers=True,
    )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )
