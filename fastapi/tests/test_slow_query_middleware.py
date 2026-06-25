"""
慢查询中间件测试

覆盖慢请求统计、排除路径隔离和数据库慢查询监控器行为。
"""

from collections.abc import Iterable

import pytest
from fastapi import Response
from starlette.requests import Request

from app.middleware.slow_query import (
    DatabaseQueryMonitor,
    SlowQueryMiddleware,
    db_query_monitor,
)
from app.middleware.slow_query_middleware import DatabaseQueryMonitor as CompatDatabaseQueryMonitor
from app.middleware.slow_query_middleware import SlowQueryMiddleware as CompatSlowQueryMiddleware
from app.middleware.slow_query_middleware import db_query_monitor as compat_db_query_monitor


def make_request(path: str = "/api/v1/demo") -> Request:
    """构造最小 HTTP 请求对象。"""
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "scheme": "http",
        }
    )


def patch_time(monkeypatch: pytest.MonkeyPatch, values: Iterable[float]) -> None:
    """按顺序替换慢请求中间件使用的时间来源。"""
    from app.middleware.slow_query import request as request_module

    value_iter = iter(values)
    monkeypatch.setattr(request_module.time, "time", lambda: next(value_iter))


@pytest.mark.asyncio
async def test_slow_request_stats_are_recorded(monkeypatch: pytest.MonkeyPatch):
    """慢请求应计入总请求和慢请求统计。"""
    middleware = SlowQueryMiddleware(
        lambda _scope, _receive, _send: None,
        slow_threshold_ms=10,
        very_slow_threshold_ms=100,
    )
    patch_time(monkeypatch, [0.0, 0.02])

    async def call_next(_request: Request) -> Response:
        return Response(status_code=204)

    response = await middleware.dispatch(make_request(), call_next)

    assert response.status_code == 204
    assert middleware.get_stats() == {
        "total_requests": 1,
        "slow_requests": 1,
        "very_slow_requests": 0,
        "slow_threshold_ms": 10,
        "very_slow_threshold_ms": 100,
        "slow_rate": 100.0,
    }


@pytest.mark.asyncio
async def test_excluded_path_does_not_update_stats():
    """跳过路径不应参与慢请求统计。"""
    middleware = SlowQueryMiddleware(lambda _scope, _receive, _send: None)

    async def call_next(_request: Request) -> Response:
        return Response(status_code=200)

    await middleware.dispatch(make_request("/health"), call_next)

    assert middleware.get_stats()["total_requests"] == 0


def test_custom_excluded_paths_do_not_leak_between_instances():
    """自定义跳过路径只影响当前中间件实例。"""
    first = SlowQueryMiddleware(
        lambda _scope, _receive, _send: None,
        exclude_paths=["/api/v1/private"],
    )
    second = SlowQueryMiddleware(lambda _scope, _receive, _send: None)

    assert first._should_skip("/api/v1/private/token") is True
    assert second._should_skip("/api/v1/private/token") is False


def test_database_query_monitor_records_stats():
    """数据库慢查询监控器应记录普通、慢和非常慢查询统计。"""
    monitor = DatabaseQueryMonitor(
        slow_query_threshold_ms=10,
        very_slow_query_threshold_ms=20,
    )

    monitor.log_query("select 1", execution_time_ms=5)
    monitor.log_query("select 2", execution_time_ms=10)
    monitor.log_query("select 3", {"name": "alice"}, execution_time_ms=30)

    stats = monitor.get_stats()

    assert {
        key: value
        for key, value in stats.items()
        if key != "slow_query_rate"
    } == {
        "total_queries": 3,
        "slow_queries": 1,
        "very_slow_queries": 1,
        "total_query_time_ms": 45,
        "avg_query_time_ms": 15.0,
    }
    assert stats["slow_query_rate"] == pytest.approx(100 / 3)

    monitor.reset_stats()

    assert monitor.get_stats()["total_queries"] == 0


def test_compat_imports_point_to_split_implementations():
    """历史导入路径应继续导出拆分后的实现。"""
    assert CompatSlowQueryMiddleware is SlowQueryMiddleware
    assert CompatDatabaseQueryMonitor is DatabaseQueryMonitor
    assert compat_db_query_monitor is db_query_monitor
