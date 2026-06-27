from datetime import timedelta
from pathlib import Path
from typing import Any

CACHE_ALIASES = {
    "default": 0,
    "session": 1,
    "user_info": 2,
    "online_user": 3,
}
LOCAL_CACHE_LOCATIONS = {
    "default": "unique-default",
    "session": "unique-session",
    "user_info": "unique-user_info",
    "online_user": "unique-online_user",
}
LOG_FILE_MAX_BYTES = 1024 * 1024 * 50
LOG_FILE_BACKUP_COUNT = 5


def build_rest_framework_config() -> dict[str, Any]:
    """集中构建 DRF 配置，避免认证、分页和驼峰转换配置散落在 settings.py。"""
    return {
        "EXCEPTION_HANDLER": "drf_admin.utils.exceptions.exception_handler",
        "DEFAULT_PAGINATION_CLASS": "drf_admin.utils.pagination.GlobalPagination",
        "DEFAULT_PERMISSION_CLASSES": (
            "rest_framework.permissions.IsAuthenticated",
            "drf_admin.utils.permissions.RBACPermission",
        ),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
        "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
        "DEFAULT_THROTTLE_RATES": {
            "anon": "10/min",
        },
        "DEFAULT_RENDERER_CLASSES": (
            "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
            "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
        ),
        "DEFAULT_PARSER_CLASSES": (
            "djangorestframework_camel_case.parser.CamelCaseJSONParser",
            "djangorestframework_camel_case.parser.CamelCaseFormParser",
            "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        ),
        "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    }


def build_simple_jwt_config(access_minutes: int, refresh_days: int) -> dict[str, Any]:
    """根据环境变量数值构建 JWT 生命周期，保持 refresh token 轮换策略不变。"""
    return {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=access_minutes),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=refresh_days),
        "ROTATE_REFRESH_TOKENS": True,
        "BLACKLIST_AFTER_ROTATION": True,
    }


def build_base_api(api_version: str) -> str:
    """生成项目 API 前缀，保持版本为空时退回 api/ 的历史行为。"""
    if api_version:
        return f"api/{api_version}/"
    return "api/"


def build_white_list(base_api: str) -> list[str]:
    """按统一 API 前缀构建权限白名单。"""
    return [
        f"/{base_api}oauth/login/",
        f"/{base_api}oauth/logout/",
        f"/{base_api}oauth/info/",
        f"/{base_api}oauth/menus/routes/",
        f"/{base_api}oauth/refresh-token/",
        f"/{base_api}system/users/profile/",
        f"/{base_api}system/notices/my-page/",
        f"/{base_api}system/dict-items/",
    ]


def build_redis_auth_segment(redis_pwd: str) -> str:
    """按 Django Redis URL 规则构建密码片段，保持空密码不写入认证段。"""
    if redis_pwd:
        return f":{redis_pwd}@"
    return ""


def build_caches(redis_host: str, redis_port: int | None, redis_auth: str) -> dict[str, Any]:
    """根据 Redis 配置构建 Django 缓存，缺少主机或端口时保持本地缓存行为。"""
    if not redis_host or not redis_port:
        return _build_local_caches()

    return {
        alias: _build_redis_cache(redis_host, redis_port, redis_auth, db_index)
        for alias, db_index in CACHE_ALIASES.items()
    }


def build_channel_layers(
    redis_host: str, redis_port: int | None, redis_auth: str, secret_key: str
) -> dict[str, Any]:
    """根据 Redis 配置构建 Channels 层，缺少配置时使用内存层。"""
    if not redis_host or not redis_port:
        return {
            "default": {
                "BACKEND": "channels.layers.InMemoryChannelLayer",
                "CONFIG": {"capacity": 1500, "expiry": 10},
            }
        }

    return {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [f"redis://{redis_auth}{redis_host}:{redis_port}/4"],
                "symmetric_encryption_keys": [secret_key],
                "capacity": 1500,
                "expiry": 10,
            },
        }
    }


def build_logging_config(logs_dir: Path) -> dict[str, Any]:
    """构建 Django 日志配置，日志目录由 settings 负责提前创建。"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _build_log_formatters(),
        "filters": _build_log_filters(),
        "handlers": _build_log_handlers(logs_dir),
        "loggers": _build_loggers(),
    }


def _build_redis_cache(
    redis_host: str, redis_port: int, redis_auth: str, db_index: int
) -> dict[str, Any]:
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{redis_auth}{redis_host}:{redis_port}/{db_index}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }


def _build_local_caches() -> dict[str, Any]:
    return {
        alias: {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": location,
        }
        for alias, location in LOCAL_CACHE_LOCATIONS.items()
    }


def _build_log_formatters() -> dict[str, Any]:
    return {
        "standard": {
            "format": "[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d]==>[%(message)s]"
        },
        "simple": {"format": "[%(asctime)s][%(levelname)s]==>[%(message)s]"},
    }


def _build_log_filters() -> dict[str, Any]:
    return {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    }


def _build_log_handlers(logs_dir: Path) -> dict[str, Any]:
    return {
        "default": _build_rotating_handler(logs_dir, "admin_info.log", "INFO", "standard"),
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "operation": _build_rotating_handler(
            logs_dir, "admin_operation.log", "INFO", "simple"
        ),
        "query": _build_rotating_handler(logs_dir, "admin_query.log", "INFO", "simple"),
        "error": _build_rotating_handler(logs_dir, "admin_error.log", "ERROR", "standard"),
    }


def _build_rotating_handler(
    logs_dir: Path, filename: str, level: str, formatter: str
) -> dict[str, Any]:
    return {
        "level": level,
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(logs_dir / filename),
        "maxBytes": LOG_FILE_MAX_BYTES,
        "backupCount": LOG_FILE_BACKUP_COUNT,
        "formatter": formatter,
        "encoding": "utf-8",
    }


def _build_loggers() -> dict[str, Any]:
    return {
        "info": {
            "handlers": ["default", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "operation": {
            "handlers": ["operation"],
            "level": "INFO",
            "propagate": True,
        },
        "query": {
            "handlers": ["query", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "error": {
            "handlers": ["error", "console"],
            "level": "ERROR",
            "propagate": True,
        },
    }
