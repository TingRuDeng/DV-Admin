# -*- coding: utf-8 -*-
"""
健康检查路由模块

提供服务健康检查、就绪检查和存活检查端点。
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, status
from loguru import logger
from pydantic import BaseModel
from tortoise import Tortoise

from app.core.config import settings

router = APIRouter(tags=["健康检查"])


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str
    version: str
    timestamp: str
    app_name: str
    environment: str


class ReadyResponse(BaseModel):
    """就绪检查响应模型"""

    status: str
    version: str
    timestamp: str
    checks: Dict[str, Any]


class LiveResponse(BaseModel):
    """存活检查响应模型"""

    status: str
    timestamp: str


async def check_database() -> Dict[str, Any]:
    """
    检查数据库连接状态

    Returns:
        包含数据库状态信息的字典
    """
    try:
        # 使用 Tortoise ORM 执行简单查询测试连接
        conn = Tortoise.get_connection("default")
        if settings.is_sqlite:
            await conn.execute_query("SELECT 1")
        else:
            await conn.execute_query("SELECT 1")

        return {
            "status": "healthy",
            "type": "sqlite" if settings.is_sqlite else "mysql",
            "message": "数据库连接正常",
        }
    except Exception as e:
        logger.error(f"数据库连接检查失败: {e}")
        return {
            "status": "unhealthy",
            "type": "sqlite" if settings.is_sqlite else "mysql",
            "message": f"数据库连接失败: {str(e)}",
        }


async def check_redis() -> Optional[Dict[str, Any]]:
    """
    检查 Redis 连接状态

    Returns:
        包含 Redis 状态信息的字典，如果未配置则返回 None
    """
    # 检查是否配置了 Redis（非默认值）
    if not settings.redis_url or settings.redis_url == "redis://localhost:6379/0":
        # 如果是默认配置且没有实际使用，返回未配置状态
        return {
            "status": "not_configured",
            "message": "Redis 未配置或使用默认配置",
        }

    try:
        # 尝试导入 Redis 客户端
        import redis.asyncio as redis

        # 创建 Redis 客户端
        client = redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            encoding="utf-8",
            decode_responses=True,
        )

        # 执行 PING 命令测试连接
        await client.ping()
        await client.close()

        return {
            "status": "healthy",
            "message": "Redis 连接正常",
        }
    except ImportError:
        return {
            "status": "unavailable",
            "message": "Redis 库未安装",
        }
    except Exception as e:
        logger.error(f"Redis 连接检查失败: {e}")
        return {
            "status": "unhealthy",
            "message": f"Redis 连接失败: {str(e)}",
        }


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="基本健康检查",
    description="返回服务基本健康状态信息",
)
async def health_check() -> HealthResponse:
    """
    基本健康检查端点

    返回服务的基本健康状态，包括版本号和环境信息。
    此端点用于快速检查服务是否运行。
    """
    return HealthResponse(
        status="healthy",
        version=settings.version,
        timestamp=datetime.utcnow().isoformat() + "Z",
        app_name=settings.app_name,
        environment=settings.app_env,
    )


@router.get(
    "/health/ready",
    response_model=ReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="就绪检查",
    description="检查服务是否已准备好接收请求（包括数据库、Redis 等依赖）",
)
async def readiness_check() -> ReadyResponse:
    """
    就绪检查端点

    检查服务是否已准备好接收请求，包括：
    - 数据库连接状态
    - Redis 连接状态（如果配置了）

    如果所有关键依赖都正常，返回 200 状态码。
    如果有关键依赖失败，返回 503 状态码。
    """
    checks: Dict[str, Any] = {}

    # 检查数据库
    db_status = await check_database()
    checks["database"] = db_status

    # 检查 Redis
    redis_status = await check_redis()
    if redis_status:
        checks["redis"] = redis_status

    # 判断整体状态
    # 数据库是关键依赖，必须健康
    all_healthy = db_status["status"] == "healthy"

    # Redis 如果配置了，也应该是健康的（但不影响整体状态，除非是 unhealthy）
    if redis_status and redis_status["status"] == "unhealthy":
        all_healthy = False

    overall_status = "ready" if all_healthy else "not_ready"

    return ReadyResponse(
        status=overall_status,
        version=settings.version,
        timestamp=datetime.utcnow().isoformat() + "Z",
        checks=checks,
    )


@router.get(
    "/health/live",
    response_model=LiveResponse,
    status_code=status.HTTP_200_OK,
    summary="存活检查",
    description="检查服务进程是否存活",
)
async def liveness_check() -> LiveResponse:
    """
    存活检查端点

    检查服务进程是否存活。
    如果此端点返回 200，说明服务正在运行。
    此端点用于 Kubernetes 等容器编排系统的存活探针。
    """
    return LiveResponse(
        status="alive",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
