# -*- coding: utf-8 -*-
"""
安全验证器模块测试
测试 app/core/security_validator.py 的功能
"""
import pytest
import warnings

from app.core.security_validator import (
    SecurityValidator,
    SecurityValidationError,
)


class TestSecurityValidator:
    """测试安全验证器"""

    def test_weak_passwords_set(self):
        """测试弱密码集合存在"""
        assert "123456" in SecurityValidator.WEAK_PASSWORDS
        assert "admin" in SecurityValidator.WEAK_PASSWORDS
        assert "password" in SecurityValidator.WEAK_PASSWORDS

    def test_min_secret_key_length(self):
        """测试最小密钥长度"""
        assert SecurityValidator.MIN_SECRET_KEY_LENGTH == 32

    def test_recommended_secret_key_length(self):
        """测试推荐密钥长度"""
        assert SecurityValidator.RECOMMENDED_SECRET_KEY_LENGTH == 64


class TestValidateSecretKey:
    """测试密钥验证"""

    def test_production_without_secret_key(self):
        """测试生产环境未设置密钥"""
        with pytest.raises(SecurityValidationError) as exc_info:
            SecurityValidator.validate_secret_key(None, is_production=True)
        assert "生产环境必须设置 SECRET_KEY" in str(exc_info.value)

    def test_production_with_empty_secret_key(self):
        """测试生产环境空密钥"""
        with pytest.raises(SecurityValidationError) as exc_info:
            SecurityValidator.validate_secret_key("", is_production=True)
        assert "生产环境必须设置 SECRET_KEY" in str(exc_info.value)

    def test_development_without_secret_key(self):
        """测试开发环境未设置密钥"""
        warnings_list = SecurityValidator.validate_secret_key(None, is_production=False)
        assert len(warnings_list) == 1
        assert "SECRET_KEY 未设置" in warnings_list[0]

    def test_production_short_secret_key(self):
        """测试生产环境短密钥"""
        short_key = "a" * 16  # 小于 MIN_SECRET_KEY_LENGTH
        with pytest.raises(SecurityValidationError) as exc_info:
            SecurityValidator.validate_secret_key(short_key, is_production=True)
        assert "长度必须至少" in str(exc_info.value)

    def test_development_short_secret_key(self):
        """测试开发环境短密钥"""
        short_key = "a" * 16
        warnings_list = SecurityValidator.validate_secret_key(short_key, is_production=False)
        assert any("长度过短" in w for w in warnings_list)

    def test_recommended_length_warning(self):
        """测试推荐长度警告"""
        key = "a" * 40  # 大于最小长度，小于推荐长度
        warnings_list = SecurityValidator.validate_secret_key(key, is_production=False)
        assert any("推荐使用" in w for w in warnings_list)

    def test_production_weak_key_pattern(self):
        """测试生产环境弱密钥模式"""
        weak_keys = ["test-key", "dev-key", "development-key", "secret", "key"]
        for weak_key in weak_keys:
            with pytest.raises(SecurityValidationError):
                SecurityValidator.validate_secret_key(weak_key, is_production=True)

    def test_development_weak_key_pattern(self):
        """测试开发环境弱密钥模式"""
        warnings_list = SecurityValidator.validate_secret_key("test-key", is_production=False)
        assert any("弱密钥模式" in w for w in warnings_list)

    def test_production_low_entropy_key(self):
        """测试生产环境低熵密钥"""
        low_entropy_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # 32 个相同字符
        with pytest.raises(SecurityValidationError) as exc_info:
            SecurityValidator.validate_secret_key(low_entropy_key, is_production=True)
        assert "字符多样性不足" in str(exc_info.value)

    def test_development_low_entropy_key(self):
        """测试开发环境低熵密钥"""
        low_entropy_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        warnings_list = SecurityValidator.validate_secret_key(low_entropy_key, is_production=False)
        assert any("字符多样性较低" in w for w in warnings_list)

    def test_strong_secret_key(self):
        """测试强密钥"""
        strong_key = "aB1!cD2@eF3#gH4$iJ5%kL6^mN7&oP8*qR9(sT0)uV1-wX2_yZ3="
        warnings_list = SecurityValidator.validate_secret_key(strong_key, is_production=False)
        # 强密钥可能只有推荐长度警告
        assert all("推荐使用" in w for w in warnings_list)


