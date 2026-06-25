"""
数据库慢查询监控器

记录 ORM 或数据库适配层传入的查询耗时和统计信息。
"""

from typing import Any

from loguru import logger

from app.utils.logger import get_request_id

SLOW_QUERY_SQL_PREVIEW_LENGTH = 500
SLOW_QUERY_PARAMS_PREVIEW_LENGTH = 200


class DatabaseQueryMonitor:
    """监控和记录数据库慢查询。"""

    def __init__(
        self,
        slow_query_threshold_ms: int = 500,
        very_slow_query_threshold_ms: int = 2000,
    ):
        """初始化数据库慢查询阈值和统计计数。"""
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.very_slow_query_threshold_ms = very_slow_query_threshold_ms
        self._query_count = 0
        self._slow_query_count = 0
        self._very_slow_query_count = 0
        self._total_query_time_ms = 0

    def log_query(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        execution_time_ms: int = 0,
    ) -> None:
        """记录一次数据库查询，并在超过阈值时写慢查询日志。"""
        self._query_count += 1
        self._total_query_time_ms += execution_time_ms

        if execution_time_ms >= self.very_slow_query_threshold_ms:
            self._very_slow_query_count += 1
            self._log_query(sql, params, execution_time_ms, "very_slow")
            return

        if execution_time_ms >= self.slow_query_threshold_ms:
            self._slow_query_count += 1
            self._log_query(sql, params, execution_time_ms, "slow")

    def _log_query(
        self,
        sql: str,
        params: dict[str, Any] | None,
        execution_time_ms: int,
        level: str,
    ) -> None:
        """按慢查询等级输出数据库查询日志。"""
        threshold_ms = (
            self.very_slow_query_threshold_ms
            if level == "very_slow"
            else self.slow_query_threshold_ms
        )
        log_data = {
            "request_id": get_request_id(),
            "type": "slow_db_query",
            "level": level,
            "sql": sql[:SLOW_QUERY_SQL_PREVIEW_LENGTH],
            "params": str(params)[:SLOW_QUERY_PARAMS_PREVIEW_LENGTH] if params else None,
            "execution_time_ms": execution_time_ms,
            "threshold_ms": threshold_ms,
        }

        if level == "very_slow":
            logger.bind(**log_data).error(f"严重慢数据库查询: {execution_time_ms}ms")
            return

        logger.bind(**log_data).warning(f"慢数据库查询: {execution_time_ms}ms")

    def get_stats(self) -> dict[str, Any]:
        """获取数据库查询统计信息。"""
        return {
            "total_queries": self._query_count,
            "slow_queries": self._slow_query_count,
            "very_slow_queries": self._very_slow_query_count,
            "total_query_time_ms": self._total_query_time_ms,
            "avg_query_time_ms": (
                self._total_query_time_ms / self._query_count
                if self._query_count > 0
                else 0
            ),
            "slow_query_rate": (
                self._slow_query_count / self._query_count * 100
                if self._query_count > 0
                else 0
            ),
        }

    def reset_stats(self) -> None:
        """重置数据库查询统计信息。"""
        self._query_count = 0
        self._slow_query_count = 0
        self._very_slow_query_count = 0
        self._total_query_time_ms = 0


db_query_monitor = DatabaseQueryMonitor()
