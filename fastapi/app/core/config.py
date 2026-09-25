"""
应用配置模块

使用 Pydantic Settings 管理应用配置，支持环境变量和 .env 文件。
"""

import secrets
import warnings
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from tortoise.backends.base.config_generator import expand_db_url

from app.core.oidc_policy import DEFAULT_SCOPES, settings_errors
from app.core.password_policy import validate_bounds
from app.core.security_validator import SecurityValidator


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )

    # 应用基础配置
    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="DV-Admin FastAPI", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")
    version: str = "0.1.0"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8769
    workers: int = 1
    trusted_proxy_ips: str = Field(default="", alias="TRUSTED_PROXY_IPS")

    # 数据库配置 - 默认为 SQLite
    database_url: str = Field(
        default="sqlite://./dv_admin.db",
        alias="DATABASE_URL",
    )
    database_min_connections: int = Field(default=1, alias="DATABASE_MIN_CONNECTIONS")
    database_max_connections: int = Field(default=10, alias="DATABASE_MAX_CONNECTIONS")

    # Redis 配置
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_password: str | None = Field(default=None, alias="REDIS_PASSWORD")

    # JWT 配置
    # 生产环境必须通过环境变量设置 SECRET_KEY
    # 开发环境如果未设置，将自动生成临时密钥
    _actual_secret_key: str | None = None  # 实际使用的密钥（可能是自动生成的）
    secret_key: str | None = Field(default=None, alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # 密码配置
    password_min_length: int = Field(default=15, alias="PASSWORD_MIN_LENGTH", ge=15, le=128)
    password_max_length: int = Field(default=128, alias="PASSWORD_MAX_LENGTH", ge=15, le=128)
    default_password: str = Field(alias="DEFAULT_PASSWORD")  # 新增/重置用户使用的显式默认密码

    # 分页配置
    default_page_size: int = Field(default=10, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, alias="MAX_PAGE_SIZE")

    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    log_file: str | None = Field(default=None, alias="LOG_FILE")
    log_rotation: str = Field(default="10 MB", alias="LOG_ROTATION")
    log_retention: str = Field(default="7 days", alias="LOG_RETENTION")

    # 慢查询配置
    slow_query_threshold_ms: int = Field(default=1000, alias="SLOW_QUERY_THRESHOLD_MS")
    very_slow_query_threshold_ms: int = Field(default=5000, alias="VERY_SLOW_QUERY_THRESHOLD_MS")
    slow_db_query_threshold_ms: int = Field(default=500, alias="SLOW_DB_QUERY_THRESHOLD_MS")

    # CORS 配置 - 使用字符串类型避免解析问题
    allowed_origins_str: str = Field(
        default="http://localhost:9527,http://127.0.0.1:9527",
        alias="ALLOWED_ORIGINS",
    )

    # 文件上传配置
    max_upload_size: int = Field(
        default=10 * 1024 * 1024,
        gt=0,
        alias="MAX_UPLOAD_SIZE",
    )  # 10MB
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")

    # 缓存配置
    cache_ttl: int = Field(default=300, alias="CACHE_TTL")  # 5分钟

    # OIDC 单点登录配置；未启用时两个端点仍注册，但统一返回 40000
    oidc_enabled: bool = Field(default=False, alias="OIDC_ENABLED")
    oidc_issuer: str = Field(default="", alias="OIDC_ISSUER")
    oidc_client_id: str = Field(default="", alias="OIDC_CLIENT_ID")
    # 为空表示公开客户端，令牌端点认证方式为 none
    oidc_client_secret: str = Field(default="", alias="OIDC_CLIENT_SECRET")
    oidc_redirect_uri: str = Field(default="", alias="OIDC_REDIRECT_URI")
    oidc_scopes: str = Field(default=DEFAULT_SCOPES, alias="OIDC_SCOPES")
    oidc_auto_provision: bool = Field(default=True, alias="OIDC_AUTO_PROVISION")
    oidc_match_existing_by_email: bool = Field(
        default=False, alias="OIDC_MATCH_EXISTING_BY_EMAIL"
    )
    oidc_allowed_email_domains: str = Field(default="", alias="OIDC_ALLOWED_EMAIL_DOMAINS")

    def model_post_init(self, __context) -> None:
        """模型初始化后的验证"""
        validate_bounds(self.password_min_length, self.password_max_length)
        oidc_errors = self.oidc_config_errors
        if oidc_errors and self.is_production:
            # 生产环境启用单点登录但配置不完整时拒绝启动，而不是只打印警告。
            raise ValueError("OIDC 单点登录配置无效：" + "；".join(oidc_errors))
        # 处理密钥
        if self.secret_key:
            # 使用环境变量设置的密钥
            self._actual_secret_key = self.secret_key
        else:
            # 开发环境自动生成临时密钥
            if self.is_production:
                raise ValueError(
                    "生产环境必须设置 SECRET_KEY 环境变量！\n"
                    "请生成一个安全的密钥：\n"
                    "  python -c \"import secrets; print(secrets.token_urlsafe(64))\"\n"
                    "然后将其设置到环境变量 SECRET_KEY 中。"
                )
            self._actual_secret_key = secrets.token_urlsafe(64)
            warnings.warn(
                "SECRET_KEY 未设置，已自动生成临时密钥。"
                "应用重启后所有 JWT token 将失效。"
                "生产环境请务必设置 SECRET_KEY 环境变量！",
                UserWarning,
                stacklevel=2,
            )

        # 执行安全验证
        security_warnings = SecurityValidator.validate_production_settings(
            app_env=self.app_env,
            debug=self.debug,
            secret_key=self.secret_key,
            default_password=self.default_password,
        )

        # 打印安全警告
        if security_warnings:
            SecurityValidator.print_security_warnings(security_warnings)

    @property
    def oidc_config_errors(self) -> list[str]:
        """启用单点登录时的配置问题；未启用时恒为空。"""
        if not self.oidc_enabled:
            return []
        return settings_errors(
            self.oidc_issuer,
            self.oidc_client_id,
            self.oidc_redirect_uri,
            self.is_production,
        )

    @property
    def allowed_origins(self) -> list[str]:
        """解析允许的来源列表"""
        if not self.allowed_origins_str or self.allowed_origins_str.strip() == "":
            return ["http://localhost:9527", "http://127.0.0.1:9527"]
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]

    @property
    def effective_secret_key(self) -> str:
        """获取实际使用的密钥（可能是环境变量设置的或自动生成的）"""
        if self._actual_secret_key:
            return self._actual_secret_key
        # 如果还没有初始化，返回空字符串（不应该发生）
        return ""

    @property
    def is_sqlite(self) -> bool:
        """是否使用 SQLite 数据库"""
        return self.database_url.startswith("sqlite://")

    @property
    def is_mysql(self) -> bool:
        """是否使用 MySQL 数据库"""
        return self.database_url.startswith(("mysql://", "mysql+aiomysql://"))

    @property
    def tortoise_orm_config(self) -> dict:
        """生成 Tortoise ORM 配置"""
        db_url = self.database_url

        # SQLite 配置
        if self.is_sqlite:
            return {
                "connections": {
                    "default": {
                        "engine": "tortoise.backends.sqlite",
                        "credentials": {
                            "file_path": db_url.replace("sqlite://", ""),
                        },
                    }
                },
                "apps": {
                    "models": {
                        "models": [
                            "app.db.models.oauth",
                            "app.db.models.system",
                        ],
                        "default_connection": "default",
                    }
                },
                "use_tz": False,
                "timezone": "Asia/Shanghai",
            }

        # MySQL 配置
        if db_url.startswith("mysql+aiomysql://"):
            db_url = "mysql://" + db_url[len("mysql+aiomysql://") :]
        connection_config = expand_db_url(db_url)
        connection_config["credentials"].update(
            {
                "minsize": self.database_min_connections,
                "maxsize": self.database_max_connections,
            }
        )

        return {
            "connections": {"default": connection_config},
            "apps": {
                "models": {
                    "models": [
                        "app.db.models.oauth",
                        "app.db.models.system",
                    ],
                    "default_connection": "default",
                }
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai",
        }

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    # BaseSettings 会从环境变量或 .env 注入必填项，mypy 无法从无参构造中推断这一点。
    return Settings()  # type: ignore[call-arg]


# 全局配置实例
settings = get_settings()
