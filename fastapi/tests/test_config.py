"""
配置模块测试
测试 config 模块的功能
"""

import pytest
from pydantic import ValidationError

from app.core.config import settings
from app.main import get_api_docs_config


class TestConfig:
    """测试配置模块"""

    def test_settings_exists(self):
        """测试配置存在"""
        assert settings is not None

    def test_app_name(self):
        """测试应用名称"""
        assert hasattr(settings, "app_name")
        assert settings.app_name is not None

    def test_app_version(self):
        """测试应用版本"""
        assert hasattr(settings, "version")
        assert settings.version is not None

    def test_debug_mode(self):
        """测试调试模式"""
        assert hasattr(settings, "debug")

    def test_database_url(self):
        """测试数据库 URL"""
        assert hasattr(settings, "database_url")
        assert settings.database_url is not None

    def test_secret_key(self):
        """测试密钥"""
        assert hasattr(settings, "secret_key")
        # secret_key 可以为 None（开发环境自动生成）
        # 但 _actual_secret_key 应该总是有值
        assert settings._actual_secret_key is not None

    def test_access_token_expire_minutes(self):
        """测试访问令牌过期时间"""
        assert hasattr(settings, "access_token_expire_minutes")
        assert settings.access_token_expire_minutes > 0

    def test_allowed_origins(self):
        """测试允许的源"""
        assert hasattr(settings, "allowed_origins")
        assert isinstance(settings.allowed_origins, list)

    def test_default_allowed_origins_match_frontend_dev_port(self):
        """默认 CORS 来源应匹配前端开发端口。"""
        from app.core.config import Settings

        default_settings = Settings(
            _env_file=None,
            ALLOWED_ORIGINS="",
            DEFAULT_PASSWORD="ChangeMe!2026",
        )

        assert default_settings.allowed_origins == [
            "http://localhost:9527",
            "http://127.0.0.1:9527",
        ]

    def test_default_password_requires_explicit_configuration(self, monkeypatch):
        """默认密码必须由环境或配置文件显式提供，避免代码内置弱口令。"""
        from app.core.config import Settings

        monkeypatch.delenv("DEFAULT_PASSWORD", raising=False)

        with pytest.raises(ValidationError, match="DEFAULT_PASSWORD"):
            Settings(_env_file=None)

    def test_tortoise_config(self):
        """测试 Tortoise 配置"""
        assert hasattr(settings, "tortoise_orm_config")
        config = settings.tortoise_orm_config
        assert "connections" in config
        assert "apps" in config

    def test_is_sqlite(self):
        """测试 SQLite 检测"""
        assert hasattr(settings, "is_sqlite")
        assert isinstance(settings.is_sqlite, bool)

    def test_is_mysql(self):
        """测试 MySQL 检测"""
        assert hasattr(settings, "is_mysql")
        assert isinstance(settings.is_mysql, bool)

    def test_is_development(self):
        """测试开发环境检测"""
        assert hasattr(settings, "is_development")
        assert isinstance(settings.is_development, bool)

    def test_is_production(self):
        """测试生产环境检测"""
        assert hasattr(settings, "is_production")
        assert isinstance(settings.is_production, bool)

    def test_api_docs_config_enabled_outside_production(self):
        """非生产环境保留 API 文档入口，便于本地联调。"""
        assert get_api_docs_config(is_production=False) == {
            "docs_url": "/api/swagger/",
            "redoc_url": "/api/redoc/",
            "openapi_url": "/api/openapi.json",
        }

    def test_api_docs_config_disabled_in_production(self):
        """生产环境不暴露 Swagger、Redoc 和 OpenAPI JSON。"""
        assert get_api_docs_config(is_production=True) == {
            "docs_url": None,
            "redoc_url": None,
            "openapi_url": None,
        }
