"""
日志服务时间辅助函数测试。
"""
from datetime import datetime, timezone

from app.services.system.log_service import local_now, normalize_local_time


class TestLogServiceTimeHelpers:
    """测试日志时间转换辅助函数。"""

    def test_normalize_local_time_converts_utc_to_shanghai_naive(self):
        """UTC aware 时间要转换为上海本地 naive 时间，避免前端显示少 8 小时。"""
        utc_time = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        result = normalize_local_time(utc_time)

        assert result == datetime(2026, 1, 1, 8, 0, 0)
        assert result.tzinfo is None

    def test_local_now_returns_naive_datetime(self):
        """当前业务时间沿用 ORM 的本地 naive 契约。"""
        result = local_now()

        assert result.tzinfo is None
