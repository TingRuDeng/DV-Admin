from pathlib import Path

from drf_admin.settings_helpers import (
    LOG_FILE_BACKUP_COUNT,
    LOG_FILE_MAX_BYTES,
    build_base_api,
    build_caches,
    build_channel_layers,
    build_logging_config,
    build_redis_auth_segment,
    build_rest_framework_config,
    build_simple_jwt_config,
    build_white_list,
)


def test_build_rest_framework_config_keeps_auth_and_camel_case_boundaries():
    """DRF 配置拆分后必须保留 RBAC、JWT 和驼峰转换边界。"""
    rest_framework = build_rest_framework_config()

    assert rest_framework["DEFAULT_PERMISSION_CLASSES"] == (
        "rest_framework.permissions.IsAuthenticated",
        "drf_admin.utils.permissions.RBACPermission",
    )
    assert rest_framework["DEFAULT_AUTHENTICATION_CLASSES"] == (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
    assert "djangorestframework_camel_case.render.CamelCaseJSONRenderer" in (
        rest_framework["DEFAULT_RENDERER_CLASSES"]
    )
    assert "djangorestframework_camel_case.parser.CamelCaseJSONParser" in (
        rest_framework["DEFAULT_PARSER_CLASSES"]
    )


def test_build_simple_jwt_config_keeps_lifetime_and_rotation_policy():
    """JWT 生命周期来自环境数值，刷新令牌轮换和黑名单策略保持不变。"""
    simple_jwt = build_simple_jwt_config(30, 1)

    assert simple_jwt["ACCESS_TOKEN_LIFETIME"].total_seconds() == 1800
    assert simple_jwt["REFRESH_TOKEN_LIFETIME"].days == 1
    assert simple_jwt["ROTATE_REFRESH_TOKENS"] is True
    assert simple_jwt["BLACKLIST_AFTER_ROTATION"] is True


def test_build_base_api_keeps_versioned_and_unversioned_prefix():
    """API 前缀必须保持有版本和无版本两种历史行为。"""
    assert build_base_api("v1") == "api/v1/"
    assert build_base_api("") == "api/"


def test_build_white_list_uses_base_api_prefix_for_public_endpoints():
    """权限白名单必须继续跟随统一 API 前缀。"""
    white_list = build_white_list("api/v1/")

    assert white_list == [
        "/api/v1/oauth/login/",
        "/api/v1/oauth/logout/",
        "/api/v1/oauth/info/",
        "/api/v1/oauth/menus/routes/",
        "/api/v1/oauth/refresh-token/",
        "/api/v1/system/users/profile/",
        "/api/v1/system/notices/my-page/",
        "/api/v1/system/dict-items/",
    ]


def test_build_redis_auth_segment_keeps_empty_password_without_auth():
    """空 Redis 密码不能生成认证片段，避免改变无密码环境的连接 URL。"""
    assert build_redis_auth_segment("") == ""


def test_build_redis_auth_segment_wraps_password_for_url():
    """有 Redis 密码时保持原 settings.py 中的 URL 认证格式。"""
    assert build_redis_auth_segment("secret") == ":secret@"


def test_build_caches_uses_local_cache_when_redis_missing():
    """缺少 Redis 主机或端口时，缓存别名继续指向本地内存缓存。"""
    caches = build_caches("", None, "")

    assert caches["default"]["BACKEND"] == "django.core.cache.backends.locmem.LocMemCache"
    assert caches["default"]["LOCATION"] == "unique-default"
    assert caches["session"]["LOCATION"] == "unique-session"
    assert caches["user_info"]["LOCATION"] == "unique-user_info"
    assert caches["online_user"]["LOCATION"] == "unique-online_user"


def test_build_caches_uses_distinct_redis_databases():
    """Redis 缓存必须继续按别名分配不同 db，避免 session 与业务缓存互相污染。"""
    caches = build_caches("localhost", 6379, ":secret@")

    assert caches["default"]["LOCATION"] == "redis://:secret@localhost:6379/0"
    assert caches["session"]["LOCATION"] == "redis://:secret@localhost:6379/1"
    assert caches["user_info"]["LOCATION"] == "redis://:secret@localhost:6379/2"
    assert caches["online_user"]["LOCATION"] == "redis://:secret@localhost:6379/3"


def test_build_channel_layers_uses_memory_layer_when_redis_missing():
    """缺少 Redis 配置时，Channels 继续使用内存层。"""
    channel_layers = build_channel_layers("", None, "", "secret-key")

    assert (
        channel_layers["default"]["BACKEND"] == "channels.layers.InMemoryChannelLayer"
    )
    assert channel_layers["default"]["CONFIG"] == {"capacity": 1500, "expiry": 10}


def test_build_channel_layers_uses_redis_database_four():
    """Channels 使用独立 Redis db 4，并继续配置对称加密密钥。"""
    channel_layers = build_channel_layers("localhost", 6379, ":secret@", "secret-key")

    config = channel_layers["default"]["CONFIG"]
    assert channel_layers["default"]["BACKEND"] == "channels_redis.core.RedisChannelLayer"
    assert config["hosts"] == ["redis://:secret@localhost:6379/4"]
    assert config["symmetric_encryption_keys"] == ["secret-key"]
    assert config["capacity"] == 1500
    assert config["expiry"] == 10


def test_build_logging_config_keeps_rotating_file_handlers(tmp_path: Path):
    """日志配置拆分后必须保留原文件名、轮转大小和备份数量。"""
    logging_config = build_logging_config(tmp_path)

    handlers = logging_config["handlers"]
    assert handlers["default"]["filename"] == str(tmp_path / "admin_info.log")
    assert handlers["operation"]["filename"] == str(tmp_path / "admin_operation.log")
    assert handlers["query"]["filename"] == str(tmp_path / "admin_query.log")
    assert handlers["error"]["filename"] == str(tmp_path / "admin_error.log")
    assert handlers["default"]["maxBytes"] == LOG_FILE_MAX_BYTES
    assert handlers["default"]["backupCount"] == LOG_FILE_BACKUP_COUNT
    assert handlers["console"]["filters"] == ["require_debug_true"]