class TestValidatePasswordStrength:
    """测试密码强度验证"""

    def test_weak_password(self):
        """测试弱密码"""
        warnings_list = SecurityValidator.validate_password_strength("123456")
        assert any("常见弱密码" in w for w in warnings_list)

    def test_short_password(self):
        """测试短密码"""
        warnings_list = SecurityValidator.validate_password_strength("abc")
        assert any("长度过短" in w for w in warnings_list)

    def test_low_complexity_password(self):
        """测试低复杂度密码"""
        warnings_list = SecurityValidator.validate_password_strength("abcdefgh")
        assert any("复杂度过低" in w for w in warnings_list)

    def test_strong_password(self):
        """测试强密码"""
        warnings_list = SecurityValidator.validate_password_strength("Admin@123456")
        # 强密码不应该有警告
        assert len(warnings_list) == 0

    def test_medium_complexity_password(self):
        """测试中等复杂度密码"""
        warnings_list = SecurityValidator.validate_password_strength("Admin123")
        # 有大小写和数字，复杂度足够
        assert not any("复杂度过低" in w for w in warnings_list)


class TestValidateProductionSettings:
    """测试生产环境设置验证"""

    def test_production_with_debug(self):
        """测试生产环境启用调试模式"""
        # 使用一个足够复杂的密钥
        complex_key = "aB1!cD2@eF3#gH4$iJ5%kL6^mN7&oP8*qR9(sT0)uV1-wX2_yZ3=aB1!cD2@eF3#"
        warnings_list = SecurityValidator.validate_production_settings(
            app_env="production",
            debug=True,
            secret_key=complex_key,
            default_password="Admin@123456",
        )
        assert any("DEBUG 模式" in w for w in warnings_list)

    def test_production_without_debug(self):
        """测试生产环境不启用调试模式"""
        # 使用一个足够复杂的密钥
        complex_key = "aB1!cD2@eF3#gH4$iJ5%kL6^mN7&oP8*qR9(sT0)uV1-wX2_yZ3=aB1!cD2@eF3#"
        warnings_list = SecurityValidator.validate_production_settings(
            app_env="production",
            debug=False,
            secret_key=complex_key,
            default_password="Admin@123456",
        )
        assert not any("DEBUG 模式" in w for w in warnings_list)

    def test_development_environment(self):
        """测试开发环境"""
        warnings_list = SecurityValidator.validate_production_settings(
            app_env="development",
            debug=True,
            secret_key=None,
            default_password="Admin@123456",
        )
        # 开发环境应该有警告
        assert len(warnings_list) > 0

    def test_production_raises_on_invalid_settings(self):
        """测试生产环境无效设置抛出异常"""
        with pytest.raises(SecurityValidationError):
            SecurityValidator.validate_production_settings(
                app_env="production",
                debug=False,
                secret_key=None,
                default_password="Admin@123456",
            )


class TestGenerateSecureKey:
    """测试生成安全密钥"""

    def test_default_length(self):
        """测试默认长度"""
        key = SecurityValidator.generate_secure_key()
        # token_urlsafe(64) 生成的长度约为 86 字符
        assert len(key) >= 64

    def test_custom_length(self):
        """测试自定义长度"""
        key = SecurityValidator.generate_secure_key(32)
        assert len(key) >= 32

    def test_uniqueness(self):
        """测试唯一性"""
        key1 = SecurityValidator.generate_secure_key()
        key2 = SecurityValidator.generate_secure_key()
        assert key1 != key2


class TestPrintSecurityWarnings:
    """测试打印安全警告"""

    def test_print_warnings(self):
        """测试打印警告"""
        warnings_list = ["WARNING: Test warning 1", "WARNING: Test warning 2"]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SecurityValidator.print_security_warnings(warnings_list)

            assert len(w) == 2
            assert all(issubclass(warning.category, UserWarning) for warning in w)

    def test_print_empty_warnings(self):
        """测试打印空警告列表"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SecurityValidator.print_security_warnings([])
            assert len(w) == 0
