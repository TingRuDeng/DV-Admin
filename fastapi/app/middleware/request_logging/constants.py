"""
请求日志常量

集中声明默认排除路径，避免中间件主流程持有散落配置。
"""

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

EXCLUDED_BODY_PATHS: frozenset[str] = frozenset(
    {
        "/api/v1/auth/login",
        "/api/v1/auth/password",
        "/api/v1/oauth/login",
        "/api/v1/oauth/refresh-token",
        "/api/v1/information/password",
        "/api/v1/information/change-avatar",
        "/api/v1/files",
        "/api/v1/profile/avatar",
    }
)
