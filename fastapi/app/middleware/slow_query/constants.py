"""
慢查询监控常量

集中声明默认阈值和跳过路径，避免请求中间件持有散落配置。
"""

DEFAULT_SLOW_THRESHOLD_MS = 1000
DEFAULT_VERY_SLOW_THRESHOLD_MS = 5000

EXCLUDED_PATHS: frozenset[str] = frozenset(
    {
        "/api/swagger",
        "/api/redoc",
        "/api/openapi.json",
        "/health",
        "/favicon.ico",
        "/media",
    }
)
