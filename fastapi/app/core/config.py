# -*- coding: utf-8 -*-
"""
应用配置模块

使用 Pydantic Settings 管理应用配置，支持环境变量和 .env 文件。
"""

import os
import secrets
import warnings
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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

    # 数据库配置 - 默认为 SQLite
    database_url: str = Field(
        default="sqlite://./dv_admin.db",
        alias="DATABASE_URL",
    )
    database_min_connections: int = Field(default=1, alias="DATABASE_MIN_CONNECTIONS")
    database_max_connections: int = Field(default=10, alias="DATABASE_MAX_CONNECTIONS")

    # Redis 配置
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")

    # JWT 配置
    # 生产环境必须通过环境变量设置 SECRET_KEY
    # 开发环境如果未设置，将自动生成临时密钥
    _actual_secret_key: Optional[str] = None  # 实际使用的密钥（可能是自动生成的）
    secret_key: Optional[str] = Field(default=None, alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # 密码配置
    password_min_length: int = Field(default=8, alias="PASSWORD_MIN_LENGTH")  # 提高最小长度
    password_max_length: int = Field(default=128, alias="PASSWORD_MAX_LENGTH")  # 提高最大长度
    default_password: str = Field(default="Admin@123456", alias="DEFAULT_PASSWORD")  # 更安全的默认密码

    # 分页配置
    default_page_size: int = Field(default=10, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, alias="MAX_PAGE_SIZE")

    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, alias="LOG_FILE")
    log_rotation: str = Field(default="10 MB", alias="LOG_ROTATION")
    log_retention: str = Field(default="7 days", alias="LOG_RETENTION")

    # 慢查询配置
    slow_query_threshold_ms: int = Field(default=1000, alias="SLOW_QUERY_THRESHOLD_MS")
    very_slow_query_threshold_ms: int = Field(default=5000, alias="VERY_SLOW_QUERY_THRESHOLD_MS")
    slow_db_query_threshold_ms: int = Field(default=500, alias="SLOW_DB_QUERY_THRESHOLD_MS")

    # CORS 配置 - 使用字符串类型避免解析问题
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:9528,http://127.0.0.1:9528",
        alias="ALLOWED_ORIGINS",
    )

    # 文件上传配置
    max_upload_size: int = Field(default=10 * 1024 * 1024, alias="MAX_UPLOAD_SIZE")  # 10MB
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")

    # 缓存配置
    cache_ttl: int = Field(default=300, alias="CACHE_TTL")  # 5分钟

    def model_post_init(self, __context) -> None:
        """模型初始化后的验证"""
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
    def allowed_origins(self) -> List[str]:
        """解析允许的来源列表"""
        if not self.allowed_origins_str or self.allowed_origins_str.strip() == "":
            return ["http://localhost:3000", "http://localhost:5173"]
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
        if db_url.startswith("mysql://"):
            db_url = "mysql+aiomysql://" + db_url[8:]

        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.mysql",
                    "credentials": {
                        "uri": db_url,
                        "minsize": self.database_min_connections,
                        "maxsize": self.database_max_connections,
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
    return Settings()


# 全局配置实例
settings = get_settings()
