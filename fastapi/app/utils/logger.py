"""
结构化日志工具模块

提供 JSON 格式的结构化日志功能，支持请求 ID 追踪。
"""

import json
import os
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from loguru import logger

# 请求 ID 上下文变量
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """获取当前请求 ID"""
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """设置当前请求 ID"""
    request_id_var.set(request_id)


def clear_request_id() -> None:
    """清除当前请求 ID"""
    request_id_var.set(None)


class JSONLogFormatter:
    """
    JSON 格式日志格式化器

    将日志输出为结构化的 JSON 格式，便于日志收集和分析。
    """

    def __init__(
        self,
        app_name: str = "DV-Admin",
        environment: str = "development",
        include_extra: bool = True,
    ):
        self.app_name = app_name
        self.environment = environment
        self.include_extra = include_extra

    def format(self, record: dict[str, Any]) -> str:
        """
        格式化日志记录为 JSON

        Args:
            record: loguru 日志记录字典

        Returns:
            JSON 格式的日志字符串
        """
        # 基础日志结构
        log_data = {
            "timestamp": datetime.fromtimestamp(record["time"].timestamp()).isoformat(),
            "level": record["level"].name,
            "level_no": record["level"].no,
            "message": record["message"],
            "logger": record["name"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
            "app": self.app_name,
            "env": self.environment,
        }

        # 添加请求 ID（如果存在）
        request_id = get_request_id()
        if request_id:
            log_data["request_id"] = request_id

        # 添加额外字段
        if self.include_extra and record.get("extra"):
            extra = record["extra"].copy()
            # 移除一些不需要的字段
            extra.pop("request_id", None)
            if extra:
                log_data["extra"] = extra

        # 添加异常信息
        if record["exception"]:
            log_data["exception"] = {
                "type": record["exception"].type.__name__ if record["exception"].type else None,
                "value": str(record["exception"].value) if record["exception"].value else None,
                "traceback": record["exception"].traceback if record["exception"].traceback else None,
            }

        return json.dumps(log_data, ensure_ascii=False, default=str)


def setup_logger(
    log_level: str = "INFO",
    log_format: str = "json",
    app_name: str = "DV-Admin",
    environment: str = "development",
    log_file: str | None = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """
    配置日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 日志格式 (json, text)
        app_name: 应用名称
        environment: 环境名称
        log_file: 日志文件路径（可选）
        rotation: 日志文件轮转大小
        retention: 日志文件保留时间
    """
    # 移除默认处理器
    logger.remove()
    is_test_env = environment.lower() in {"test", "testing"} or "PYTEST_CURRENT_TEST" in os.environ
    use_async_queue = not is_test_env

    # 根据格式配置处理器
    if log_format.lower() == "json":
        # JSON 格式
        formatter = JSONLogFormatter(
            app_name=app_name,
            environment=environment,
        )
        logger.add(
            sys.stdout,
            level=log_level,
            format=formatter.format,
            enqueue=use_async_queue,
            backtrace=True,
            diagnose=environment == "development",
        )
    else:
        # 文本格式（开发环境友好）
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "{extra[request_id] if extra.get('request_id') else '-'} | "
                   "<level>{message}</level>",
            enqueue=use_async_queue,
            backtrace=True,
            diagnose=environment == "development",
        )

    # 添加文件日志（如果指定）
    if log_file:
        if log_format.lower() == "json":
            formatter = JSONLogFormatter(
                app_name=app_name,
                environment=environment,
            )
            logger.add(
                log_file,
                level=log_level,
                format=formatter.format,
                rotation=rotation,
                retention=retention,
                enqueue=use_async_queue,
                compression="zip",
            )
        else:
            logger.add(
                log_file,
                level=log_level,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
                rotation=rotation,
                retention=retention,
                enqueue=use_async_queue,
                compression="zip",
            )


class RequestContextLogger:
    """
    请求上下文日志器

    提供带有请求上下文的日志记录功能。
    """

    def __init__(self, name: str = "app"):
        self.name = name
        self._logger = logger.bind(name=name)

    def _bind_context(self) -> "logger":
        """绑定请求上下文"""
        request_id = get_request_id()
        if request_id:
            return self._logger.bind(request_id=request_id)
        return self._logger

    def debug(self, message: str, **kwargs: Any) -> None:
        """记录 DEBUG 级别日志"""
        self._bind_context().debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """记录 INFO 级别日志"""
        self._bind_context().info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """记录 WARNING 级别日志"""
        self._bind_context().warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """记录 ERROR 级别日志"""
        self._bind_context().error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """记录 CRITICAL 级别日志"""
        self._bind_context().critical(message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """记录异常日志"""
        self._bind_context().exception(message, **kwargs)


def get_logger(name: str = "app") -> RequestContextLogger:
    """
    获取日志器实例

    Args:
        name: 日志器名称

    Returns:
        RequestContextLogger 实例
    """
    return RequestContextLogger(name)
